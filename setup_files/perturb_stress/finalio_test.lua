local ridgecrest = {}
ridgecrest.__index = ridgecrest

-- Directory of input files
fractal_dir = '/home/jyun/Tandem/perturb_stress'

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
        local _var1,_var2 = file_name:read('*number','*number')
        if _var1 ~= nil then
            table.insert(var1,_var1)
            table.insert(var2,_var2)
        end
        for line in lines do
            local _var1,_var2 = file_name:read('*number','*number')
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

-------------------- Define your domain: below is the base values for all the parameters
function ridgecrest.new(params)
    local self = setmetatable({}, ridgecrest)
    self.fname_final_stress = params.fname_final_stress
    if #self.fname_final_stress > 0 then
        print(fractal_dir..'/'..self.fname_final_stress)
        self.y_fin,self.fin_tau,self.fin_sn = readtxt_1D(fractal_dir..'/'..self.fname_final_stress,3)
        print(self.y_fin[1])
        print(self.fin_tau[1])
        print(self.fin_sn[1])
    end
    return self
end

function ridgecrest:delta_tau(x, y, t)
    local _del_tau = 0.0
    if #self.fname_final_stress > 0 then
        _del_tau = linear_interpolation(self.y_fin,self.fin_tau,y)
    elseif t < self.init_time then
        -- print('t < init_time')
        _del_tau = 0.0
    else
        _del_tau = -pert_at_y(self.delTs,self.depinfo,self.init_time,t,y,self.dt)
    end
    return _del_tau
end

scen = ridgecrest.new{fname_final_stress='final_stress_pert31_vs340.dat'}
print(scen.delta_tau(0,-7.5,5e+10))