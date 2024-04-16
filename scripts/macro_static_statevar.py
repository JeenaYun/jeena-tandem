import numpy as np
import setup_shortcut
import change_params
from read_outputs import *
sc = setup_shortcut.setups()
ch = change_params.variate()

save_on = 0
# ---
import matplotlib.pylab as plt
import myplots
mp = myplots.Figpref()
plt.rcParams['font.size'] = '15'

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
            # var = np.max(np.log10(np.array(outputs[:,:,var_idx])),axis=0)
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

def fout_time(outputs,dep,target_depth,target_var,plot_in_sec,ls='-',col='k',lab='',abs_on=False,zo=1):
    time,var,xlab,ylab,fign,indx = get_var(outputs,dep,target_depth,target_var,plot_in_sec,abs_on)
    plt.plot(time,var,color=col, lw=2.5,label=lab,linestyle=ls,zorder=zo)
    plt.xlabel(xlab,fontsize=17)
    plt.ylabel(ylab,fontsize=17)
    if target_depth < 1e-1:
        tstring = 'surface'
    else:
        tstring = '%1.2f [km]'%abs(dep[indx])
    return tstring

# ---
from cumslip_compute import analyze_events
cumslip_dir = '/export/dump/jyun/perturb_stress/reference'
vmin,vmax,Vths,intv,Vlb,dt_interm,cuttime,rths,dt_creep,dt_coseismic = sc.base_event_criteria(cumslip_dir)
if os.path.exists('%s/cumslip_outputs_Vths_%1.0e_srvar_%03d_rths_%d_tcreep_%d_tseis_%02d.npy'%(cumslip_dir,Vths,intv*100,rths,dt_creep/ch.yr2sec,dt_coseismic*10)):
    cumslip_outputs,spin_up_idx = load_cumslip_outputs(cumslip_dir)
    tstart,tend,evdep = cumslip_outputs[0][0],cumslip_outputs[0][1],cumslip_outputs[1][1]
    rupture_length,av_slip,system_wide,partial_rupture,event_cluster,lead_fs,major_pr,minor_pr = analyze_events(cumslip_outputs,rths)

# ---
save_dir = 'perturb_stress/seissol_outputs'
mu = 0.4
target_eventids = [31,31]
model_ns = ['dipping_slow','vert_slow']
receivef_strikes = [350,340]

for i in range(len(target_eventids)):
    target_eventid = target_eventids[i]
    model_n = model_ns[i]
    receivef_strike = receivef_strikes[i]
    model_code = sc.model_code(model_n)
    save_dir2 = '/export/dump/jyun/'+'perturb_stress/pert%d_%s%d_stress_dep'%(target_eventid,sc.model_code(model_n),receivef_strike)
    save_dir4 = '/export/dump/jyun/'+'perturb_stress/pert%d_%s%d'%(target_eventid,sc.model_code(model_n),receivef_strike)

    if 'save_dir2' in locals(): outputs2,dep2,params2 = load_fault_probe_outputs(save_dir2)
    if 'save_dir4' in locals(): outputs4,dep4,params4 = load_fault_probe_outputs(save_dir4)

    idx = system_wide[system_wide>=spin_up_idx][target_eventid]

    plt.figure(figsize=(10,6))
    tdep,tvar = evdep[idx],'state'
    tstring = fout_time(outputs4[:,1:,:],dep4,tdep,tvar,col='k',plot_in_sec=True,lab='Basic aging law',ls='--')
    fout_time(outputs2[:,1:,:],dep2,tdep,tvar,col=mp.mypink,plot_in_sec=True,lab='Stress-dependent aging law',zo=3)
    plt.legend(fontsize=15,loc='lower right')
    plt.title('Event %d; %s%d; Depth = %s'%(idx,model_code,receivef_strike,tstring),fontsize=20,fontweight = 'bold')
    plt.tight_layout()
    plt.savefig('/home/jyun/Tandem/perturb_stress/ev%d_%s%d_static_state.png'%(idx,model_code,receivef_strike))
