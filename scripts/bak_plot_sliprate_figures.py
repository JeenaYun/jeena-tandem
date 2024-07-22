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
prefix = 'perturb_stress/after_pert8_vsX10_340'
# prefix = 'perturb_stress/pert8_vsX30_340'
save_dir = '/export/dump/jyun/'+prefix
outputs,dep,params = load_fault_probe_outputs(save_dir)

vmin,vmax,Vths,intv,Vlb,dt_interm,cuttime,rths,dt_creep,dt_coseismic = sc.base_event_criteria('/export/dump/jyun/perturb_stress/reference',image)
# ---------- Load reference event details
if 'X10' in save_dir:
    print('Load reference event details')
    cumslip_outputs = np.load('/export/dump/jyun/perturb_stress/reference/cumslip_outputs_Vths_%1.0e_srvar_%03d_rths_%d_tcreep_%d_tseis_%02d.npy'%(Vths,intv*100,rths,dt_creep/yr2sec,dt_coseismic*10),allow_pickle=True)
    ref_tstart = cumslip_outputs[0][0]

# ----------
print('Compute perturbed event details')
cumslip_outputs = compute_cumslip(outputs,dep,cuttime,Vlb,Vths,dt_creep,dt_coseismic,dt_interm,intv)
tstart,tend,evdep = cumslip_outputs[0][0],cumslip_outputs[0][1],cumslip_outputs[1][1]
rupture_length,av_slip,system_wide,partial_rupture,event_cluster,lead_fs,major_pr,minor_pr = analyze_events(cumslip_outputs,rths)
if len(major_pr) > 0: major_pr = event_cluster[major_pr][:,1]
if len(minor_pr) > 0: minor_pr = event_cluster[minor_pr][:,1]

print('Total number of events: %d'%(len(tstart)))
print('System-size indexes:',system_wide)
print('Evdep:',evdep)
print('Event depth with perturbation:',evdep[system_wide])

# ----------
ii = np.argsort(abs(dep))
time = outputs[0,:,0]
its_all = np.array([np.argmin(abs(outputs[0][:,0]-t)) for t in tstart])

# ----------
publish = True
save_on = 1
# system_color = mp.mydarkviolet
system_color = mp.mymint
partial_color = 'w'

# --------- X10 script (full)
ax=fout_image(image,outputs,dep,params,cumslip_outputs,save_dir,prefix,rths,vmin,vmax,Vths,[],horz_size=12,vert_size=4.5,plot_in_timestep=True,plot_in_sec=False,cb_off=False,publish=publish,save_on=False)
plt.scatter(its_all[2],evdep[2],s=200,marker='*',facecolor=system_color,edgecolor='k',lw=0.7,zorder=3,label='System-size events')
if len(lead_fs) > 0:
    plt.scatter(its_all[0],evdep[0],s=40,marker='d',facecolor=system_color,edgecolor='k',lw=0.7,zorder=3,label='Leading foreshocks')
if len(partial_rupture) > 0:
    plt.scatter(its_all[[1,3,4,5,6]],evdep[[1,3,4,5,6]],s=40,marker='d',facecolor=partial_color,edgecolor='k',lw=0.7,zorder=2,label='Partial rupture events')
ax.text(its_all[2]-250,evdep[2]+0.75,'3',color='w',fontsize=11.5,fontweight='bold',ha='right',va='top')
ax.text(its_all[1]-150,evdep[1]-0.3,'2',color='w',fontsize=11.5,fontweight='bold',ha='right',va='bottom')
ax.text(its_all[0],evdep[0]-0.5,'1',color='w',fontsize=11.5,fontweight='bold',ha='right',va='bottom')
ax.legend(fontsize=10,framealpha=1,loc='lower right')
ax.vlines(x=np.argmin(abs(time-ref_tstart[88])),ymin=0,ymax=24,linestyle='--',color='w',lw=1.5)
ax.text(np.argmin(abs(time-ref_tstart[88]))+500,23,'← Time of the unperturbed mainshock',color='w',fontsize=14.5,fontweight='bold',ha='left',va='bottom')
ax.set_ylim(0,24)
ax.invert_yaxis()
plt.tight_layout()
# if save_on: plt.savefig('%s/test.png'%(save_dir))
if save_on: plt.savefig('%s/sliprate_timestep_with_previous_event.png'%(save_dir),dpi=350)
print('saving png done')
# if save_on: plt.savefig('%s/sliprate_timestep_with_previous_event.pdf'%(save_dir),dpi=350)
# print('saving pdf done')

# --------- X10 script (decimated)
# ax=fout_image(image,outputs[:,::2,:],dep,params,cumslip_outputs,save_dir,prefix,rths,vmin,vmax,Vths,[],horz_size=12,vert_size=4.5,plot_in_timestep=True,plot_in_sec=False,cb_off=False,publish=publish,save_on=False)
# plt.scatter(its_all[2]/2,evdep[2],s=200,marker='*',facecolor=system_color,edgecolor='k',lw=0.7,zorder=3,label='System-size events')
# if len(lead_fs) > 0:
#     plt.scatter(its_all[0]/2,evdep[0],s=40,marker='d',facecolor=system_color,edgecolor='k',lw=0.7,zorder=3,label='Leading foreshocks')
# if len(partial_rupture) > 0:
#     plt.scatter(its_all[[1,3,4,5,6]]/2,evdep[[1,3,4,5,6]],s=40,marker='d',facecolor=partial_color,edgecolor='k',lw=0.7,zorder=2,label='Partial rupture events')
# ax.text((its_all[2]-250)/2,evdep[2]+0.75,'3',color='w',fontsize=11.5,fontweight='bold',ha='right',va='top')
# ax.text((its_all[1]-150)/2,evdep[1]-0.3,'2',color='w',fontsize=11.5,fontweight='bold',ha='right',va='bottom')
# ax.text((its_all[0])/2,evdep[0]-0.5,'1',color='w',fontsize=11.5,fontweight='bold',ha='right',va='bottom')
# ax.legend(fontsize=10,framealpha=1,loc='lower right')
# ax.vlines(x=np.argmin(abs(time-ref_tstart[88]))/2,ymin=0,ymax=24,linestyle='--',color='w',lw=1.5)
# ax.text((np.argmin(abs(time-ref_tstart[88]))+500)/2,23,'← Time of the unperturbed mainshock',color='w',fontsize=14.5,fontweight='bold',ha='left',va='bottom')
# ax.set_ylim(0,24)
# ax.invert_yaxis()
# xl = ax.get_xlim()
# locs, labels = plt.xticks()
# x2 = ['%d'%(l*2) for l in locs]
# plt.xticks(locs,x2)
# ax.set_xlim(xl)
# plt.tight_layout()
# if save_on: plt.savefig('%s/test.png'%(save_dir))
# if save_on: plt.savefig('%s/sliprate_timestep_with_previous_event.png'%(save_dir),dpi=350)
# print('saving png done')
# if save_on: plt.savefig('%s/sliprate_timestep_with_previous_event.pdf'%(save_dir),dpi=350)
# print('saving pdf done')

# --------- X30 script
# ax=fout_image(image,outputs,dep,params,cumslip_outputs,save_dir,prefix,rths,vmin,vmax,Vths,[],horz_size=8,vert_size=4.5,plot_in_timestep=False,plot_in_sec=True,cb_off=False,publish=publish,save_on=False)
# # plt.scatter(tstart[0]-time[0],evdep[0],s=200,marker='*',facecolor=system_color,edgecolor='k',lw=0.7,zorder=3,label='System-size event')
# plt.scatter(tstart[0]-time[0],evdep[0],s=200,marker='*',facecolor=mp.mymint,edgecolor='k',lw=0.7,zorder=3,label='System-size event')
# ax.legend(fontsize=10,framealpha=1,loc='lower right')
# ax.set_ylim(0,24)
# ax.invert_yaxis()
# plt.tight_layout()
# # if save_on: plt.savefig('%s/test.png'%(save_dir))
# if save_on: plt.savefig('%s/sliprate_image.png'%(save_dir),dpi=350)
# print('saving png done')
# # if save_on: plt.savefig('%s/sliprate_image.pdf'%(save_dir),dpi=350)
# # print('saving pdf done')
