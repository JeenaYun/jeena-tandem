import numpy as np
import setup_shortcut
import change_params
from read_outputs import *
import matplotlib.pylab as plt
import myplots
from cumslip_compute import analyze_events,compute_cumslip
mp = myplots.Figpref()
plt.rcParams['font.size'] = '15'
sc = setup_shortcut.setups()
ch = change_params.variate()

target_eventid = 12
save_dir = 'perturb_stress/seissol_outputs'
model_n = 'vert_slow'
mu = 0.4
receivef_strike = 320

save_dir1 = '/export/dump/jyun/perturb_stress/reference'
save_dir3 = '/export/dump/jyun/perturb_stress/after_pert%d_%s%d'%(target_eventid,sc.model_code(model_n),receivef_strike)

if 'save_dir3' in locals(): outputs3,dep3,params3 = load_fault_probe_outputs(save_dir3)

if 'save_dir1' in locals():
    start_time = np.load('%s/short_outputs_start_time.npy'%(save_dir1))
    if len(np.where(start_time<=outputs3[0,0,0])[0]) > 0:
        soidx = np.where(start_time<=outputs3[0,0,0])[0][-1]
        if soidx < len(start_time)-1 and outputs3[0,-1,0] >= start_time[soidx+1]:
            print('WARNING: Output 2 and 3 are in the middle of short outputs %d and %d - loading both'%(soidx,soidx+1))
            outputs1_1,dep1_1,params1_1 = load_short_fault_probe_outputs(save_dir1,soidx)
            outputs1_2,dep1_2,params1_2 = load_short_fault_probe_outputs(save_dir1,soidx+1)
        else:
            outputs1,dep1,params1 = load_short_fault_probe_outputs(save_dir1,soidx)
    else:
        outputs1,dep1,params1 = load_short_fault_probe_outputs(save_dir1,0)

if 'v6_ab2_Dc2' in save_dir1:
    Vths = 1e-1
    intv = 0.15
elif 'perturb_stress' in save_dir1:
    Vths = 2e-1
    intv = 0.15
else:
    Vths = 1e-2
    intv = 0.
Vlb = 0
dt_interm = 0
cuttime = 0
rths = 10
dt_creep = 2*ch.yr2sec
dt_coseismic = 0.5

if os.path.exists('%s/cumslip_outputs_Vths_%1.0e_srvar_%03d_rths_%d_tcreep_%d_tseis_%02d.npy'%(save_dir1,Vths,intv*100,rths,dt_creep/ch.yr2sec,dt_coseismic*10)):
    cumslip_outputs = np.load('%s/cumslip_outputs_Vths_%1.0e_srvar_%03d_rths_%d_tcreep_%d_tseis_%02d.npy'%(save_dir1,Vths,intv*100,rths,dt_creep/ch.yr2sec,dt_coseismic*10),allow_pickle=True)
    spin_up_idx = np.load('%s/spin_up_idx_Vths_%1.0e_srvar_%03d_rths_%d_tcreep_%d_tseis_%02d.npy'%(save_dir1,Vths,intv*100,rths,dt_creep/ch.yr2sec,dt_coseismic*10))
    tstart,tend,evdep = cumslip_outputs[0][0],cumslip_outputs[0][1],cumslip_outputs[1][1]
    rupture_length,av_slip,system_wide,partial_rupture,event_cluster,lead_fs,major_pr,minor_pr = analyze_events(cumslip_outputs,rths)
    idx = system_wide[system_wide>=spin_up_idx][target_eventid]
    print('Loaded pre-saved cumslip outputs')
else:
    print('No pre-saved cumslip outputs')
print('======== Event details without perturbation ========')
print('Event %d'%(idx))
print('Event depth without perturbation: %1.2f'%(evdep[idx]))

if 'save_dir3' in locals(): 
    cumslip_outputs3 = compute_cumslip(outputs3,dep3,cuttime,Vlb,Vths,dt_creep,dt_coseismic,dt_interm,intv)
    tstart3,tend3,evdep3 = cumslip_outputs3[0][0],cumslip_outputs3[0][1],cumslip_outputs3[1][1]
    system_wide3 = analyze_events(cumslip_outputs3,rths)[2]
    print('======== Event details with perturbation ========')
    print('evdep3:',evdep3)
    print('system_wide3:',system_wide3)
    print('Event depth with perturbation:',evdep3[system_wide3])

# -----
outputs1[:,:,0] = outputs1[:,:,0] - tstart[idx]
outputs3[:,:,0] = outputs3[:,:,0] - tstart[idx]
lag = tstart[idx]-tstart3[system_wide3]
time_tag = "advance" if lag > 0 else "delay"

def get_var(outputs,dep,target_depth,target_var,plot_in_sec,abs_on):
    if target_depth == None:
        print('Mode: Maximum along fault')
        indx = None
    else:
        indx = np.argmin(abs(abs(dep) - abs(target_depth)))
        print('Depth = %1.2f [km]'%abs(dep[indx]))

    if target_var == 'state':
        var_idx,ylab,fign = 1,'State Variable','state'
    elif target_var == 'slip':
        var_idx,ylab,fign = 2,'Cumulative Slip [m]','cumslip'
    elif target_var == 'shearT':
        var_idx,ylab,fign = 3,'Shear Stress [MPa]','shearT'
    elif target_var == 'sliprate':
        var_idx,ylab,fign = 4,'log$_{10}$(Slip Rate [m/s])','sliprate'
    elif target_var == 'normalT':
        var_idx,ylab,fign = 5,'Normal Stress [MPa]','normalT'

    if target_depth == None:
        if var_idx == 4:
            var = np.log10(np.max(np.array(outputs[:,:,var_idx]),axis=0))
        else:
            var = np.max(np.array(outputs[:,:,var_idx]),axis=0)
        ylab = 'Peak ' + ylab
    else:
        if var_idx == 4:
            if np.all(np.array(outputs[indx])[:,var_idx]>0):
                var = np.log10(np.array(outputs[indx])[:,var_idx])
            else:
                print('Negative slip rate - taking absolute')
                var = np.log10(abs(np.array(outputs[indx])[:,var_idx]))
        else:
            var = np.array(outputs[indx])[:,var_idx]
    if abs_on:
        var = abs(var)
        ylab = 'Absolute ' + ylab
    if plot_in_sec:
        time = np.array(outputs[0])[:,0]
        xlab = 'Time [s]'
    else:
        time = np.array(outputs[0])[:,0]/sc.yr2sec
        xlab = 'Time [yrs]'
    return time,var,xlab,ylab,fign,indx

def fout_time_max(save_dir,outputs,target_var,plot_in_sec,toff=0,ls='-',col='k',lab='',abs_on=False,save_on=True):
    time,var,xlab,ylab,fign,_ = get_var(outputs,None,None,target_var,plot_in_sec,abs_on)
    if abs(toff) > 0: time += toff
    plt.plot(time,var,color=col, lw=2.5,label=lab,linestyle=ls)
    plt.xlabel(xlab,fontsize=17)
    plt.ylabel(ylab,fontsize=17)
    plt.tight_layout()
    if save_on:
        plt.savefig('%s/%s.png'%(save_dir,fign))

plt.figure(figsize=(15,6))
tvar = 'sliprate'
inc1 = 1e3
inc2 = 5e4
i1 = np.where(np.logical_and(outputs1[0,:,0]>=outputs3[0,0,0]-inc1,outputs1[0,:,0]<=outputs3[0,-1,0]+inc2))[0]
fout_time_max(save_dir1,outputs1[:,i1,:],tvar,lab='Unperturbed',plot_in_sec=True,col='k',save_on=False)
fout_time_max(save_dir3,outputs3[:,1:,:],tvar,lab='Perturbed',plot_in_sec=True,col=mp.myblue,save_on=False)
xl = [-10*3600,4*3600]
yl = plt.gca().get_ylim()
plt.vlines(x=0,ymin=yl[0],ymax=yl[1],lw=2.5,colors='0.62',linestyles='--',zorder=0)
plt.text((xl[1]-xl[0])*0.01,-yl[1]*3.5,'Unperturbed event time',fontsize=13,color='0.62',fontweight='bold')
plt.vlines(x=(tstart3[system_wide3]-tstart[idx]),ymin=yl[0],ymax=yl[1],lw=2.5,colors=mp.mynavy,linestyles='--',zorder=0)
plt.text((tstart3[system_wide3]-tstart[idx])+(xl[1]-xl[0])*0.01,-yl[1]*3.5,'Perturbed event time',fontsize=13,color=mp.mynavy,fontweight='bold')
if lag < 3600:
    plt.text(xl[1]-(xl[1]-xl[0])*0.025,yl[1]*0.75,'Time %s of %d s'%(time_tag,np.round(lag)),fontsize=20,color='k',fontweight='bold',ha='right',va='top')
    plt.xlabel('Time relative to the unperturbed event [s]',fontsize=17)
else:
    plt.text(xl[1]-(xl[1]-xl[0])*0.025,yl[1]*0.75,'Time %s of %d hr'%(time_tag,np.round(lag/3600)),fontsize=20,color='k',fontweight='bold',ha='right',va='top')
    xt = np.linspace(-3600*10,3600*4,8)
    xtl = ['%d'%(ixt/3600) for ixt in xt]
    plt.xticks(ticks=xt,labels=xtl)
    plt.xlabel('Time relative to the unperturbed event [hr]',fontsize=17)
plt.ylim(-yl[1]*6.5,yl[1])
plt.xlim(xl)
plt.legend(fontsize=15,loc='upper left')
plt.ylabel('log$_{10}$(Peak Slip Rate [m/s])',fontsize=17)
plt.grid(True,alpha=0.5)
plt.savefig('%s/pub_trigger_response.png'%(save_dir3),dpi=350)
plt.show()