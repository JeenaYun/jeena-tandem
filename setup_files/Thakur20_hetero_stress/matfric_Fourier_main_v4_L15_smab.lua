local BP1 = {}

-- Frictional parameters
BP1.a_b1 = 0.012
BP1.a_b2 = -0.004
BP1.a_b3 = 0.015
BP1.a_b4 = 0.024
BP1.b = 0.019

-- Shear stress [MPa]: negative for right-lateral
BP1.tau1 = -10
BP1.tau2 = -30
BP1.tau3 = -22.5

-- Depths where parameters vary [km]
BP1.Wf = 24
BP1.H = 12.0
BP1.h = 5.0
BP1.H2 = 2.0

-- Others
BP1.Vp = 1e-9           -- Plate rate [m/s]
BP1.rho0 = 2.670        -- Density []
BP1.V0 = 1.0e-6         -- Reference slip rate [m/s]
BP1.f0 = 0.6            -- Reference friction coefficient

------------ Load your input fractal profile data ------------
snprefile = io.open ('/home/jyun/Tandem/Thakur20_hetero_stress/fractal_snpre_04','r')
-- snprefile = io.open ('fractal_snpre_04','r')
lines = snprefile:lines()
local fault_y = {}
local sigma = {}
_y,_sigma = snprefile:read('*number', '*number')
if _y ~= nil then
    table.insert(fault_y,_y)
    table.insert(sigma,_sigma)
end

for line in lines do
    -- print(line)
    _y,_sigma = snprefile:read('*number', '*number')
    if _y ~= nil then
        table.insert(fault_y,_y)
        table.insert(sigma,_sigma)
    end
end
io.close(snprefile)

------------ Define linear interpolation function ------------
function linear_interpolation(x, y, x0)
    local n = #x
    if x0 < x[1] or x0 > x[n] then
        return nil -- x0 is outside the range of x
    end
    for i = 1, n-1 do
        if x0 >= x[i] and x0 <= x[i+1] then
            local slope = (y[i+1] - y[i]) / (x[i+1] - x[i])
            return y[i] + slope * (x0 - x[i])
        end
    end
end

------------ Define functions for smooth a-b profile ------------
function f_left(dep,grad,intercpt,center,epsilon)
    local fx = -grad/(4*epsilon)*((dep-(center+epsilon))^2)+intercpt
    return fx
end

function f_right(dep,grad,intercpt,center,epsilon)
    local fx = grad/(4*epsilon)*(dep-(center-epsilon))^2+intercpt
    return fx
end

function yl(dep)
    local k = ((BP1.a_b4 - BP1.a_b3)/(BP1.Wf-BP1.H-BP1.h))*(dep - BP1.H) + BP1.a_b2
    return k
end

------------ Tandem configuration start ------------
function BP1:new(o)
    o = o or {}
    setmetatable(o, self)
    self.__index = self
    return o
end

function BP1:boundary(x, y, t)
    if x > 1.0 then
        return self.Vp/2.0 * t
    elseif x < -1.0 then
        return -self.Vp/2.0 * t
    else
        return self.Vp * t
    end
end

function BP1:mu(x, y)
    return 32.0
end

function BP1:eta(x, y)
    return math.sqrt(self:mu(x, y) * self.rho0) / 2.0
end

function BP1:L(x, y)
    return 0.0015
end

function BP1:sn_pre(x, y)
    local het_sigma = linear_interpolation(fault_y, sigma, y)
    if y > 0 then
        het_sigma = 10
    end
    return het_sigma
end

function BP1:Vinit(x, y)
    return 1.0e-9
end

function BP1:ab(x, y)
    local z = -y
    local _ab1 = self.a_b2 + (self.a_b2 - self.a_b1) * (z - self.H2) / self.H2
    local _ab2 = self.a_b2 + (self.a_b3 - self.a_b2) * (z - self.H) / self.h
    local _ab3 = self.a_b3 + (self.a_b4 - self.a_b3) * (z - self.h - self.H) / (self.Wf - self.h - self.H)
    local sharp_ab = nil
    local epsilon = 0.5

    if z < self.H2 then
        sharp_ab = _ab1
    elseif z < self.H then
        sharp_ab = self.a_b2
    elseif z < self.H + self.h then
        sharp_ab = _ab2
    elseif z < self.Wf then
        sharp_ab = _ab3
    else
        sharp_ab = self.a_b4
    end

    if math.abs(z - self.H - self.h) <= epsilon then
        smooth_ab = f_left(z, (self.a_b4 - yl(self.Wf))/self.h, self.a_b4-yl(self.Wf), self.H+self.h, epsilon) + yl(z)
    elseif math.abs(z - self.H) <= epsilon then
        smooth_ab = f_right(z, (self.a_b3-self.a_b2)/self.h, self.a_b2, self.H, epsilon)
    elseif math.abs(z - self.H2) <= epsilon then
        smooth_ab = f_left(z, (self.a_b2-self.a_b1)/self.H2, self.a_b2, self.H2, epsilon)
    else
        smooth_ab = sharp_ab
    end
    return smooth_ab
end

function BP1:a(x, y)
    local z = -y
    local _ab = self:ab(x,y)
    return _ab + self.b
end

function BP1:tau_pre(x, y)
    local z = -y
    local _tau1 = self.tau2 + (self.tau2 - self.tau1) * (z - self.H2) / self.H2
    local _tau2 = self.tau2 + (self.tau3 - self.tau2) * (z - self.H) / self.h

    if z < self.H2 then
        return _tau1
    elseif z < self.H then
        return self.tau2
    elseif z < self.H + self.h then
        return _tau2
    else
        return self.tau3
    end
end

bp1 = BP1:new()

bp1_sym = BP1:new()
function bp1_sym:boundary(x, y, t)
    return self.Vp/2.0 * t
end

-- print('---- In lua ----')

-- num = BP1:ab(0,0)
-- print('0 km (org = 0.012) ->', num)

-- num = BP1:ab(0,-2)
-- print('2 km (org = -0.004) ->', num)

-- num = BP1:ab(0,-12)
-- print('12 km (org = -0.004) ->', num)

-- num = BP1:ab(0,-17)
-- print('17 km (org = 0.015) ->', num)

-- num = BP1:ab(0,-24)
-- print('24 km (org = 0.024) ->', num)