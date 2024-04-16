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

-- Normal stress [MPa]: positive for compression
BP1.sigma1 = 10
BP1.sigma2 = 50

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
BP1.Dc = 0.002          -- Basevalue for Dc
BP1.nu = 0.25           -- Poisson ratio


-------------------- Define a function that reads in your input fractal profile
function read_fractal(fname)
    local fractal_file = io.open (fname,'r')
    local lines = fractal_file:lines()
    local fault_y = {}
    local var = {}
    local _y,_var = fractal_file:read('*number', '*number')
    if _y ~= nil then
        table.insert(fault_y,_y)
        table.insert(var,_var)
    end

    for line in lines do
        _y,_var = fractal_file:read('*number', '*number')
        if _y ~= nil then
            table.insert(fault_y,_y)
            table.insert(var,_var)
        end
    end
    io.close(fractal_file)
    return fault_y,var
end

-------------------- Define your input data
-- y_sn,fractal_sn = read_fractal('/home/jyun/Tandem/perturb_stress/fractal_snpre_06')
y_ab,fractal_ab = read_fractal('/home/jyun/Tandem/perturb_stress/fractal_ab_02')
y_dc,fractal_dc = read_fractal('/home/jyun/Tandem/perturb_stress/fractal_Dc_02')

y_extract,extract_tau = read_fractal('/home/jyun/Tandem/perturb_stress/extract_shearT_121946.dat')
y_extract,extract_V = read_fractal('/home/jyun/Tandem/perturb_stress/extract_sliprate_121946.dat')
y_extract,extract_sn = read_fractal('/home/jyun/Tandem/perturb_stress/extract_normalT_121946.dat')

-------------------- Define linear interpolation function
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

-------------------- Define your domain: below is the base values for all the parameters
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
    return 20.0
end

function BP1:eta(x, y)
    return math.sqrt(self:mu(x, y) * self.rho0) / 2.0
end

function BP1:L(x, y)
    local het_L = linear_interpolation(y_dc, fractal_dc, y)
    if y > 0 then
        het_L = self.Dc
    end
    -- file = io.open ('/home/jyun/Tandem/perturb_stress/dc_profile_sliplaw_lowres','a')
    -- io.output(file)
    -- io.write(y,'\t',het_L*5,'\n')
    -- io.close(file)
    return het_L*5
    -- return het_L
end

function BP1:lam(x, y)
    return 2 * self.nu * self:mu(x,y) / (1 - 2 * self.nu)
end

function BP1:sn_pre(x, y)
    -- local het_sigma = linear_interpolation(y_sn, fractal_sn, y)
    -- if het_sigma == nil then
    --     het_sigma = self.sigma1
    -- end
    -- return het_sigma
    local extract_sn_pre = linear_interpolation(y_extract,extract_sn, y)
    if extract_sn_pre == nil then
        extract_sn_pre = self.sigma1
    end
    -- file = io.open ('/home/jyun/Tandem/perturb_stress/sn_pre_profile','a')
    -- io.output(file)
    -- io.write(y,'\t',extract_sn_pre,'\n')
    -- io.close(file)
    return extract_sn_pre
end

function BP1:Vinit(x, y)
    -- return 1.0e-9
    local extract_Vinit = linear_interpolation(y_extract,extract_V, y)
    if extract_Vinit == nil then
        extract_Vinit = extract_V[#extract_V]
    end
    -- file = io.open ('/home/jyun/Tandem/perturb_stress/Vinit_profile','a')
    -- io.output(file)
    -- io.write(y,'\t',extract_Vinit,'\n')
    -- io.close(file)
    return extract_Vinit
end

function BP1:ab(x, y)
    local het_ab = linear_interpolation(y_ab, fractal_ab, y)
    if y > 0 then
        het_ab = self.a_b1
    end
    return het_ab
end

function BP1:a(x, y)
    local z = -y
    local _ab = self:ab(x,y)
    local _a = _ab + self.b
    -- file = io.open ('/home/jyun/Tandem/perturb_stress/ab_profile_reference','a')
    -- io.output(file)
    -- io.write(y,'\t',_a,'\t',self.b,'\n')
    -- io.close(file)
    return _a
end

function BP1:tau_pre(x, y)
    -- local z = -y
    -- local _tau1 = self.tau2 + (self.tau2 - self.tau1) * (z - self.H2) / self.H2
    -- local _tau2 = self.tau2 + (self.tau3 - self.tau2) * (z - self.H) / self.h
    -- local _tau = self.tau3
    -- local _sn = self:sn_pre(x,y)

    -- if z < self.H2 then
    --     _tau = _tau1
    -- elseif z < self.H then
    --     _tau = self.tau2
    -- elseif z < self.H + self.h then
    --     _tau = _tau2
    -- end
    -- return _tau
    local extract_tau_pre = linear_interpolation(y_extract,extract_tau, y)
    if extract_tau_pre == nil then
        extract_tau_pre = extract_tau[#extract_tau]
    end
    -- file = io.open ('/home/jyun/Tandem/perturb_stress/tau_pre_profile','a')
    -- io.output(file)
    -- io.write(y,'\t',extract_tau_pre,'\n')
    -- io.close(file)
    return extract_tau_pre
end

bp1 = BP1:new()

bp1_sym = BP1:new()
function bp1_sym:boundary(x, y, t)
    return self.Vp/2.0 * t
end