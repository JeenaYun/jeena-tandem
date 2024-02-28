local source_test = {}

-- Frictional parameters
source_test.a0 = 0.010
source_test.amax = 0.025
source_test.b = 0.019

-- Shear stress [MPa]: negative for right-lateral
source_test.tau1 = -10
source_test.tau2 = -30
source_test.tau3 = -22.5

-- Normal stress [MPa]: positive for compression
source_test.sigma1 = 10
source_test.sigma2 = 50

-- Depths where parameters vary [km]
source_test.Wf = 24
source_test.H = 12.0
source_test.h = 5.0
source_test.H2 = 2.0

-- Others
source_test.Vp = 1e-9           -- Plate rate [m/s]
source_test.rho0 = 2.670        -- Density []
source_test.V0 = 1.0e-6         -- Reference slip rate [m/s]
source_test.f0 = 0.6            -- Reference friction coefficient
source_test.Dc = 0.002          -- Basevalue for Dc
source_test.nu = 0.25           -- Poisson ratio

function source_test:new(o)
    o = o or {}
    setmetatable(o, self)
    self.__index = self
    return o
end

function source_test:boundary(x, y, t)
    if x > 1.0 then
        return self.Vp/2.0 * t
    elseif x < -1.0 then
        return -self.Vp/2.0 * t
    else
        return self.Vp * t
    end
end

function source_test:mu(x, y)
    return 32.038120320
end

function source_test:eta(x, y)
    return math.sqrt(self:mu(x, y) * self.rho0) / 2.0
end

function source_test:lam(x, y)
    return 2 * self.nu * self:mu(x,y) / (1 - 2 * self.nu)
end

function source_test:Vinit(x, y)
    return 1.0e-9
end

function source_test:L(x, y)
    return 0.008
end

function source_test:sn_pre(x, y)
    local sn = self.sigma1
    local z = -y
    if z > self.H2 then
        sn = self.sigma2
    end
    return sn
end

function source_test:tau_pre(x, y)
    local z = -y
    local _tau1 = self.tau2 + (self.tau2 - self.tau1) * (z - self.H2) / self.H2
    local _tau2 = self.tau2 + (self.tau3 - self.tau2) * (z - self.H) / self.h
    local _tau = self.tau3

    if z < self.H2 then
        _tau = _tau1
    elseif z < self.H then
        _tau = self.tau2
    elseif z < self.H + self.h then
        _tau = _tau2
    end
    return _tau
end

function source_test:a(x, y)
    local z = -y
    local aa = self.amax
    if z < self.H then
        aa = self.a0
    elseif z < self.H + self.h then
        aa = self.a0 + (self.amax - self.a0) * (z - self.H) / self.h
    end
    return aa
end

base = source_test:new()