local source_test = {}
source_test.__index = source_test

-- Directory of input files
stress_dir = '/raid/class239/jeena/Tandem/source_test/seissol_outputs'

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
source_test.alpha = 0.3         -- coefficient for the stress-dependent law


-------------------- Define useful functions 
-- 1) Load from a 1D input file: e.g., fractal parameters
function readtxt_1D(fname,colnum)
    local file_name = io.open (fname,'r')
    local lines = file_name:lines()
    local var1 = {}
    if colnum == 1 then
        _var1 = file_name:read('*number')
        if _var1 ~= nil then
            table.insert(var1,_var1)
        end
        for line in lines do
            _var1 = file_name:read('*number')
            if _var1 ~= nil then
                table.insert(var1,_var1)
            end
        end
        io.close(file_name)
        return var1
    elseif colnum == 2 then
        local var2 = {}
        local _var1,_var2 = file_name:read('*number', '*number')
        if _var1 ~= nil then
            table.insert(var1,_var1)
            table.insert(var2,_var2)
        end
        for line in lines do
            local _var1,_var2 = file_name:read('*number', '*number')
            if _var1 ~= nil then
                table.insert(var1,_var1)
                table.insert(var2,_var2)
            end
        end
        io.close(file_name)
        return var1,var2
    elseif colnum == 3 then
        local var2 = {}
        local var3 = {}
        local _var1,_var2,_var3 = file_name:read('*number','*number','*number')
        if _var1 ~= nil then
            table.insert(var1,_var1)
            table.insert(var2,_var2)
            table.insert(var3,_var3)
        end
        for line in lines do
            local _var1,_var2,_var3 = file_name:read('*number','*number','*number')
            if _var1 ~= nil then
                table.insert(var1,_var1)
                table.insert(var2,_var2)
                table.insert(var3,_var3)
            end
        end
        io.close(file_name)
        return var1,var2,var3
    end
end

-- 2) Load from a 2D input file: e.g., stress perturbation
function readtxt_2D(file_name)
    local array = {}  -- Initialize the 2D array
    -- Open the file in read mode
    local file = io.open(file_name, "r")
    if file then
        for line in file:lines() do
            local inner_array = {}  -- Initialize an inner array to store elements of each line
            -- Split the line by a delimiter (assuming space in this case)
            for element in line:gmatch("%S+") do
                table.insert(inner_array, element)  -- Add elements to the inner array
            end
            table.insert(array, inner_array)  -- Add the inner array to the main 2D array
        end
        file:close()  -- Close the file
    else
        print("File not found or unable to open.")
    end
    return array
end

-- 3) Linear interpolation
function linear_interpolation(x, y, x0)
    local n = #x
    local y0 = nil
    if x0 < x[1] or x0 > x[n] then -- x0 is out of range, take the last value
        if x0 < x[1] then
            y0 = y[1]
        elseif x0 > x[n] then
            y0 = y[n]
        end
    end
    for i = 1, n-1 do
        if x0 >= x[i] and x0 <= x[i+1] then
            local slope = (y[i+1] - y[i]) / (x[i+1] - x[i])
            y0 = y[i] + slope * (x0 - x[i])
        end
    end
    return y0
end

-- 4) Read perturbation file and interpolate value at given 
function pert_at_y(delDat,dep,init_time,t,y,dt)
    local y0 = 0.0
    if init_time > 0 then -- Safety tool 1
        local ti = math.floor((t-init_time)/dt+0.5) + 1
        if ti > 0 then -- Safety tool 2
            if ti <= #delDat then
                y0 = linear_interpolation(dep, delDat[ti],y)
            else
                if ti <= #delDat+10 then
                    print('working')
                end
                y0 = linear_interpolation(dep, delDat[#delDat],y)
            end
        end
    end
    return y0
end

-------------------- Define your domain: below is the base values for all the parameters
function source_test.new(params)
    local self = setmetatable({}, source_test)
    self.model_n = params.model_n
    self.strike = params.strike
    self.fcoeff = params.fcoeff
    self.init_time = params.init_time
    self.dt = params.dt

    -- Define filenames
    local fname_Pn = stress_dir..'/ssaf_'..self.model_n..'_Pn_pert_mu'..string.format("%02d",self.fcoeff*10)..'_'..tostring(self.strike)..'.dat'
    local fname_Ts = stress_dir..'/ssaf_'..self.model_n..'_Ts_pert_mu'..string.format("%02d",self.fcoeff*10)..'_'..tostring(self.strike)..'.dat'
    local fname_dep = stress_dir..'/ssaf_'..self.model_n..'_dep_stress_pert_mu'..string.format("%02d",self.fcoeff*10)..'_'..tostring(self.strike)..'.dat'

    self.delPn = readtxt_2D(fname_Pn)
    self.delTs = readtxt_2D(fname_Ts)
    self.depinfo = readtxt_1D(fname_dep,1)

    return self
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

function source_test:delta_sn(x, y, t)
    local _del_sn = 0.0
    if self.init_time > 0 and t >= self.init_time then
        _del_sn = pert_at_y(self.delPn,self.depinfo,self.init_time,t,y,self.dt)
    end
    return _del_sn
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

function source_test:delta_tau(x, y, t)
    local _del_tau = 0.0
    if self.init_time > 0 and t >= self.init_time then
        _del_tau = -pert_at_y(self.delTs,self.depinfo,self.init_time,t,y,self.dt)
    end
    return _del_tau
end

function source_test:a(x, y)
    local z = -y
    if z < self.H then
        return self.a0
    elseif z < self.H + self.h then
        return self.a0 + (self.amax - self.a0) * (z - self.H) / self.h
    else
        return self.amax
    end
end

function source_test:source(x, y, t)
    local sn_t = -self:delta_sn(x, y, t)
    local sn = self:sn_pre(x, y) + sn_t
    local sn_t_1 = 0.0
    local dsn = 0.0
    if self.init_time > 0 and t > self.init_time then
        sn_t_1 = pert_at_y(self.delPn,self.depinfo,self.init_time,t-self.dt,y,self.dt)
        dsn = sn_t - (-sn_t_1)
    end
    local sn_dot = dsn/self.dt
    local add_term = self.alpha * sn_dot / sn
    return -add_term
end

original_64150 = source_test.new{model_n='vert_slow',strike=340,fcoeff=0.4,dt=0.01,init_time=1.636364397254912186e+10}