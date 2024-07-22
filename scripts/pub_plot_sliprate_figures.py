'''
(Publication) Generate combined slip rate images
By Jeena Yun
Last modification: 2024.04.21.
'''
import numpy as np
import matplotlib.pylab as plt
from pub_faultoutputs_image import *
import myplots
from read_outputs import load_fault_probe_outputs
from cumslip_compute import *
import setup_shortcut
import os
mp = myplots.Figpref()
sc = setup_shortcut.setups()

image = 'sliprate'
yr2sec = 60*60*24*365

# ---------- Load reference event details
vmin,vmax,Vths,intv,Vlb,dt_interm,cuttime,rths,dt_creep,dt_coseismic = sc.base_event_criteria('/export/dump/jyun/perturb_stress/reference',image)
print('Load reference event details')
cumslip_outputs = np.load('/export/dump/jyun/perturb_stress/reference/cumslip_outputs_Vths_%1.0e_srvar_%03d_rths_%d_tcreep_%d_tseis_%02d.npy'%(Vths,intv*100,rths,dt_creep/yr2sec,dt_coseismic*10),allow_pickle=True)
ref_tstart = cumslip_outputs[0][0]

# ----------
publish = True
save_on = 1
# system_color = mp.mydarkviolet
system_color = mp.mymint
partial_color = 'w'
size_star,size_diamond,scatter_lw =250,60,0.7

plt.rcParams['font.size'] = '12'
fig = plt.figure(figsize=(12,9))
grid = plt.GridSpec(2, 5)

# --------- X10 script (full)
prefix = 'perturb_stress/after_pert8_vsX10_340'
save_dir = '/export/dump/jyun/'+prefix
outputs,dep,params = load_fault_probe_outputs(save_dir)

print('Compute perturbed event details')
cumslip_outputs = compute_cumslip(outputs,dep,cuttime,Vlb,Vths,dt_creep,dt_coseismic,dt_interm,intv)
tstart,evdep = cumslip_outputs[0][0],cumslip_outputs[1][1]
rupture_length,av_slip,system_wide,partial_rupture,event_cluster,lead_fs,major_pr,minor_pr = analyze_events(cumslip_outputs,rths)
ii = np.argsort(abs(dep))
time = outputs[0,:,0]
its_all = np.array([np.argmin(abs(outputs[0][:,0]-t)) for t in tstart])

plt.subplot(grid[0, 0:])
fout_image(image,outputs,dep,params,cumslip_outputs,save_dir,prefix,rths,vmin,vmax,Vths,[],plot_in_timestep=True,plot_in_sec=False,cb_off=False,publish=publish,no_scatter=True,save_on=False)
plt.scatter(its_all[2],evdep[2],s=size_star,marker='*',facecolor=system_color,edgecolor='k',lw=scatter_lw,zorder=3,label='System-size events')
if len(lead_fs) > 0:
    plt.scatter(its_all[0],evdep[0],s=size_diamond,marker='d',facecolor=system_color,edgecolor='k',lw=scatter_lw,zorder=3,label='Leading foreshocks')
if len(partial_rupture) > 0:
    plt.scatter(its_all[[1,3,4,5,6]],evdep[[1,3,4,5,6]],s=size_diamond,marker='d',facecolor=partial_color,edgecolor='k',lw=scatter_lw,zorder=2,label='Partial rupture events')
plt.text(its_all[2]-250,evdep[2]+0.75,'3',color='w',fontsize=11.5,fontweight='bold',ha='right',va='top')
plt.text(its_all[1]-150,evdep[1]-0.3,'2',color='w',fontsize=11.5,fontweight='bold',ha='right',va='bottom')
plt.text(its_all[0],evdep[0]-0.5,'1',color='w',fontsize=11.5,fontweight='bold',ha='right',va='bottom')
xl = plt.xlim()
plt.text(-xl[1]*0.08,-1.25,'(a)',color='k',fontsize=17,fontweight='bold')
plt.title('Event 88; VSI, 340˚; X10 Amplified',fontsize=15,fontweight='bold')
plt.legend(fontsize=10,framealpha=1,loc='lower right')
plt.vlines(x=np.argmin(abs(time-ref_tstart[88])),ymin=0,ymax=24,linestyle='--',color='w',lw=1.5)
plt.text(np.argmin(abs(time-ref_tstart[88]))+500,23,r'← $\bf t_{ u}$',color='w',fontsize=14.5,fontweight='bold',ha='left',va='bottom')
# plt.text(np.argmin(abs(time-ref_tstart[88]))+500,23,'← Time of the unperturbed mainshock',color='w',fontsize=14.5,fontweight='bold',ha='left',va='bottom')
plt.ylim(0,24)
plt.gca().invert_yaxis()
plt.tight_layout()

# --------- X30 script
prefix = 'perturb_stress/pert8_vsX30_340'
save_dir = '/export/dump/jyun/'+prefix
outputs,dep,params = load_fault_probe_outputs(save_dir)

print('Compute perturbed event details')
cumslip_outputs = compute_cumslip(outputs,dep,cuttime,Vlb,Vths,dt_creep,dt_coseismic,dt_interm,intv)
tstart,evdep = cumslip_outputs[0][0],cumslip_outputs[1][1]
system_wide = analyze_events(cumslip_outputs,rths)[2]
ii = np.argsort(abs(dep))
time = outputs[0,:,0]
its_all = np.array([np.argmin(abs(outputs[0][:,0]-t)) for t in tstart])

plt.subplot(grid[1, 1:4])
fout_image(image,outputs,dep,params,cumslip_outputs,save_dir,prefix,rths,vmin,vmax,Vths,[],plot_in_timestep=False,plot_in_sec=True,cb_off=False,publish=publish,no_scatter=True,save_on=False)
plt.scatter(tstart[0]-time[0],evdep[0],s=size_star,marker='*',facecolor=mp.mymint,edgecolor='k',lw=scatter_lw,zorder=3,label='System-size event')
xl = plt.xlim()
plt.text(-xl[1]*0.13,-1.25,'(b)',color='k',fontsize=17,fontweight='bold')
plt.title('Event 88; VSI, 340˚; X30 Amplified',fontsize=13,fontweight='bold')
# plt.legend(fontsize=10,framealpha=1,loc='lower right')
plt.ylim(0,24)
plt.gca().invert_yaxis()
plt.tight_layout()

# if save_on: plt.savefig('test.png')
if save_on: plt.savefig('/export/dump/jyun/perturb_stress/plots/pub_X10_X30_sliprate_image.png',dpi=350)
print('saving png done')
# if save_on: plt.savefig('pub_X10_X30_sliprate_image.pdf',dpi=350)
# print('saving pdf done')
