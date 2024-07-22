import numpy as np
import matplotlib.pylab as plt
from pub_cumslip_compute import *
from read_outputs import load_fault_probe_outputs
import myplots
import setup_shortcut

mp = myplots.Figpref()
sc = setup_shortcut.setups()

def cumslip_spinup(ax,prefix,cumslip_outputs,spup_cumslip_outputs,rths,legend_on=False):
    system_wide,partial_rupture,event_cluster,lead_fs = analyze_events(cumslip_outputs,rths)[2:6]
    Hs = ch.load_parameter(prefix)[1]

    linewidth = 0.5
    size_star,size_diamond,scatter_lw =100,50,0.5
    if len(cumslip_outputs) > 4:
        ax.plot(spup_cumslip_outputs[4],cumslip_outputs[4][1],color='yellowgreen',lw=linewidth)
    ax.plot(spup_cumslip_outputs[3],cumslip_outputs[3][1],color=mp.mydarkpink,lw=linewidth)
    ax.plot(spup_cumslip_outputs[2],cumslip_outputs[2][1],color='0.62',lw=linewidth)
    if len(system_wide) > 0:
        ax.scatter(spup_cumslip_outputs[1][system_wide],cumslip_outputs[1][1][system_wide],marker='*',s=size_star,facecolor=mp.mydarkviolet,edgecolors='k',lw=scatter_lw,zorder=3,label='System-wide events')
    if len(lead_fs) > 0:
        ax.scatter(spup_cumslip_outputs[1][lead_fs],cumslip_outputs[1][1][lead_fs],marker='d',s=size_diamond,facecolor=mp.mydarkviolet,edgecolors='k',lw=scatter_lw,zorder=3,label='Leading foreshocks')
    if len(partial_rupture) > 0:
        ax.scatter(spup_cumslip_outputs[1][partial_rupture],cumslip_outputs[1][1][partial_rupture],marker='d',s=size_diamond,facecolor='w',edgecolors='k',lw=scatter_lw,zorder=2,label='Partial rupture events')
    if legend_on: ax.legend(fontsize=10,framealpha=1,loc='lower right')
    xl = ax.get_xlim()
    ax.set_xlim(0,xl[1])
    ax.set_ylabel('Depth [km]',fontsize=12.5)
    ax.set_xlabel('Cumulative Slip [m]',fontsize=12.5)
    ax.set_ylim(0,Hs[0])
    ax.invert_yaxis()


testmode = 1
plt.rcParams['font.size'] = '12'
fig,ax = plt.subplots(2,2,figsize=(12,8))
from string import ascii_lowercase
tits = ['Normal Stress Hetergeneity',r'D$_{\bf RS}$ Hetergeneity','(a-b) Hetergeneity',r'Normal Stress, D$_{\bf RS}$, and (a-b) Hetergeneity']
model_lists = ['models/Thakur20_hetero_stress/n8_v6',\
                'models/Thakur20_various_fractal_profiles/ab2',\
                'models/Thakur20_various_fractal_profiles/v6_ab2_Dc2_mu32',\
                'models/Thakur20_various_fractal_profiles/v6_ab2_Dc2_mu20']
Vths,SRvar,Vlb,dt_interm,cuttime,rths,dt_creep,dt_coseismic = 1e-2,0,0,0,0,10,2*sc.yr2sec,0.5

legend_on = False
for ii,prefix in enumerate(model_lists):
        if 'v6_ab2_Dc2_mu32' in prefix:
                Vths = 0.05
        outputs,dep,params = load_fault_probe_outputs(prefix,print_on=False)
        cumslip_outputs = cumslip_outputs = compute_cumslip(outputs,dep,cuttime,Vlb,Vths,dt_creep,dt_coseismic,dt_interm,SRvar,print_on=False)
        spup_cumslip_outputs = compute_spinup(outputs,dep,cuttime,cumslip_outputs,['yrs',200],rths,print_on=False)
        if ii == 0: legend_on = True
        cumslip_spinup(ax[int(ii/2),np.mod(ii,2)],prefix,cumslip_outputs,spup_cumslip_outputs,rths,legend_on=legend_on)
        xl = ax[int(ii/2),np.mod(ii,2)].get_xlim()
        ax[int(ii/2),np.mod(ii,2)].text(-xl[1]*0.1237,-1.25,'(%s)'%(ascii_lowercase[ii]),fontweight='bold',fontsize=15)
        ax[int(ii/2),np.mod(ii,2)].set_title('%s'%(tits[ii]),fontweight='bold',fontsize=13)
        legend_on = False

plt.tight_layout()
if testmode:
    plt.savefig('/home/jyun/Tandem/test.png')
else:
    plt.savefig('/export/dump/jyun/perturb_stress/plots/spinup_cumslip_all.png',dpi=300)