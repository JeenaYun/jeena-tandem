// gf-debug.cpp
// Partial GF comparison tool.  Mirrors tandem.cpp structure.
//
// First run (file absent): computes N' sampled columns of the GF operator,
//   writes them to <gf-path> together with a header and a facet-label IS.
//
// Second run (file present): loads the saved matrix, applies row permutation
//   when commsize changed (following the algorithm in gf-debug-app-plan.md),
//   then compares G_mini vs G_loaded and reports absolute + relative errors.
//
// BUG (intentional): the plan assumes column ordering is already correct
//   when reusing cols[] from the file.  This is wrong when commsize changes
//   because global DOF indices depend on the MPI partition; the same DOF
//   number refers to a different physical element in a different-commsize run.
//   Only Rperm is applied here; Cperm and col-remapping are omitted.
//   Use gf-debug-fixed for the correct algorithm.

#include "common/Banner.h"
#include "common/CmdLine.h"
#include "common/MGConfig.h"
#include "common/MeshConfig.h"
#include "common/PetscUtil.h"
#include "common/PetscVector.h"
#include "config.h"
#include "form/SeasQDOperator.h"
#include "localoperator/Elasticity.h"
#include "localoperator/Poisson.h"
#include "parallel/LocalGhostCompositeView.h"
#include "parallel/Scatter.h"
#include "parallel/SparseBlockVector.h"
#include "pc/register.h"
#include "tandem/Context.h"
#include "tandem/ContextBase.h"
#include "tandem/FrictionConfig.h"
#include "tandem/SeasConfig.h"
#include "tandem/SeasScenario.h"
#include "tensor/Tensor.h"

#include "io/GMSHParser.h"
#include "io/GlobalSimplexMeshBuilder.h"
#include "mesh/GenMesh.h"
#include "mesh/GlobalSimplexMesh.h"
#include "mesh/Simplex.h"
#include "parallel/Affinity.h"
#include "util/Schema.h"
#include "util/SchemaHelper.h"

#include <argparse.hpp>
#include <mpi.h>
#include <petscmat.h>
#include <petscsys.h>
#include <petscsystypes.h>
#include <petscvec.h>

#include <algorithm>
#include <cmath>
#include <cstring>
#include <iostream>
#include <memory>
#include <optional>
#include <random>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <vector>

using namespace tndm;

// Expose protected SeasQDOperator::solve / update_traction / traction_
class GFDebugOperator : public SeasQDOperator {
public:
    using SeasQDOperator::SeasQDOperator;
    void probe_column(LocalGhostCompositeView& view) {
        solve(0.0, view);
        update_traction(view);
    }
    PetscVector const& traction_ref() const { return traction_; }
};

// Write fault facet vertex labels to a binary IS file.
// Mirrors write_facet_labels_IS in SeasQDDiscreteGreenOperator.
static void write_facet_IS(LocalSimplexMesh<DomainDimension> const& mesh,
                            AbstractAdapterOperator const& adapter,
                            MPI_Comm comm, std::string const& path) {
    auto const& fault_map = adapter.fault_map();
    PetscInt nfacets = (PetscInt)fault_map.local_size();
    constexpr PetscInt facet_size = (PetscInt)(DomainDimension);
    PetscInt* idx;
    CHKERRTHROW(PetscCalloc1(nfacets * facet_size, &idx));
    auto const& aFacets = mesh.facets();
    for (std::size_t bndNo = 0; bndNo < (std::size_t)nfacets; ++bndNo) {
        auto fctNo = fault_map.fctNo(bndNo);
        auto facets = aFacets[fctNo];
        for (std::size_t d = 0; d < facet_size; ++d)
            idx[bndNo * facet_size + d] = (PetscInt)facets[d];
    }
    IS is;
    CHKERRTHROW(ISCreateGeneral(comm, nfacets * facet_size, idx, PETSC_USE_POINTER, &is));
    PetscViewer v;
    CHKERRTHROW(PetscViewerBinaryOpen(comm, path.c_str(), FILE_MODE_WRITE, &v));
    CHKERRTHROW(ISView(is, v));
    CHKERRTHROW(PetscViewerDestroy(&v));
    CHKERRTHROW(ISDestroy(&is));
    CHKERRTHROW(PetscFree(idx));
}

// Load facet IS written by write_facet_IS, broadcast to all ranks.
// On rank 0: is_rank0 is set and idx points into IS (caller restores with ISRestoreIndices).
// On other ranks: idx is heap-allocated (caller frees with PetscFree).
static void load_broadcast_facet_IS(std::string const& path, MPI_Comm comm,
                                     PetscInt& is_len, PetscInt*& idx, IS& is_rank0) {
    int rank;
    MPI_Comm_rank(comm, &rank);
    is_rank0 = NULL;
    idx      = NULL;
    is_len   = 0;
    if (rank == 0) {
        CHKERRTHROW(ISCreate(PETSC_COMM_SELF, &is_rank0));
        PetscViewer v;
        CHKERRTHROW(PetscViewerBinaryOpen(PETSC_COMM_SELF, path.c_str(), FILE_MODE_READ, &v));
        CHKERRTHROW(ISLoad(is_rank0, v));
        CHKERRTHROW(PetscViewerDestroy(&v));
        CHKERRTHROW(ISGetSize(is_rank0, &is_len));
        CHKERRTHROW(ISGetIndices(is_rank0, (const PetscInt**)&idx));
    }
    MPI_Bcast(&is_len, 1, MPIU_INT, 0, comm);
    if (rank != 0) CHKERRTHROW(PetscCalloc1(is_len, &idx));
    MPI_Bcast(idx, is_len, MPIU_INT, 0, comm);
}

static void free_facet_IS(int rank, PetscInt* idx, IS is_rank0) {
    if (rank == 0) {
        CHKERRTHROW(ISRestoreIndices(is_rank0, (const PetscInt**)&idx));
        CHKERRTHROW(ISDestroy(&is_rank0));
    } else {
        CHKERRTHROW(PetscFree(idx));
    }
}

// Build fault_map_index[local_bndNo] = write-run global element index for the
// same physical fault element as current-run local element bndNo.
// Mirrors create_permutation_redundant_IS in SeasQDDiscreteGreenOperator.
static void build_fault_map_index(LocalSimplexMesh<DomainDimension> const& mesh,
                                   AbstractAdapterOperator const& adapter,
                                   PetscInt const* is_idx, PetscInt is_len,
                                   std::vector<PetscInt>& fault_map_index) {
    constexpr PetscInt facet_size = (PetscInt)(DomainDimension);
    auto const& fault_map = adapter.fault_map();
    PetscInt nfacets = (PetscInt)fault_map.local_size();

    using map_t = std::unordered_map<Simplex<DomainDimension - 1u>, std::size_t,
                                     SimplexHash<DomainDimension - 1u>>;
    map_t fmap(is_len / facet_size);
    for (PetscInt n = 0; n < is_len / facet_size; ++n) {
        Simplex<DomainDimension - 1u> plex{};
        for (PetscInt d = 0; d < facet_size; ++d)
            plex[d] = is_idx[n * facet_size + d];
        fmap[plex] = (std::size_t)n;
    }
    fault_map_index.resize(nfacets);
    auto const& aFacets = mesh.facets();
    for (std::size_t bndNo = 0; bndNo < (std::size_t)nfacets; ++bndNo) {
        auto fctNo = fault_map.fctNo(bndNo);
        auto it    = fmap.find(aFacets[fctNo]);
        if (it == fmap.end())
            throw std::runtime_error("[gf-debug] facet not found in write-run IS");
        fault_map_index[bndNo] = (PetscInt)it->second;
    }
}

// Apply row permutation to G_loaded: G_loaded = Rperm * G_loaded.
// Rperm[cur_elem*br+d, write_elem*br+d] = 1, mapping write-run rows to current-run rows.
//
// BUG: column ordering is NOT fixed here.  The plan claims "column order is
// already correct because cols[] came from the file", but this is wrong when
// commsize changes: DOF index cols[k] refers to a different physical element
// in each run.  The missing fix is to also remap cols[] and recompute G_mini.
static void apply_row_permutation(LocalSimplexMesh<DomainDimension> const& mesh,
                                   AbstractAdapterOperator const& adapter,
                                   Mat& G_loaded, MPI_Comm comm,
                                   std::string const& facets_path) {
    int rank;
    MPI_Comm_rank(comm, &rank);

    PetscInt is_len = 0;
    PetscInt* idx   = NULL;
    IS is_rank0;
    load_broadcast_facet_IS(facets_path, comm, is_len, idx, is_rank0);

    PetscInt nfacets = (PetscInt)adapter.fault_map().local_size();
    PetscInt nfacets_global = 0;
    MPI_Allreduce(&nfacets, &nfacets_global, 1, MPIU_INT, MPI_SUM, comm);

    std::vector<PetscInt> fault_map_index;
    build_fault_map_index(mesh, adapter, idx, is_len, fault_map_index);
    free_facet_IS(rank, idx, is_rank0);

    PetscInt mb_offset = 0;
    MPI_Scan(&nfacets, &mb_offset, 1, MPIU_INT, MPI_SUM, comm);
    mb_offset -= nfacets;

    PetscInt M, N, m, n;
    CHKERRTHROW(MatGetSize(G_loaded, &M, &N));
    CHKERRTHROW(MatGetLocalSize(G_loaded, &m, &n));
    PetscInt br = M / nfacets_global;

    Mat Rperm;
    CHKERRTHROW(MatCreate(comm, &Rperm));
    CHKERRTHROW(MatSetSizes(Rperm, m, m, M, M));
    CHKERRTHROW(MatSetType(Rperm, MATAIJ));
    CHKERRTHROW(MatSeqAIJSetPreallocation(Rperm, br, NULL));
    CHKERRTHROW(MatMPIAIJSetPreallocation(Rperm, br, NULL, br, NULL));
    for (PetscInt bndNo = 0; bndNo < nfacets; ++bndNo) {
        PetscInt from = mb_offset + bndNo;
        PetscInt to   = fault_map_index[bndNo];
        for (PetscInt d = 0; d < br; ++d)
            CHKERRTHROW(MatSetValue(Rperm, br * from + d, br * to + d, 1.0, INSERT_VALUES));
    }
    CHKERRTHROW(MatAssemblyBegin(Rperm, MAT_FINAL_ASSEMBLY));
    CHKERRTHROW(MatAssemblyEnd(Rperm, MAT_FINAL_ASSEMBLY));

    Mat G_new;
    CHKERRTHROW(MatMatMult(Rperm, G_loaded, MAT_INITIAL_MATRIX, PETSC_DEFAULT, &G_new));
    CHKERRTHROW(MatDestroy(&Rperm));
    CHKERRTHROW(MatDestroy(&G_loaded));
    G_loaded = G_new;
}

static void run_gf_debug(LocalSimplexMesh<DomainDimension> const& mesh, Config const& cfg,
                          PetscInt N_prime, std::string const& gf_path, int seed,
                          bool report_cols) {
    MPI_Comm comm = PETSC_COMM_WORLD;
    int rank, commsize;
    MPI_Comm_rank(comm, &rank);
    MPI_Comm_size(comm, &commsize);

    // Build context and operator (same pattern as tandem.cpp / solveSEASProblem)
    std::unique_ptr<seas::ContextBase> ctx;
    switch (cfg.type) {
    case LocalOpType::Elasticity:
        ctx = std::make_unique<seas::Context<Elasticity>>(
            mesh, std::make_unique<SeasScenario<Elasticity>>(cfg.lib, cfg.scenario),
            std::make_unique<DieterichRuinaAgeingScenario>(cfg.lib, cfg.scenario),
            cfg.up, cfg.ref_normal);
        break;
    case LocalOpType::Poisson:
        ctx = std::make_unique<seas::Context<Poisson>>(
            mesh, std::make_unique<SeasScenario<Poisson>>(cfg.lib, cfg.scenario),
            std::make_unique<DieterichRuinaAgeingScenario>(cfg.lib, cfg.scenario),
            cfg.up, cfg.ref_normal);
        break;
    default:
        throw std::runtime_error("gf-debug: unsupported operator type (Elasticity or Poisson only)");
    }

    GFDebugOperator seasop(std::move(ctx->dg()), std::move(ctx->adapter()),
                            std::move(ctx->friction()), cfg.matrix_free,
                            MGConfig(cfg.mg_coarse_level, cfg.mg_strategy));
    ctx->setup_seasop(seasop);
    seasop.warmup();

    // Problem dimensions (mirrors compute_discrete_greens_function)
    auto slip_bs  = static_cast<PetscInt>(seasop.friction().slip_block_size());
    auto trac_bs  = static_cast<PetscInt>(seasop.adapter().traction_block_size());
    PetscInt num_local = static_cast<PetscInt>(seasop.adapter().num_local_elements());
    PetscInt m = num_local * trac_bs;

    PetscVector S_full(slip_bs, num_local, comm);
    PetscInt N_total, n_local;
    CHKERRTHROW(VecGetSize(S_full.vec(), &N_total));
    CHKERRTHROW(VecGetLocalSize(S_full.vec(), &n_local));

    PetscInt nb_offset = 0;
    MPI_Scan(&n_local, &nb_offset, 1, MPIU_INT, MPI_SUM, comm);
    nb_offset -= n_local;

    PetscInt mb_offset = 0;
    MPI_Scan(&num_local, &mb_offset, 1, MPIU_INT, MPI_SUM, comm);
    mb_offset -= num_local;

    auto scatter = Scatter(seasop.adapter().fault_map().scatter_plan());
    auto ghost   = scatter.template recv_prototype<double>(slip_bs, ALIGNMENT);

    // Resolve column indices: load from file (second run) or generate fresh (first run)
    PetscBool file_found = PETSC_FALSE;
    CHKERRTHROW(PetscTestFile(gf_path.c_str(), 'r', &file_found));

    std::vector<PetscInt> cols;
    PetscInt N_prime_actual = N_prime;
    PetscInt commsize_ckpt  = static_cast<PetscInt>(commsize);

    if (file_found) {
        PetscViewer vhdr;
        CHKERRTHROW(PetscViewerBinaryOpen(comm, gf_path.c_str(), FILE_MODE_READ, &vhdr));
        CHKERRTHROW(PetscViewerBinaryRead(vhdr, &commsize_ckpt,   1,              NULL, PETSC_INT));
        CHKERRTHROW(PetscViewerBinaryRead(vhdr, &N_prime_actual,  1,              NULL, PETSC_INT));
        cols.resize(N_prime_actual);
        CHKERRTHROW(PetscViewerBinaryRead(vhdr, cols.data(), N_prime_actual, NULL, PETSC_INT));
        CHKERRTHROW(PetscViewerDestroy(&vhdr));
    } else {
        cols.resize(N_prime);
        if (rank == 0) {
            std::mt19937 rng(seed);
            std::uniform_int_distribution<PetscInt> dist(0, N_total - 1);
            for (auto& c : cols) c = dist(rng);
        }
        MPI_Bcast(cols.data(), N_prime, MPIU_INT, 0, comm);
    }

    if (rank == 0 && report_cols) {
        std::cout << "[gf-debug] Selected DOF indices:";
        for (PetscInt k = 0; k < N_prime_actual; ++k) std::cout << " " << cols[k];
        std::cout << "\n";
    }

    // Compute G_mini in memory (mirrors compute_discrete_greens_function column loop)
    Mat G_mini;
    CHKERRTHROW(MatCreateDense(comm, m, PETSC_DECIDE, PETSC_DECIDE, N_prime_actual,
                                nullptr, &G_mini));
    CHKERRTHROW(MatSetBlockSizes(G_mini, trac_bs, 1));

    for (PetscInt k = 0; k < N_prime_actual; ++k) {
        PetscInt j = cols[k];
        CHKERRTHROW(VecZeroEntries(S_full.vec()));
        if (j >= nb_offset && j < nb_offset + n_local) {
            PetscScalar one = 1.0;
            CHKERRTHROW(VecSetValue(S_full.vec(), j, one, INSERT_VALUES));
        }
        S_full.begin_assembly();
        S_full.end_assembly();
        scatter.begin_scatter(S_full, ghost);
        scatter.wait_scatter();
        {
            auto S_view = LocalGhostCompositeView(S_full, ghost);
            seasop.probe_column(S_view);
        }
        auto th = seasop.traction_ref().begin_access_readonly();
        for (PetscInt faultNo = 0; faultNo < num_local; ++faultNo) {
            PetscInt g_m = mb_offset + faultNo;
            auto blk = th.subtensor(slice{}, faultNo);
            CHKERRTHROW(MatSetValuesBlocked(G_mini, 1, &g_m, 1, &k, blk.data(), INSERT_VALUES));
        }
        seasop.traction_ref().end_access_readonly(th);
        if (rank == 0)
            std::cout << "[gf-debug] column " << (k + 1) << "/" << N_prime_actual
                      << "  DOF j=" << j << "\n";
    }
    CHKERRTHROW(MatAssemblyBegin(G_mini, MAT_FINAL_ASSEMBLY));
    CHKERRTHROW(MatAssemblyEnd(G_mini, MAT_FINAL_ASSEMBLY));

    // First run: write matrix + facet IS, then exit
    if (!file_found) {
        PetscViewer vw;
        CHKERRTHROW(PetscViewerBinaryOpen(comm, gf_path.c_str(), FILE_MODE_WRITE, &vw));
        PetscInt cs = static_cast<PetscInt>(commsize);
        CHKERRTHROW(PetscViewerBinaryWrite(vw, &cs,              1,              PETSC_INT));
        CHKERRTHROW(PetscViewerBinaryWrite(vw, &N_prime_actual,  1,              PETSC_INT));
        CHKERRTHROW(PetscViewerBinaryWrite(vw, cols.data(), N_prime_actual,      PETSC_INT));
        CHKERRTHROW(MatView(G_mini, vw));
        CHKERRTHROW(PetscViewerDestroy(&vw));
        write_facet_IS(mesh, seasop.adapter(), comm, gf_path + ".facets");
        if (rank == 0)
            std::cout << "\n=== gf-debug: first run ===\n"
                      << "Wrote N'=" << N_prime_actual << " columns (N=" << N_total
                      << ") to " << gf_path << "\n"
                      << "Run again with the same --gf-path to compare.\n";
        CHKERRTHROW(MatDestroy(&G_mini));
        return;
    }

    // Second run: load G_loaded
    Mat G_loaded;
    CHKERRTHROW(MatCreateDense(comm, m, PETSC_DECIDE, PETSC_DECIDE, N_prime_actual,
                                nullptr, &G_loaded));
    {
        PetscViewer vr;
        CHKERRTHROW(PetscViewerBinaryOpen(comm, gf_path.c_str(), FILE_MODE_READ, &vr));
        PetscInt skip;
        CHKERRTHROW(PetscViewerBinaryRead(vr, &skip, 1, NULL, PETSC_INT));
        CHKERRTHROW(PetscViewerBinaryRead(vr, &skip, 1, NULL, PETSC_INT));
        std::vector<PetscInt> skip_cols(N_prime_actual);
        CHKERRTHROW(PetscViewerBinaryRead(vr, skip_cols.data(), N_prime_actual, NULL, PETSC_INT));
        CHKERRTHROW(MatLoad(G_loaded, vr));
        CHKERRTHROW(PetscViewerDestroy(&vr));
    }

    bool repartition = (static_cast<PetscInt>(commsize) != commsize_ckpt);
    if (rank == 0)
        std::cout << "[gf-debug] commsize_ckpt=" << commsize_ckpt
                  << "  current=" << commsize
                  << "  repartition=" << (repartition ? "YES" : "NO") << "\n";

    // Apply row permutation only when commsize changed.
    // The plan (gf-debug-app-plan.md) claims column order is already correct
    // because cols[] came from the file.  This is the bug: when commsize changes,
    // a given global DOF index refers to a different physical element, so G_mini
    // and G_loaded are comparing responses to different physical elements.
    if (repartition)
        apply_row_permutation(mesh, seasop.adapter(), G_loaded, comm, gf_path + ".facets");

    // Random test vector (same on all ranks)
    std::vector<double> v_rand(N_prime_actual);
    if (rank == 0) {
        std::mt19937 rng(seed + 1);
        std::uniform_real_distribution<double> dist(-1.0, 1.0);
        for (auto& x : v_rand) x = dist(rng);
    }
    MPI_Bcast(v_rand.data(), N_prime_actual, MPI_DOUBLE, 0, comm);

    // Three traction estimates
    Vec v_petsc, w_mem_vec, w_loaded_vec, w_full_vec;
    CHKERRTHROW(MatCreateVecs(G_mini, &v_petsc, &w_mem_vec));
    CHKERRTHROW(VecDuplicate(w_mem_vec, &w_loaded_vec));
    CHKERRTHROW(VecDuplicate(w_mem_vec, &w_full_vec));
    {
        PetscInt lo, hi;
        CHKERRTHROW(VecGetOwnershipRange(v_petsc, &lo, &hi));
        for (PetscInt k = lo; k < hi; ++k)
            CHKERRTHROW(VecSetValue(v_petsc, k, v_rand[k], INSERT_VALUES));
        CHKERRTHROW(VecAssemblyBegin(v_petsc));
        CHKERRTHROW(VecAssemblyEnd(v_petsc));
    }
    CHKERRTHROW(MatMult(G_mini,   v_petsc, w_mem_vec));
    CHKERRTHROW(MatMult(G_loaded, v_petsc, w_loaded_vec));
    // w_full: direct solve for the same slip input as G_mini
    {
        CHKERRTHROW(VecZeroEntries(S_full.vec()));
        for (PetscInt k = 0; k < N_prime_actual; ++k) {
            PetscInt j = cols[k];
            if (j >= nb_offset && j < nb_offset + n_local)
                CHKERRTHROW(VecSetValue(S_full.vec(), j, v_rand[k], ADD_VALUES));
        }
        S_full.begin_assembly();
        S_full.end_assembly();
        scatter.begin_scatter(S_full, ghost);
        scatter.wait_scatter();
        {
            auto S_view = LocalGhostCompositeView(S_full, ghost);
            seasop.probe_column(S_view);
        }
        CHKERRTHROW(VecCopy(seasop.traction_ref().vec(), w_full_vec));
    }

    // ── Errors ──────────────────────────────────────────────────────────────

    // Frobenius norms of G_mini and (G_mini - G_loaded)
    double norm_G_mini_F, norm_diff_F;
    CHKERRTHROW(MatNorm(G_mini, NORM_FROBENIUS, &norm_G_mini_F));
    {
        Mat G_diff;
        CHKERRTHROW(MatDuplicate(G_mini, MAT_COPY_VALUES, &G_diff));
        CHKERRTHROW(MatAXPY(G_diff, -1.0, G_loaded, DIFFERENT_NONZERO_PATTERN));
        CHKERRTHROW(MatNorm(G_diff, NORM_FROBENIUS, &norm_diff_F));
        CHKERRTHROW(MatDestroy(&G_diff));
    }
    double frob_rel = (norm_G_mini_F > 0.0) ? norm_diff_F / norm_G_mini_F : norm_diff_F;

    // Per-column 2-norms
    std::vector<double> col_abs(N_prime_actual), col_rel(N_prime_actual);
    {
        Vec e_k, col_m, col_l;
        CHKERRTHROW(MatCreateVecs(G_mini, &e_k, &col_m));
        CHKERRTHROW(VecDuplicate(col_m, &col_l));
        for (PetscInt k = 0; k < N_prime_actual; ++k) {
            CHKERRTHROW(VecZeroEntries(e_k));
            CHKERRTHROW(VecSetValue(e_k, k, 1.0, INSERT_VALUES));
            CHKERRTHROW(VecAssemblyBegin(e_k));
            CHKERRTHROW(VecAssemblyEnd(e_k));
            CHKERRTHROW(MatMult(G_mini,   e_k, col_m));
            CHKERRTHROW(MatMult(G_loaded, e_k, col_l));
            double nm, nd;
            CHKERRTHROW(VecNorm(col_m, NORM_2, &nm));
            CHKERRTHROW(VecAXPY(col_l, -1.0, col_m));
            CHKERRTHROW(VecNorm(col_l, NORM_2, &nd));
            col_abs[k] = nd;
            col_rel[k] = (nm > 0.0) ? nd / nm : nd;
        }
        CHKERRTHROW(VecDestroy(&e_k));
        CHKERRTHROW(VecDestroy(&col_m));
        CHKERRTHROW(VecDestroy(&col_l));
    }

    // Traction vector absolute and relative errors
    double norm_full, norm_mem;
    double abs_mem_full, abs_load_full, abs_mem_load;
    CHKERRTHROW(VecNorm(w_full_vec, NORM_2, &norm_full));
    CHKERRTHROW(VecNorm(w_mem_vec,  NORM_2, &norm_mem));
    {
        Vec tmp;
        CHKERRTHROW(VecDuplicate(w_full_vec, &tmp));
        CHKERRTHROW(VecCopy(w_mem_vec,    tmp));
        CHKERRTHROW(VecAXPY(tmp, -1.0, w_full_vec));
        CHKERRTHROW(VecNorm(tmp, NORM_2, &abs_mem_full));
        CHKERRTHROW(VecCopy(w_loaded_vec, tmp));
        CHKERRTHROW(VecAXPY(tmp, -1.0, w_full_vec));
        CHKERRTHROW(VecNorm(tmp, NORM_2, &abs_load_full));
        CHKERRTHROW(VecCopy(w_mem_vec,    tmp));
        CHKERRTHROW(VecAXPY(tmp, -1.0, w_loaded_vec));
        CHKERRTHROW(VecNorm(tmp, NORM_2, &abs_mem_load));
        CHKERRTHROW(VecDestroy(&tmp));
    }
    double rel_mem_full  = (norm_full > 0.0) ? abs_mem_full  / norm_full : abs_mem_full;
    double rel_load_full = (norm_full > 0.0) ? abs_load_full / norm_full : abs_load_full;
    double rel_mem_load  = (norm_mem  > 0.0) ? abs_mem_load  / norm_mem  : abs_mem_load;

    // ── Report ───────────────────────────────────────────────────────────────
    if (rank == 0) {
        auto max_rel_it = std::max_element(col_rel.begin(), col_rel.end());
        auto min_rel_it = std::min_element(col_rel.begin(), col_rel.end());
        auto max_abs_it = std::max_element(col_abs.begin(), col_abs.end());
        auto min_abs_it = std::min_element(col_abs.begin(), col_abs.end());
        double mean_rel = 0.0, mean_abs = 0.0;
        for (PetscInt k = 0; k < N_prime_actual; ++k) {
            mean_rel += col_rel[k];
            mean_abs += col_abs[k];
        }
        mean_rel /= N_prime_actual;
        mean_abs /= N_prime_actual;
        int k_max_rel = (int)(max_rel_it - col_rel.begin());
        int k_min_rel = (int)(min_rel_it - col_rel.begin());
        int k_max_abs = (int)(max_abs_it - col_abs.begin());
        int k_min_abs = (int)(min_abs_it - col_abs.begin());

        std::cout << "\n=== gf-debug report (BUGGY: row perm only) ===\n";
        std::cout << "N  (total fault DOFs) : " << N_total         << "\n";
        std::cout << "N' (sampled columns)  : " << N_prime_actual  << "\n";
        std::cout << "Seed                  : " << seed            << "\n";
        std::cout << "||G_mini||_F          : " << norm_G_mini_F   << "\n";
        std::cout << "||w_full||            : " << norm_full       << "\n";
        std::cout << "||w_mem ||            : " << norm_mem        << "\n";

        std::cout << "\n--- Matrix comparison (G_mini vs G_loaded";
        if (repartition) std::cout << ", Rperm applied to rows only";
        std::cout << ") ---\n";
        std::cout << "||G_mini - G_loaded||_F          = " << norm_diff_F
                  << "  (absolute)\n";
        std::cout << "||G_mini - G_loaded||_F/||G||_F  = " << frob_rel
                  << "  (relative)\n";
        std::cout << "Max col absolute err = " << *max_abs_it
                  << "  (k=" << k_max_abs << ", DOF j=" << cols[k_max_abs] << ")\n";
        std::cout << "Min col absolute err = " << *min_abs_it
                  << "  (k=" << k_min_abs << ", DOF j=" << cols[k_min_abs] << ")\n";
        std::cout << "Mean col absolute err = " << mean_abs << "\n";
        std::cout << "Max col relative err = " << *max_rel_it
                  << "  (k=" << k_max_rel << ", DOF j=" << cols[k_max_rel] << ")\n";
        std::cout << "Min col relative err = " << *min_rel_it
                  << "  (k=" << k_min_rel << ", DOF j=" << cols[k_min_rel] << ")\n";
        std::cout << "Mean col relative err = " << mean_rel << "\n";

        std::cout << "\n--- Traction vector comparison ---\n";
        std::cout << "||w_mem  - w_full || = " << abs_mem_full
                  << "  /  " << rel_mem_full
                  << "  (abs / rel)  sanity: in-memory GF vs direct solver\n";
        std::cout << "||w_load - w_full || = " << abs_load_full
                  << "  /  " << rel_load_full
                  << "  (abs / rel)  loaded GF vs direct solver\n";
        std::cout << "||w_mem  - w_load || = " << abs_mem_load
                  << "  /  " << rel_mem_load
                  << "  (abs / rel)  in-memory GF vs loaded GF\n";

        std::cout << "\n--- Per-column diagnostics ---\n";
        std::cout << "k\tDOF_j\t||diff||_abs\t||diff||/||col||_rel\n";
        for (PetscInt k = 0; k < N_prime_actual; ++k)
            std::cout << k << "\t" << cols[k] << "\t"
                      << col_abs[k] << "\t" << col_rel[k] << "\n";
        std::cout << "=======================\n";
    }

    CHKERRTHROW(MatDestroy(&G_mini));
    CHKERRTHROW(MatDestroy(&G_loaded));
    CHKERRTHROW(VecDestroy(&v_petsc));
    CHKERRTHROW(VecDestroy(&w_mem_vec));
    CHKERRTHROW(VecDestroy(&w_loaded_vec));
    CHKERRTHROW(VecDestroy(&w_full_vec));
}

int main(int argc, char** argv) {
    auto affinity = Affinity();

    int pArgc = 0;
    char** pArgv = nullptr;
    for (int i = 0; i < argc; ++i) {
        if (strcmp(argv[i], "--petsc") == 0) {
            pArgc = argc - i;
            pArgv = argv + i;
            argc  = i;
            break;
        }
    }

    argparse::ArgumentParser program("gf-debug");
    program.add_argument("--petsc").help("PETSc options, must be passed last!");
    program.add_argument("config").help("Configuration file (.toml)");
    program.add_argument("--n-cols")
        .help("Number of GF columns to sample (10-100 is typical)")
        .required()
        .scan<'i', int>();
    program.add_argument("--gf-path")
        .help("File for the partial GF (written on first run, read on second run)")
        .required();
    program.add_argument("--seed")
        .help("RNG seed for column selection")
        .default_value(42)
        .scan<'i', int>();
    program.add_argument("--report-cols")
        .help("Print the selected DOF indices")
        .default_value(false)
        .implicit_value(true);

    auto makePathRelativeToConfig =
        MakePathRelativeToOtherPath([&program]() { return program.get("config"); });
    TableSchema<Config> schema;
    setConfigSchema(schema, makePathRelativeToConfig);

    std::optional<Config> cfg = readFromConfigurationFileAndCmdLine(schema, program, argc, argv);
    if (!cfg) return -1;

    int         n_cols      = program.get<int>("--n-cols");
    std::string gf_path     = program.get("--gf-path");
    int         seed        = program.get<int>("--seed");
    bool        report_cols = program.get<bool>("--report-cols");

    CHKERRQ(PetscInitialize(&pArgc, &pArgv, nullptr, nullptr));
    CHKERRQ(register_PCs());
    CHKERRQ(register_KSPs());

    int rank, procs;
    MPI_Comm_rank(PETSC_COMM_WORLD, &rank);
    MPI_Comm_size(PETSC_COMM_WORLD, &procs);

    if (rank == 0) Banner::standard(std::cout, affinity);

    std::unique_ptr<GlobalSimplexMesh<DomainDimension>> globalMesh;
    if (cfg->mesh_file) {
        bool ok = false;
        GlobalSimplexMeshBuilder<DomainDimension> builder;
        if (rank == 0) {
            GMSHParser parser(&builder);
            ok = parser.parseFile(*cfg->mesh_file);
            if (!ok)
                std::cerr << *cfg->mesh_file << "\n" << parser.getErrorMessage();
        }
        MPI_Bcast(&ok, 1, MPI_CXX_BOOL, 0, PETSC_COMM_WORLD);
        if (ok) globalMesh = builder.create(PETSC_COMM_WORLD);
        if (procs > 1) globalMesh->repartitionByHash();
    } else if (cfg->generate_mesh && cfg->resolution) {
        auto meshGen = cfg->generate_mesh->create(*cfg->resolution, PETSC_COMM_WORLD);
        globalMesh   = meshGen.uniformMesh();
    }
    if (!globalMesh) {
        std::cerr << "Must provide a valid mesh file or mesh generation config.\n";
        PetscFinalize();
        return -1;
    }
    globalMesh->repartition();
    auto mesh = globalMesh->getLocalMesh(1);

    run_gf_debug(*mesh, *cfg, static_cast<PetscInt>(n_cols), gf_path, seed, report_cols);

    return PetscFinalize();
}
