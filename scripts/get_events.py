#!/usr/bin/env python3
'''
By Jeena Yun
Update note: 
Last modification: 2024.03.19.
'''
import numpy as np
from read_outputs import load_fault_probe_outputs
from cumslip_compute import compute_cumslip,compute_spinup

save_on = 1
yr2sec = 365*24*60*60
save_dir = '/export/dump/jyun/perturb_stress/hf10_reference'
outputs,dep,params = load_fault_probe_outputs(save_dir)
print(outputs.shape)
print('timestep 0 = %1.15e'%(outputs[100,0,0]))
print('timestep last = %1.15e'%(outputs[100,-1,0]))

# -----
if 'v6_ab2_Dc2' in save_dir:
    Vths = 1e-1
    intv = 0.15
elif 'perturb_stress' in save_dir:
    print('model: perturb_stress')
    Vths = 2e-1
    intv = 0.15
else:
    Vths = 1e-2
    intv = 0.
Vlb = 0
dt_interm = 0
cuttime = 0
rths = 10
dt_creep = 2*yr2sec
dt_coseismic = 0.5

if save_on:
    cumslip_outputs = compute_cumslip(outputs,dep,cuttime,Vlb,Vths,dt_creep,dt_coseismic,dt_interm,intv)
    spin_up_idx = compute_spinup(outputs,dep,cuttime,cumslip_outputs,['yrs',200],rths)[-1]
    np.save('%s/cumslip_outputs_Vths_%1.0e_srvar_%03d_rths_%d_tcreep_%d_tseis_%02d.npy'%(save_dir,Vths,intv*100,rths,dt_creep/yr2sec,dt_coseismic*10),cumslip_outputs)
    np.save('%s/spin_up_idx_Vths_%1.0e_srvar_%03d_rths_%d_tcreep_%d_tseis_%02d.npy'%(save_dir,Vths,intv*100,rths,dt_creep/yr2sec,dt_coseismic*10),spin_up_idx)
else:
    print('%s/cumslip_outputs_Vths_%1.0e_srvar_%03d_rths_%d_tcreep_%d_tseis_%02d.npy'%(save_dir,Vths,intv*100,rths,dt_creep/yr2sec,dt_coseismic*10))
    print('%s/spin_up_idx_Vths_%1.0e_srvar_%03d_rths_%d_tcreep_%d_tseis_%02d.npy'%(save_dir,Vths,intv*100,rths,dt_creep/yr2sec,dt_coseismic*10))