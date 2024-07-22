#!/usr/bin/env python3
"""
(Publication) Generate a figure that compares the timing of the perturbation
Last modification: 2024.04.22.
by Jeena Yun
"""
import numpy as np
from perturb_tools import ROUTINE_PERTURB
from perturb_plots import fout_time_max,fout_time,pub_triggering_response
import matplotlib.pylab as plt
from matplotlib.patches import Rectangle,FancyArrowPatch
import myplots
mp = myplots.Figpref()
plt.rcParams['font.size'] = '11'

save_on = 1
axis_lab_fs = 11.5
figlab_fs = 15
tit_fs = 14
legend_fs = 9
txt_fs=13
lines_lw1 = 1.25
lines_lw2 = 2.
vline_lw = 1.5

xlmin,xlmax = -18*3600, 3*3600

# ----- Initiate class and load outputs
routine = ROUTINE_PERTURB('pert31_vs340')

fig,[ax1,ax2]=plt.subplots(nrows=2,ncols=1,figsize=(8,8),dpi=350)
# ----- 1. Big picture
lag,noline,after_tstart = routine.estimate_triggering_response(routine.ref,routine.after_pert)
if lag > 0: time_tag = "advance"
else: time_tag = "delay"

ref_outputs = np.copy(routine.ref.outputs)
pert_outputs = np.copy(routine.pert.outputs)
after_pert_outputs = np.copy(routine.after_pert.outputs)
ref_outputs[:,:,0] = ref_outputs[:,:,0] - routine.ref.tstart[routine.ref.idx]
pert_outputs[:,:,0] = pert_outputs[:,:,0] - routine.ref.tstart[routine.ref.idx]
after_pert_outputs[:,:,0] = after_pert_outputs[:,:,0] - routine.ref.tstart[routine.ref.idx]

i1 = np.where(np.logical_and(ref_outputs[0,:,0] >= xlmin, ref_outputs[0,:,0] <= xlmax))[0]
ax1,_ = fout_time_max(ax1,ref_outputs[:,i1,:],'sliprate',plot_in_sec=True,lw=lines_lw1,col='k',lab='Unperturbed',fs=axis_lab_fs)
ax1,pmax = fout_time_max(ax1,pert_outputs[:,1:,:],'sliprate',plot_in_sec=True,lw=lines_lw1,col=mp.mypink,lab='Perturbation Period',fs=axis_lab_fs)
ax1,_ = fout_time_max(ax1,after_pert_outputs[:,1:,:],'sliprate',plot_in_sec=True,lw=lines_lw1,col=mp.mynavy,lab='Perturbed',fs=axis_lab_fs)
# ax1,_ = fout_time_max(ax1,after_pert_outputs[:,1:,:],'sliprate',plot_in_sec=True,lw=lines_lw1,col=mp.myblue,lab='Perturbed',fs=axis_lab_fs)
ax1.legend(fontsize=legend_fs,loc='upper left')

xl = [xlmin,xlmax]
yl = ax1.get_ylim()
ax1.vlines(x=0,ymin=yl[0]*2,ymax=yl[1]*2,lw=vline_lw,colors='0.5',linestyles='--',zorder=0)
ax1.text((xl[1]-xl[0])*0.01,-yl[1]*2.5,r'$\bf t_{ event}$',fontsize=txt_fs,color='0.5',fontweight='bold')
ax1.vlines(x=after_tstart-routine.ref.tstart[routine.ref.idx],ymin=yl[0]*2,ymax=yl[1]*2,lw=vline_lw,colors=mp.myblue,linestyles='--',zorder=0)
ax1.text((after_tstart-routine.ref.tstart[routine.ref.idx])+(xl[1]-xl[0])*0.01,-yl[1]*2.5,r'$\bf t_{ event}^{ \delta}$',fontsize=txt_fs,color=mp.myblue,fontweight='bold')
# ax1.vlines(x=after_tstart-routine.ref.tstart[routine.ref.idx],ymin=yl[0]*2,ymax=yl[1]*2,lw=vline_lw,colors=mp.mynavy,linestyles='--',zorder=0)
# ax1.text((after_tstart-routine.ref.tstart[routine.ref.idx])+(xl[1]-xl[0])*0.01,-yl[1]*2.5,r'$\bf t_{ event}^{ \delta}$',fontsize=txt_fs,color=mp.mynavy,fontweight='bold')

ax1.add_patch(FancyArrowPatch((after_tstart[0]-routine.ref.tstart[routine.ref.idx],-1.5),(0,-1.5),arrowstyle='<->',mutation_scale=10,color=mp.myburgundy))
ax1.text((after_tstart[0]-routine.ref.tstart[routine.ref.idx])/2,-1.25,r'$\bf t_{ diff}$',fontsize=txt_fs,color=mp.myburgundy,fontweight='bold',ha='center',va='bottom')

ax1.add_patch(Rectangle((pert_outputs[0,1,0]-1800,(yl[0]+min(pmax))/2),3600,4,ec='0.5',fc='none',lw=vline_lw,linestyle='--'))
ax1.text(pert_outputs[0,1,0]-1800,(yl[0]+min(pmax))/2+4,'(b)',fontsize=txt_fs,fontweight='bold',color='k',ha='right',va='bottom')

ax1.text(xl[0]-(xl[1]-xl[0])*0.07,yl[1]+(yl[1]-yl[0])*0.02,'(a)',fontsize=figlab_fs,fontweight='bold',color='k',ha='right',va='bottom')
ax1.set_title('Event 282',fontsize=tit_fs,fontweight='bold')
# ax1.set_title('Event 282 (%1.2f km)'%(routine.ref.evdep[routine.ref.idx]),fontsize=tit_fs,fontweight='bold')
xt = np.linspace(xlmin,xlmax,8)
xtl = ['%d'%(ixt/3600) for ixt in xt]
ax1.set_xticks(ticks=xt,labels=xtl)
ax1.set_xlabel('Time relative to the unperturbed event time [hr]',fontsize=axis_lab_fs)
ax1.grid(True,alpha=0.5)
ax1.set_xlim(xl)
ax1.set_ylim(yl)

# ----- 2. During perturbation
_,time_tandem,pn,ts = routine.pert.get_output_dCFS(routine.ref.evdep[routine.ref.idx])
ax2.plot(time_tandem,-ts,c=mp.mydarkpink,lw=lines_lw2,label='Shear Traction',zorder=3)
ax2.plot(time_tandem,pn,c=mp.mypink,lw=lines_lw2,linestyle='--',label='Normal Stress',zorder=2)
ax2.legend(fontsize=legend_fs,loc='lower right')

xl = ax2.get_xlim()
yl = ax2.get_ylim()
ax2.text(xl[0]-(xl[1]-xl[0])*0.07,yl[1]+(yl[1]-yl[0])*0.02,'(b)',fontsize=figlab_fs,fontweight='bold',color='k',ha='right',va='bottom')
ax2.set_title('Stress Perturbation History at %1.2f km (VSI, 340˚)'%(routine.ref.evdep[routine.ref.idx]),fontsize=tit_fs,fontweight='bold')
# ax2.set_title('Stress Perturbation at Unperturbed Hypocenter (VSI, 340˚)',fontsize=tit_fs,fontweight='bold')
ax2.set_xlabel('Time Since Start of Perturbation [s]',fontsize=axis_lab_fs)
ax2.set_ylabel('Stress Change [MPa]',fontsize=axis_lab_fs)
ax2.grid(True,alpha=0.5)
ax2.set_xlim(xl)
ax2.set_ylim(yl)

plt.tight_layout()
if save_on: plt.savefig('/export/dump/jyun/perturb_stress/plots/compare_pert_time.png',dpi=350)