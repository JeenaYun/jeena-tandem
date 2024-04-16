local ridgecrest = {}
ridgecrest.__index = ridgecrest

-- Directory of input files
fractal_dir = '/home/jyun/Tandem/perturb_stress'
stress_dir = '/home/jyun/Tandem/perturb_stress/seissol_outputs'

-- Frictional parameters
ridgecrest.a_b1 = 0.012
ridgecrest.a_b2 = -0.004
ridgecrest.a_b3 = 0.015
ridgecrest.a_b4 = 0.024
ridgecrest.b = 0.019

-- Shear stress [MPa]: negative for right-lateral
ridgecrest.tau1 = -10
ridgecrest.tau2 = -30
ridgecrest.tau3 = -22.5

-- Normal stress [MPa]: positive for compression
ridgecrest.sigma1 = 10
ridgecrest.sigma2 = 50

-- Depths where parameters vary [km]
ridgecrest.Wf = 24
ridgecrest.H = 12.0
ridgecrest.h = 5.0
ridgecrest.H2 = 2.0

-- Others
ridgecrest.rho0 = 2.670        -- Density []
ridgecrest.V0 = 1.0e-6         -- Reference slip rate [m/s]
ridgecrest.f0 = 0.6            -- Reference friction coefficient
ridgecrest.Dc = 0.002          -- Basevalue for Dc
ridgecrest.nu = 0.25           -- Poisson ratio


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
    if init_time > 0 then -- Safety tool
        local ti = math.floor((t-init_time)/dt+0.5) + 1
        if ti <= #delDat then
            y0 = linear_interpolation(dep, delDat[ti],y)
        else
            if ti <= #delDat+10 then
                print('working')
            end
            y0 = linear_interpolation(dep, delDat[#delDat],y)
        end
    end
    return y0
end

-- 5) Function to display the shape of a 2D array
function displayShape(array)
    local rows = #array  -- Get the number of rows
    if rows > 0 then
        local columns = #array[1]  -- Get the number of columns (assuming all rows have the same number of columns)
        print("(" .. rows .. ", " .. columns..")")
    else
        print("Array is empty")
    end
end

-------------------- Define your domain: below is the base values for all the parameters
function ridgecrest.new(params)
    local self = setmetatable({}, ridgecrest)
    self.model_n = params.model_n
    self.strike = params.strike
    self.fcoeff = params.fcoeff
    self.init_time = params.init_time
    self.dt = params.dt
    self.fsn = params.fsn
    self.fab = params.fab
    self.fdc = params.fdc
    self.lowres = params.lowres
    self.Vp = params.Vp

    -- Define filenames
    -- local fname_fractal_sn = fractal_dir..'/fractal_snpre_'..string.format("%02d",self.fsn)
    local fname_fractal_ab = fractal_dir..'/fractal_ab_'..string.format("%02d",self.fab)
    local fname_fractal_dc = fractal_dir..'/fractal_Dc_'..string.format("%02d",self.fdc)

    local fname_init_tau = fractal_dir..'/extract_shearT_121946.dat'
    local fname_init_V = fractal_dir..'/extract_sliprate_121946.dat'
    local fname_init_sn = fractal_dir..'/extract_normalT_121946.dat'

    local fname_Pn = stress_dir..'/ssaf_'..self.model_n..'_Pn_pert_mu'..string.format("%02d",self.fcoeff*10)..'_'..tostring(self.strike)..'.dat'
    local fname_Ts = stress_dir..'/ssaf_'..self.model_n..'_Ts_pert_mu'..string.format("%02d",self.fcoeff*10)..'_'..tostring(self.strike)..'.dat'
    local fname_dep = stress_dir..'/ssaf_'..self.model_n..'_dep_stress_pert_mu'..string.format("%02d",self.fcoeff*10)..'_'..tostring(self.strike)..'.dat'

    self.delPn = readtxt_2D(fname_Pn)
    self.delTs = readtxt_2D(fname_Ts)
    self.depinfo = readtxt_1D(fname_dep,1)

    -- Define your input data
    -- self.y_sn,self.fractal_sn = readtxt_1D(fname_fractal_sn,2)
    self.y_ab,self.fractal_ab = readtxt_1D(fname_fractal_ab,2)
    self.y_dc,self.fractal_dc = readtxt_1D(fname_fractal_dc,2)

    self.y_extract,self.extract_tau = readtxt_1D(fname_init_tau,2)
    self.y_extract,self.extract_V = readtxt_1D(fname_init_V,2)
    self.y_extract,self.extract_sn = readtxt_1D(fname_init_sn,2)

    return self
end

function ridgecrest:boundary(x, y, t)
    if x > 1.0 then
        return self.Vp/2.0 * t
    elseif x < -1.0 then
        return -self.Vp/2.0 * t
    else
        return self.Vp * t
    end
end

function ridgecrest:mu(x, y)
    return 20.0
end

function ridgecrest:eta(x, y)
    return math.sqrt(self:mu(x, y) * self.rho0) / 2.0
end

function ridgecrest:lam(x, y)
    return 2 * self.nu * self:mu(x,y) / (1 - 2 * self.nu)
end

function ridgecrest:Vinit(x, y)
    local extract_Vinit = linear_interpolation(self.y_extract,self.extract_V, y)
    if extract_Vinit == nil then
        extract_Vinit = self.extract_V[#self.extract_V]
    end
    -- file = io.open ('/home/jyun/Tandem/perturb_stress/Vinit_profile','a')
    -- io.output(file)
    -- io.write(y,'\t',extract_Vinit,'\n')
    -- io.close(file)
    return extract_Vinit
end

function ridgecrest:L(x, y)
    local het_L = linear_interpolation(self.y_dc, self.fractal_dc, y)
    if y > 0 then
        het_L = self.Dc
    end
    -- file = io.open ('/home/jyun/Tandem/perturb_stress/dc_profile_sliplaw_lowres','a')
    -- io.output(file)
    -- io.write(y,'\t',het_L*5,'\n')
    -- io.close(file)
    if math.abs(self.lowres-1) > 1e-1 then
        print('low resolution model')
        return_L = het_L * self.lowres
    else
        return_L = het_L
    end
    return return_L
end

function ridgecrest:sn_pre(x, y)
    local extract_sn_pre = linear_interpolation(self.y_extract,self.extract_sn, y)
    if extract_sn_pre == nil then
        extract_sn_pre = self.sigma1
    end
    -- file = io.open ('/home/jyun/Tandem/perturb_stress/sn_pre_profile','a')
    -- io.output(file)
    -- io.write(y,'\t',extract_sn_pre,'\n')
    -- io.close(file)
    return extract_sn_pre
end

function ridgecrest:delta_sn(x, y, t)
    local _del_sn = 0.0
    if self.init_time > 0 and t >= self.init_time then
        _del_sn = pert_at_y(self.delPn,self.depinfo,self.init_time,t,y,self.dt)
    end
    return _del_sn
end

function ridgecrest:tau_pre(x, y)
    local extract_tau_pre = linear_interpolation(self.y_extract,self.extract_tau, y)
    if extract_tau_pre == nil then
        extract_tau_pre = self.extract_tau[#self.extract_tau]
    end
    -- file = io.open ('/home/jyun/Tandem/perturb_stress/tau_pre_profile','a')
    -- io.output(file)
    -- io.write(y,'\t',extract_tau_pre,'\n')
    -- io.close(file)
    return extract_tau_pre
end

function ridgecrest:delta_tau(x, y, t)
    local _del_tau = 0.0
    if self.init_time > 0 and t >= self.init_time then
        _del_tau = -pert_at_y(self.delTs,self.depinfo,self.init_time,t,y,self.dt)
    end
    return _del_tau
end

function ridgecrest:ab(x, y)
    local het_ab = linear_interpolation(self.y_ab,self.fractal_ab, y)
    if y > 0 then
        het_ab = self.a_b1
    end
    return het_ab
end

function ridgecrest:a(x, y)
    local z = -y
    local _ab = self:ab(x,y)
    local _a = _ab + self.b
    -- file = io.open ('/home/jyun/Tandem/perturb_stress/ab_profile_perturb_diffwavelength','a')
    -- io.output(file)
    -- io.write(y,'\t',_a,'\t',self.b,'\n')
    -- io.close(file)
    return _a
end

return ridgecrest