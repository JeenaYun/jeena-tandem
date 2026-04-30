package.path = package.path .. ";/home/jyun/Loading_test/?.lua"
local modules = require "useful_lua_functions"

local side_push = {}
side_push.__index = side_push

side_push.a0 = 0.010
side_push.amax = 0.025
side_push.H = 15.0
side_push.h = 3.0

side_push.rho0 = 2.670
side_push.cs0 = 3.464
side_push.nu0 = 0.25

side_push.b = 0.015
side_push.V0 = 1.0e-6
side_push.Vp = 1.0e-9
-- side_push.f0 = 0.6

side_push.mesh_A = 3/1000
side_push.x0 = -12.91
side_push.z0 = 0.5
side_push.D_lith = 30

-------------------- Define useful functions 
is_near_parabola = modules.is_near_parabola
readtxt_1D_3var = modules.readtxt_1D_3var
interp1d = modules.interp1d

-------------------- Start table
function side_push.new(params)
    local self = setmetatable({}, side_push)
    self.allVS = params.allVS
    self.VMtype = params.VMtype
    self.rightfix = params.rightfix
    self.f0 = params.f0
    self.tau0_mode = params.tau0_mode

    -------------------- Read from a pre-defined file
    -- if self.tau0_mode == 'from_tensor' then
    if self.tau0_mode:find('from_tensor',1,true) then
        self.ver = tonumber(self.tau0_mode:match("from_tensor_(%d+)$"))
        local from_tensor_fname
        -- if self.ver == 1 then
        --     from_tensor_fname = "/home/jyun/Loading_test/from_tensor_60_25_35.txt"
        -- elseif self.ver == 2 then
        --     from_tensor_fname = "/home/jyun/Loading_test/from_tensor_120_0_40.txt"
        -- elseif self.ver == 3 then
        --     from_tensor_fname = "/home/jyun/Loading_test/from_tensor_60_0_20.txt"
        -- elseif self.ver == 4 then
        --     from_tensor_fname = "/home/jyun/Loading_test/from_tensor_72_0_24.txt"
        -- elseif self.ver == 5 then
        --     from_tensor_fname = "/home/jyun/Loading_test/from_tensor_Madden_scen6.txt"
        -- elseif self.ver == 6 then
        --     from_tensor_fname = "/home/jyun/Loading_test/from_tensor_40_0_19.txt"
        -- end
        -- self.y_from_tensor, self.from_tensor_sn, self.from_tensor_tau = readtxt_1D_3var(from_tensor_fname)
        -- self.from_tensor_fname = from_tensor_fname
    end

    -------------------- Define simple 2D VM
    if self.VMtype ~= 'uniform' then
        self.cp1 = 6.8
        self.cp2 = 8.1
        self.cp3 = 7.2
        self.cp4 = 7.5
        
        self.cs1 = 3.84
        self.cs2 = 4.5
        self.cs3 = 4.16
        self.cs4 = 4.17
        
        self.rho1 = 2.7
        self.rho2 = 3.3
        self.rho3 = 2.8
        self.rho4 = 3.3
        if self.VMtype == 'ver2' then
            self.cp5 = 6.8
            self.cs5 = 3.78
            self.rho5 = 2.8
        end
    end
    return self
end

function side_push:boundary(x, y, t)
    local Sh = self.Vp * t
    if x < -300 then
        if self.rightfix then
            return Sh, 0
        else
            return Sh / 2, 0
        end
    elseif x > 300 then
        if self.rightfix then
            return 0, 0
        else
            return -Sh / 2, 0
        end
    end
end

function side_push:compart_ver1(x, y)
    local y_at_curve = -self.mesh_A * (x - self.x0)^2 + self.z0
    local decoup_dep = self.D_lith + 20
    local decoup_x = math.sqrt(-(-decoup_dep - self.z0)/self.mesh_A) + self.x0
    local region = 0
    if y >= y_at_curve and x >= self.x0 then
        if math.abs(y) <= self.D_lith then
            region = 1
        elseif x <= decoup_x then
            region = 3
        else
            region = 2
        end
    else
        region = 2
        if x <= self.x0 then
            if math.abs(y) >= self.D_lith then
                region = 4
            end
        else
            -- Draw a circle of radius = D_lith and see whether it crosses with the curve
            local n_samples = 100
            isoutside = is_near_parabola(x, y, self.mesh_A, -self.x0, self.z0, self.D_lith, n_samples)
            if isoutside then
                region = 4
            end
        end
    end
    
    local cp, cs, rho = 0, 0, 0
    if region == 1 then
        cp = self.cp1
        cs = self.cs1
        rho = self.rho1
    elseif region == 2 then
        cp = self.cp2
        cs = self.cs2
        rho = self.rho2
    elseif region == 3 then
        cp = self.cp3
        cs = self.cs3
        rho = self.rho3
    elseif region == 4 then
        cp = self.cp4
        cs = self.cs4
        rho = self.rho4
    elseif region == 0 then
        print('Something went wrong')
    end
    local mu = cs^2 * rho
    local K = self:get_K(cp, mu, rho)
    local lam = K - (2/3) * mu
    local eta = cs * rho / 2.0
    
    return cp, cs, rho, K, mu, lam, eta, region
end

function side_push:compart_ver2(x, y)
    local y_at_curve = -self.mesh_A * (x - self.x0)^2 + self.z0
    local cp, cs, rho, K, mu, lam, eta, region = self:compart_ver1(x, y)
    if region == 2 then
        local n_samples = 100
        local isoutside = is_near_parabola(x, y, self.mesh_A, -self.x0, self.z0, 5, n_samples)
        if x <= 0 then
            if math.abs(y) <= 5 then
                region = 5
            end
        elseif not isoutside and y <= y_at_curve then
            region = 5
        end
    end
    if region == 5 then
        cp = self.cp5
        cs = self.cs5
        rho = self.rho5
        mu = cs^2 * rho
        K = self:get_K(cp, mu, rho)
        lam = K - (2/3) * mu
        eta = cs * rho / 2.0
        return cp, cs, rho, K, mu, lam, eta, region
    else
        return cp, cs, rho, K, mu, lam, eta, region
    end
end

function side_push:get_cs(x, y)
    if self.VMtype == 'uniform' then
        return self.cs0
    elseif self.VMtype == 'ver1' then
        local xx, local_cs, xx, xx, xx, xx, xx, xx = self:compart_ver1(x, y)
        return local_cs
    elseif self.VMtype == 'ver2' then
        local xx, local_cs, xx, xx, xx, xx, xx, xx = self:compart_ver2(x, y)
        return local_cs
    end
end

function side_push:get_K(cp, mu, rho)
    return cp^2 * rho - (4 / 3) * mu
end

function side_push:mu(x, y)
    if self.VMtype == 'uniform' then
        return self.cs0^2 * self.rho0
    elseif self.VMtype == 'ver1' then
        local xx, xx, xx, xx, local_mu, xx, xx, xx = self:compart_ver1(x, y)
        return local_mu
    elseif self.VMtype == 'ver2' then
        local xx, xx, xx, xx, local_mu, xx, xx, xx = self:compart_ver2(x, y)
        return local_mu
    end
end

function side_push:lam(x, y)
    if self.VMtype == 'uniform' then
        return 2 * self.nu0 * self:mu(x,y) / (1 - 2 * self.nu0)
    elseif self.VMtype == 'ver1' then
        local xx, xx, xx, xx, xx, local_lam, xx, xx = self:compart_ver1(x, y)
        return local_lam
    elseif self.VMtype == 'ver2' then
        local xx, xx, xx, xx, xx, local_lam, xx, xx = self:compart_ver2(x, y)
        return local_lam
    end
end

function side_push:eta(x, y)
    if self.VMtype == 'uniform' then
        return self.cs0 * self.rho0 / 2.0
    elseif self.VMtype == 'ver1' then
        local xx, xx, xx, xx, xx, xx, local_eta, xx = self:compart_ver1(x, y)
        return local_eta
    elseif self.VMtype == 'ver2' then
        local xx, xx, xx, xx, xx, xx, local_eta, xx = self:compart_ver2(x, y)
        return local_eta
    end
end

function side_push:L(x, y)
    return 0.008
end

function side_push:Sinit(x, y)
    return 0.0
end

function side_push:Vinit(x, y)
    if self.tau0_mode:find('from_tensor',1,true) then
        if self.allVS then
            if self.ver >= 5 then
                return 1e-12
            else
                return 1e-10
            end
        else
            if self.ver == 6 then
                return self.Vp
            else
                return 1e-20
            end

        end
    else
        return self.Vp
    end
end

function side_push:a(x, y)
    if self.allVS then
        if math.abs(y) < 1e-1 then
            print('All VS model')
        end
        return self.amax
    else
        local d = math.abs(y)
        if d < self.H then
            return self.a0
        elseif d < self.H + self.h then
            return self.a0 + (self.amax - self.a0) * (d - self.H) / self.h
        else
            return self.amax
        end
    end
end

function side_push:sn_pre(x, y)
    -- positive in compression
    if self.tau0_mode:find('from_tensor',1,true) then
        local from_tensor_sn_at_xy = interp1d(self.y_from_tensor, self.from_tensor_sn, y)
        if self.f0 < 0.6 then
            from_tensor_sn_at_xy = from_tensor_sn_at_xy * (self.f0 / 0.6)
        end
        return from_tensor_sn_at_xy
    else
        return 50.0
    end
end

function side_push:tau_pre(x, y)
    if self.tau0_mode:find('from_tensor',1,true) then
        if math.abs(y) < 1e-1 then
            print(self.from_tensor_fname)
        end
        local from_tensor_tau_at_xy = interp1d(self.y_from_tensor, self.from_tensor_tau, y)
        if self.f0 < 0.6 then
            from_tensor_tau_at_xy = from_tensor_tau_at_xy * (self.f0 / 0.6)
        end
        return from_tensor_tau_at_xy
    else
        local Vi = self:Vinit(x, y)
        local sn = self:sn_pre(x, y)
        local e = math.exp((self.f0 + self.b * math.log(self.V0 / math.abs(Vi))) / self.amax)
        return -(sn * self.amax * math.asinh((Vi / (2.0 * self.V0)) * e) + self:eta(x, y) * Vi)
    end
end

-- function side_push:sn_pre(x, y)
--     -- positive in compression
--     return 50.0
-- end

-- function side_push:tau_pre(x, y)
--     local Vi = self:Vinit(x, y)
--     local sn = self:sn_pre(x, y)
--     local e = math.exp((self.f0 + self.b * math.log(self.V0 / math.abs(Vi))) / self.amax)
--     return -(sn * self.amax * math.asinh((Vi / (2.0 * self.V0)) * e) + self:eta(x, y) * Vi)
-- end

allVS_uniform = side_push.new{allVS=true, VMtype='uniform', rightfix=false, f0=0.6, tau0_mode='typical'}
allVS_uniform_from_tensor_2 = side_push.new{allVS=true, VMtype='uniform', rightfix=false, f0=0.6, tau0_mode='from_tensor_2'}
allVS_uniform_from_tensor_5 = side_push.new{allVS=true, VMtype='uniform', rightfix=false, f0=0.6, tau0_mode='from_tensor_5'}
allVS_uniform_from_tensor_6 = side_push.new{allVS=true, VMtype='uniform', rightfix=false, f0=0.6, tau0_mode='from_tensor_6'}
allVS_uniform_lowf0 = side_push.new{allVS=true, VMtype='uniform', rightfix=false, f0=0.15, tau0_mode='typical'}
allVS_uniform_rightfixed = side_push.new{allVS=true, VMtype='uniform', rightfix=true, f0=0.6, tau0_mode='typical'}
------ 
BP3_uniform = side_push.new{allVS=false, VMtype='uniform', rightfix=false, f0=0.6, tau0_mode='typical'}
BP3_uniform_from_tensor_2 = side_push.new{allVS=false, VMtype='uniform', rightfix=false, f0=0.6, tau0_mode='from_tensor_2'}
BP3_uniform_from_tensor_5 = side_push.new{allVS=false, VMtype='uniform', rightfix=false, f0=0.6, tau0_mode='from_tensor_5'}
BP3_uniform_from_tensor_6 = side_push.new{allVS=false, VMtype='uniform', rightfix=false, f0=0.6, tau0_mode='from_tensor_6'}
BP3_uniform_from_tensor_2_lowf0 = side_push.new{allVS=false, VMtype='uniform', rightfix=false, f0=0.15, tau0_mode='from_tensor_2'}
BP3_uniform_lowf0 = side_push.new{allVS=false, VMtype='uniform', rightfix=false, f0=0.15, tau0_mode='typical'}
BP3_uniform_rightfixed = side_push.new{allVS=false, VMtype='uniform', rightfix=true, f0=0.6, tau0_mode='typical'}
BP3_ver1 = side_push.new{allVS=false, VMtype='ver1', rightfix=false, f0=0.6, tau0_mode='typical'}
BP3_ver2 = side_push.new{allVS=false, VMtype='ver2', rightfix=false, f0=0.6, tau0_mode='typical'}


-- print(BP3_ver2:get_cs(54.62834711, -13.1845097))
-- print(allVS_uniform_from_tensor_5:sn_pre(0,0))
-- print(BP3_uniform_from_tensor:tau_pre(0,0))
-- print(BP3_uniform_from_tensor:sn_pre(0,-10))
-- print(BP3_uniform_from_tensor:tau_pre(0,-10))
-- print(BP3_uniform_from_tensor:sn_pre(0,-15))
-- print(BP3_uniform_from_tensor:tau_pre(0,-15))
-- print(BP3_ver2:mu(0,0))