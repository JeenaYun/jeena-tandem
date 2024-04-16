package.path = package.path .. ";/home/jyun/Tandem"
local ridgecrest54 = require "matfric_Fourier_main_perturb"
local ridgecrest54_stress_dep = require "matfric_Fourier_main_perturb_stress_dep"
local ridgecrest54_sliplaw = require "matfric_Fourier_main_perturb_sliplaw"


vs340_456169_lowres_spinup_sliplaw_reference = ridgecrest54_sliplaw.new{model_n='vert_slow',strike=340,fcoeff=0.4,dt=0.01,init_time=7.076414321358305931e+09,fsn=6,fab=2,fdc=2,lowres=5,Vp=1e-09}