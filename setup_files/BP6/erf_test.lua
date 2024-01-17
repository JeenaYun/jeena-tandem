function erf(x)
    -- constants
    local a1 =  0.254829592
    local a2 = -0.284496736
    local a3 =  1.421413741
    local a4 = -1.453152027
    local a5 =  1.061405429
    local p  =  0.3275911

    -- Save the sign of x
    local sign = 1
    if x < 0 then
        sign = -1
    end
    local x = math.abs(x)

    -- A&S formula 7.1.26
    local c = 1.0/(1.0 + p*x)
    local val = 1.0 - (((((a5*c + a4)*c) + a3)*c + a2)*c + a1)*c*math.exp(-x*x)

    return sign*val
end

function getG(y, t, alpha)
    local z = y*1e3
    local Gterm1 = 0.0
    local Gterm2 = 0.0
    local G = 0.0
    if t > 0 then
        Gterm1 = math.exp(-(z*z)/(4*alpha*t)) / math.sqrt(math.pi)
        Gterm2 = (math.abs(z)/math.sqrt(4*alpha*t))*(1-erf(math.abs(z)/math.sqrt(4*alpha*t)))
        G = math.sqrt(t)*(Gterm1-Gterm2)
    end
    return G
end

function delta_sn(x, y, t)
    local q = 0.0
    local mult = q0/(beta * phi * math.sqrt(alpha))*1e-6 -- turn to MPa unit
    if t >= 0 then
        Gt = getG(y, t, alpha)
        if t <= toff then
            q = mult*Gt
        else
            Gttoff = getG(y, t - toff, alpha)
            q = mult*(Gt - Gttoff)
        end
    end
    return q
end

-- Example usage:
alpha = 0.1             -- m2/s
beta = 1e-8             -- Pa-1
phi = 0.1
q0 = 1.25e-6            -- m/s
toff = 100*60*60*24     -- s

local z = 1
local t = 4e7
q = delta_sn(x, z, t)
print("q value at t = "..t,"==>",q)

-- local file_name = io.open ('time.dat','r')
-- local wfile = io.open("qout.dat", "w")
-- local lines = file_name:lines()
-- t = file_name:read('*number')
-- if t ~= nil then
--     q = delta_sn(0, z, t)
--     wfile:write(q .. "\n")    
-- end
-- for line in lines do
--     t = file_name:read('*number')
--     if t ~= nil then
--         q = delta_sn(0, z, t)
--         wfile:write(q .. "\n")    
--     end
-- end
-- io.close(file_name)
-- io.close(wfile)