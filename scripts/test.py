def testfun(a,b='default'):
    return a,b

a,b1 = testfun(a='fixed a',b='some value')
print('a = %s, b1 = %s'%(a,b1))
a,b2 = testfun(a='fixed a',b=None)
print('a = %s, b2 = %s'%(a,b2))
a,b3 = testfun('fixed a')
print('a = %s, b3 = %s'%(a,b3))



# import numpy as np
# import matplotlib.pylab as plt
# from faultoutputs_image import *
# import setup_shortcut
# import change_params
# import myplots
# from read_outputs import load_fault_probe_outputs,load_short_fault_probe_outputs
# plt.rcParams['font.size'] = '15'

# sc = setup_shortcut.setups()
# mp = myplots.Figpref()
# ch = change_params.variate()

# prefix,compute_on,short_out_idx,load_output = 'perturb_stress/reference',False,0,False
# save_dir = '/export/dump/jyun/'+prefix

# # ----------
# y,Hs,a,b,a_b,tau0,sigma0,Dc,others = ch.load_parameter(prefix)

# # ----------
# outputs,dep,params = load_fault_probe_outputs(save_dir)

# # ----------
# from cumslip_compute import *
# import os

# image = 'sliprate'
# # image = 'shearT'
# print('Image %s figure'%(image))

# if image == 'sliprate':
#     vmin,vmax = 1e-12,1e1
# elif image == 'shearT':
#     vmin,vmax = -5,5
# else:
#     vmin,vamx = None,None

# if 'v6_ab2_Dc2' in prefix:
#     Vths = 1e-1
#     intv = 0.15
# elif 'perturb_stress' in prefix:
#     Vths = 2e-1
#     intv = 0.15
# else:
#     Vths = 1e-2
#     intv = 0.
# Vlb = 0
# dt_interm = 0
# cuttime = 0
# rths = 10
# dt_creep = 2*ch.yr2sec
# dt_coseismic = 0.5

# if not compute_on:
#     print('Load saved file')
#     cumslip_outputs = np.load('/export/dump/jyun/perturb_stress/reference/cumslip_outputs_Vths_%1.0e_srvar_%03d_rths_%d_tcreep_%d_tseis_%02d.npy'%(Vths,intv*100,rths,dt_creep/ch.yr2sec,dt_coseismic*10),allow_pickle=True)
# else:
#     print('Compute event details')
#     cumslip_outputs = compute_cumslip(outputs,dep,cuttime,Vlb,Vths,dt_creep,dt_coseismic,dt_interm,intv)
# tstart,tend,evdep = cumslip_outputs[0][0],cumslip_outputs[0][1],cumslip_outputs[1][1]
# rupture_length,av_slip,system_wide,partial_rupture,event_cluster,lead_fs,major_pr,minor_pr = analyze_events(cumslip_outputs,rths)
# if len(major_pr) > 0: major_pr = event_cluster[major_pr][:,1]
# if len(minor_pr) > 0: minor_pr = event_cluster[minor_pr][:,1]

# if not compute_on:
#     print('Load saved file')
#     spin_up_idx = np.load('/export/dump/jyun/perturb_stress/reference/spin_up_idx_Vths_%1.0e_srvar_%03d_rths_%d_tcreep_%d_tseis_%02d.npy'%(Vths,intv*100,rths,dt_creep/ch.yr2sec,dt_coseismic*10))
# else:
#     print('Compute spin-up index')
#     spin_up_idx = compute_spinup(outputs,dep,cuttime,cumslip_outputs,['yrs',200],rths)[-1]
#     # spup_cumslip_outputs = compute_spinup(outputs,dep,cuttime,cumslip_outputs,['yrs',200],rths)
#     # spin_up_idx = spup_cumslip_outputs[-1]

# print('Total number of events: %d / Spin-up index: %d'%(len(tstart),spin_up_idx))
# print('System-size indexes:',system_wide)

# # ----------
# from event_analyze import analyze_SSE_events
# SSE_type='shallow'
# SSE_outputs_shallow = compute_SSE_cumslip(outputs,dep,SSE_type,cumslip_outputs,print_on=True)
# np.save('%s/%s_SSE.npy'%(save_dir,SSE_type),SSE_outputs_shallow)

# SSE_type='deep'
# SSE_outputs_deep = compute_SSE_cumslip(outputs,dep,SSE_type,cumslip_outputs,print_on=True)
# np.save('%s/%s_SSE.npy'%(save_dir,SSE_type),SSE_outputs_deep)
# # sse_rupture_length,sse_av_slip = analyze_SSE_events(SSE_outputs,print_on=True)