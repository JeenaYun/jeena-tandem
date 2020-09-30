#ifndef POISSONSCENARIO_20200930_H
#define POISSONSCENARIO_20200930_H

#include "config.h"
#include "localoperator/Poisson.h"

#include "form/Error.h"
#include "geometry/Curvilinear.h"
#include "script/LuaLib.h"
#include "util/Schema.h"
#include "util/SchemaHelper.h"

#include <optional>
#include <string>

namespace tndm {

struct PoissonScenarioConfig {
    std::string lib;
    std::optional<std::string> warp;
    std::optional<std::string> force;
    std::optional<std::string> boundary;
    std::optional<std::string> slip;
    std::optional<std::string> coefficient;
    std::optional<std::string> solution;
    std::optional<std::array<double, DomainDimension>> ref_normal;

    template <typename PathConverter>
    static void setSchema(TableSchema<PoissonScenarioConfig>& schema,
                          PathConverter path_converter) {
        schema.add_value("lib", &PoissonScenarioConfig::lib)
            .converter(path_converter)
            .validator(PathExists());
        schema.add_value("warp", &PoissonScenarioConfig::warp);
        schema.add_value("force", &PoissonScenarioConfig::force);
        schema.add_value("boundary", &PoissonScenarioConfig::boundary);
        schema.add_value("slip", &PoissonScenarioConfig::slip);
        schema.add_value("coefficient", &PoissonScenarioConfig::coefficient);
        schema.add_value("solution", &PoissonScenarioConfig::solution);
        schema.add_array("ref_normal", &PoissonScenarioConfig::ref_normal).of_values();
    }
};

class PoissonScenario {
public:
    using solution_t = std::function<std::array<double, 1>(Vector<double> const&)>;
    using transform_t = Curvilinear<DomainDimension>::transform_t;
    template <std::size_t Q> using functional_t = tmp::Poisson::functional_t<Q>;

    PoissonScenario(PoissonScenarioConfig const& problem) : ref_normal_(problem.ref_normal) {
        lib_.loadFile(problem.lib);

        if (problem.warp) {
            warp_ = lib_.getFunction<DomainDimension, DomainDimension>(*problem.warp);
        }
        if (problem.coefficient) {
            coefficient_ = lib_.getFunction<DomainDimension, 1>(*problem.coefficient);
        }
        auto functional = [](LuaLib& lib, std::optional<std::string> const& opt,
                             std::optional<functional_t<1>>& target) {
            if (opt) {
                target = std::make_optional(lib.getFunction<DomainDimension, 1>(*opt));
            }
        };
        functional(lib_, problem.force, force_);
        functional(lib_, problem.boundary, boundary_);
        functional(lib_, problem.slip, slip_);
        if (problem.solution) {
            auto myF = lib_.getFunction<DomainDimension, 1>(*problem.solution);
            solution_ = [myF](Vector<double> const& v) -> std::array<double, 1> {
                std::array<double, DomainDimension> x;
                for (std::size_t i = 0; i < DomainDimension; ++i) {
                    x[i] = v(i);
                }
                return myF(x);
            };
        }
    }

    auto const& transform() const { return warp_; }
    auto const& force() const { return force_; }
    auto const& boundary() const { return boundary_; }
    auto const& slip() const { return slip_; }
    std::unique_ptr<SolutionInterface> solution() const {
        if (solution_) {
            return std::make_unique<LambdaSolution<decltype(*solution_)>>(*solution_);
        }
        return nullptr;
    }
    auto const& coefficient() const { return coefficient_; }

    auto make_local_operator(Curvilinear<DomainDimension> const& cl) const {
        auto poisson = std::make_unique<tmp::Poisson>(cl, coefficient_);
        if (force_) {
            poisson->set_force(*force_);
        }
        if (boundary_) {
            poisson->set_dirichlet(*boundary_);
        }
        if (slip_ && ref_normal_) {
            poisson->set_slip(*slip_, *ref_normal_);
        }
        return poisson;
    }

private:
    std::optional<std::array<double, DomainDimension>> ref_normal_;
    LuaLib lib_;
    transform_t warp_ = [](std::array<double, DomainDimension> const& v) { return v; };
    functional_t<1> coefficient_ =
        [](std::array<double, DomainDimension> const& v) -> std::array<double, 1> { return {1.0}; };
    std::optional<functional_t<1>> force_ = std::nullopt;
    std::optional<functional_t<1>> boundary_ = std::nullopt;
    std::optional<functional_t<1>> slip_ = std::nullopt;
    std::optional<solution_t> solution_ = std::nullopt;
};

} // namespace tndm

#endif // POISSONSCENARIO_20200930_H
