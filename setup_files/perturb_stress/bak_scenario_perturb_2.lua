-- Last modification: 2024.04.05
package.path = package.path .. ";/home/jyun/Tandem"
local ridgecrest54 = require "matfric_Fourier_main_perturb"
local ridgecrest54_stress_dep = require "matfric_Fourier_main_perturb_stress_dep"
local ridgecrest54_sliplaw = require "matfric_Fourier_main_perturb_sliplaw"

-------------------- List of libraries
-- vs340_1515453 = ridgecrest54.new{model_n='vert_slow',strike=340,fcoeff=0.4,dt=0.01,init_time=2.712094562139096069e+10,fsn=6,fab=2,fdc=2,lowres=1,Vp=1e-9}
-- adj_vs340_1515453 = ridgecrest54.new{model_n='vert_slow',strike=340,fcoeff=0.4,dt=0.01,init_time=2.712094562139096069e+10,fsn=6,fab=2,fdc=2,lowres=1,Vp=1e-9}
-- adj3_vs340_1515451 = ridgecrest54.new{model_n='vert_slow',strike=340,fcoeff=0.4,dt=0.01,init_time=2.712094556622940445e+10,fsn=6,fab=2,fdc=2,lowres=1,Vp=1e-9}
-- after_vs340_1515453 = ridgecrest54.new{model_n='vert_slow',strike=340,fcoeff=0.4,dt=0.01,init_time=2.712094562139096069e+10,fsn=6,fab=2,fdc=2,lowres=1,Vp=1e-9}
-- vs340_1515454 = ridgecrest54.new{model_n='vert_slow',strike=340,fcoeff=0.4,dt=0.01,init_time=2.712094562140095901e+10,fsn=6,fab=2,fdc=2,lowres=1,Vp=1e-9}
-- vs340_3092410 = ridgecrest54.new{model_n='vert_slow',strike=340,fcoeff=0.4,dt=0.01,init_time=5.574361834871828461e+10,fsn=6,fab=2,fdc=2,lowres=1,Vp=1e-9}
-- after_vs340_3092410 = ridgecrest54.new{model_n='vert_slow',strike=340,fcoeff=0.4,dt=0.01,init_time=5.574361834871828461e+10,fsn=6,fab=2,fdc=2,lowres=1,Vp=1e-9}
-- vs340_4915642 = ridgecrest54.new{model_n='vert_slow',strike=340,fcoeff=0.4,dt=0.01,init_time=8.267655560204478455e+10,fsn=6,fab=2,fdc=2,lowres=1,Vp=1e-9}
-- vs340_8908134 = ridgecrest54.new{model_n='vert_slow',strike=340,fcoeff=0.4,dt=0.01,init_time=1.421668527168912659e+11,fsn=6,fab=2,fdc=2,lowres=1,Vp=1e-9}
-- vs340_2055768 = ridgecrest54.new{model_n='vert_slow',strike=340,fcoeff=0.4,dt=0.01,init_time=3.721969163349252319e+10,fsn=6,fab=2,fdc=2,lowres=1,Vp=1e-9}
-- vf330_1515453 = ridgecrest54.new{model_n='vert_fast',strike=330,fcoeff=0.4,dt=0.01,init_time=2.712094562139096069e+10,fsn=6,fab=2,fdc=2,lowres=1,Vp=1e-9}
-- vs340_7176480 = ridgecrest54.new{model_n='vert_slow',strike=340,fcoeff=0.4,dt=0.01,init_time=1.162875225174398804e+11,fsn=6,fab=2,fdc=2,lowres=1,Vp=1e-9}
-- vf330_4915642 = ridgecrest54.new{model_n='vert_fast',strike=330,fcoeff=0.4,dt=0.01,init_time=8.267655560204478455e+10,fsn=6,fab=2,fdc=2,lowres=1,Vp=1e-9}
-- ds350_4915642 = ridgecrest54.new{model_n='dipping_slow',strike=350,fcoeff=0.4,dt=0.01,init_time=8.267655560204478455e+10,fsn=6,fab=2,fdc=2,lowres=1,Vp=1e-9}
-- vs340_1516355 = ridgecrest54.new{model_n='vert_slow',strike=340,fcoeff=0.4,dt=0.01,init_time=2.712098594139096069e+10,fsn=6,fab=2,fdc=2,lowres=1,Vp=1e-9}
-- vs340_1509747 = ridgecrest54.new{model_n='vert_slow',strike=340,fcoeff=0.4,dt=0.01,init_time=2.712089594139096069e+10,fsn=6,fab=2,fdc=2,lowres=1,Vp=1e-9}
-- vs340_1517106 = ridgecrest54.new{model_n='vert_slow',strike=340,fcoeff=0.4,dt=0.01,init_time=2.712100034139096069e+10,fsn=6,fab=2,fdc=2,lowres=1,Vp=1e-9}
-- vsX10_340_1515453 = ridgecrest54.new{model_n='vert_slow_X10',strike=340,fcoeff=0.4,dt=0.01,init_time=2.712094562139096069e+10,fsn=6,fab=2,fdc=2,lowres=1,Vp=1e-9}
-- vsX5_340_1515453 = ridgecrest54.new{model_n='vert_slow_X5',strike=340,fcoeff=0.4,dt=0.01,init_time=2.712094562139096069e+10,fsn=6,fab=2,fdc=2,lowres=1,Vp=1e-9}
-- vsX3_340_1515453 = ridgecrest54.new{model_n='vert_slow_X3',strike=340,fcoeff=0.4,dt=0.01,init_time=2.712094562139096069e+10,fsn=6,fab=2,fdc=2,lowres=1,Vp=1e-9}
-- vs340_1515030 = ridgecrest54.new{model_n='vert_slow',strike=340,fcoeff=0.4,dt=0.01,init_time=2.712093194139096069e+10,fsn=6,fab=2,fdc=2,lowres=1,Vp=1e-9}
-- vs340_1515453_stress_dep = ridgecrest54_stress_dep.new{model_n='vert_slow',strike=340,fcoeff=0.4,dt=0.01,init_time=2.712094562139096069e+10,fsn=6,fab=2,fdc=2,lowres=1,Vp=1e-9}
-- vs340_2055768_stress_dep = ridgecrest54_stress_dep.new{model_n='vert_slow',strike=340,fcoeff=0.4,dt=0.01,init_time=3.721969163349252319e+10,fsn=6,fab=2,fdc=2,lowres=1,Vp=1e-9}
-- vs340_4915642_stress_dep = ridgecrest54_stress_dep.new{model_n='vert_slow',strike=340,fcoeff=0.4,dt=0.01,init_time=8.267655560204478455e+10,fsn=6,fab=2,fdc=2,lowres=1,Vp=1e-9}
-- vf330_4915642_stress_dep = ridgecrest54_stress_dep.new{model_n='vert_fast',strike=330,fcoeff=0.4,dt=0.01,init_time=8.267655560204478455e+10,fsn=6,fab=2,fdc=2,lowres=1,Vp=1e-9}
-- ds350_4915642_stress_dep = ridgecrest54_stress_dep.new{model_n='dipping_slow',strike=350,fcoeff=0.4,dt=0.01,init_time=8.267655560204478455e+10,fsn=6,fab=2,fdc=2,lowres=1,Vp=1e-9}
-- vsX10_340_1515453_stress_dep = ridgecrest54_stress_dep.new{model_n='vert_slow_X10',strike=340,fcoeff=0.4,dt=0.01,init_time=2.712094562139096069e+10,fsn=6,fab=2,fdc=2,lowres=1,Vp=1e-9}
-- vs320_2055768 = ridgecrest54.new{model_n='vert_slow',strike=320,fcoeff=0.4,dt=0.01,init_time=3.721969163349252319e+10,fsn=6,fab=2,fdc=2,lowres=1,Vp=1e-9}
-- vs320_4915642 = ridgecrest54.new{model_n='vert_slow',strike=320,fcoeff=0.4,dt=0.01,init_time=8.267655560204478455e+10,fsn=6,fab=2,fdc=2,lowres=1,Vp=1e-9}
-- vf320_2055768 = ridgecrest54.new{model_n='vert_fast',strike=320,fcoeff=0.4,dt=0.01,init_time=3.721969163349252319e+10,fsn=6,fab=2,fdc=2,lowres=1,Vp=1e-9}
-- df320_1515453 = ridgecrest54.new{model_n='dipping_fast',strike=320,fcoeff=0.4,dt=0.01,init_time=2.712094562139096069e+10,fsn=6,fab=2,fdc=2,lowres=1,Vp=1e-9}
-- df330_2055768 = ridgecrest54.new{model_n='dipping_fast',strike=330,fcoeff=0.4,dt=0.01,init_time=3.721969163349252319e+10,fsn=6,fab=2,fdc=2,lowres=1,Vp=1e-9}
-- ds330_4915642 = ridgecrest54.new{model_n='dipping_slow',strike=330,fcoeff=0.4,dt=0.01,init_time=8.267655560204478455e+10,fsn=6,fab=2,fdc=2,lowres=1,Vp=1e-9}
-- ds340_4915642 = ridgecrest54.new{model_n='dipping_slow',strike=340,fcoeff=0.4,dt=0.01,init_time=8.267655560204478455e+10,fsn=6,fab=2,fdc=2,lowres=1,Vp=1e-9}
-- df340_4915642 = ridgecrest54.new{model_n='dipping_fast',strike=340,fcoeff=0.4,dt=0.01,init_time=8.267655560204478455e+10,fsn=6,fab=2,fdc=2,lowres=1,Vp=1e-9}
-- vf340_4915642 = ridgecrest54.new{model_n='vert_fast',strike=340,fcoeff=0.4,dt=0.01,init_time=8.267655560204478455e+10,fsn=6,fab=2,fdc=2,lowres=1,Vp=1e-9}
-- vs340_2348838_diffwavelength = ridgecrest54.new{model_n='vert_slow',strike=340,fcoeff=0.4,dt=0.01,init_time=2.668015812663448715e+10,fsn=8,fab=3,fdc=10,lowres=1,Vp=1e-9}
vs340_456169_lowres_spinup_sliplaw_reference = ridgecrest54_sliplaw.new{model_n='vert_slow',strike=340,fcoeff=0.4,dt=0.01,init_time=7.076414321358305931e+09,fsn=6,fab=2,fdc=2,lowres=5,Vp=1e-09}
