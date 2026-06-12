#include "RateAndStateBase.h"

#include "basis/WarpAndBlend.h"

#include <petscsys.h>

#include <algorithm>
#include <memory>

namespace tndm {

auto RateAndStateBase::Space() -> NodalRefElement<DomainDimension - 1u> {
    return NodalRefElement<DomainDimension - 1u>(
        PolynomialDegree, WarpAndBlendFactory<DomainDimension - 1u>(), ALIGNMENT);
}

RateAndStateBase::RateAndStateBase(std::shared_ptr<Curvilinear<DomainDimension>> cl)
    : cl_(std::move(cl)), space_(Space()) {

    for (std::size_t f = 0; f < DomainDimension + 1u; ++f) {
        auto facetParam = cl_->facetParam(f, space_.refNodes());
        geoE_q.emplace_back(cl_->evaluateBasisAt(facetParam));
    }
}

void RateAndStateBase::begin_preparation(std::size_t numFaultFaces) {
    auto nbf = space_.numBasisFunctions();
    fault_.setStorage(std::make_shared<fault_t>(numFaultFaces * nbf), 0u, numFaultFaces, nbf);
}

void RateAndStateBase::prepare(std::size_t faultNo, FacetInfo const& info,
                               LinearAllocator<double>&) {
    auto nbf = space_.numBasisFunctions();
    auto coords =
        Tensor(fault_[faultNo].template get<Coords>().data()->data(), cl_->mapResultInfo(nbf));
    cl_->map(info.up[0], geoE_q[info.localNo[0]], coords);

    // DEBUG: print nodal coordinates to verify basis orientation
    PetscSynchronizedPrintf(PETSC_COMM_WORLD,
                            "NODAL_COORD_CHECK: up[0] GID %lu Nodal Coords[0]: %f, %f, %f\n",
                            (unsigned long)info.g_up[0], coords.data()[0], coords.data()[1],
                            coords.data()[2]);
}

void RateAndStateBase::end_preparation() { PetscSynchronizedFlush(PETSC_COMM_WORLD, PETSC_STDOUT); }

} // namespace tndm
