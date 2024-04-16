
import numpy as np
from glob import glob
from perturb_tools import PERTURB
import matplotlib.pylab as plt
import myplots
mp = myplots.Figpref()
plt.rcParams['font.size'] = '15'

def plot_all_events(tstart,evdep,system_wide,partial_rupture,lead_fs):
    plt.scatter(tstart[partial_rupture],evdep[partial_rupture],70,ec='k',fc=mp.mylightblue,lw=1,marker='d',zorder=3,label='Partial rupture events')
    plt.scatter(tstart[lead_fs],evdep[lead_fs],70,ec='k',fc=mp.mydarkviolet,lw=1,marker='d',zorder=3,label='Leading foreshocks')
    plt.scatter(tstart[system_wide],evdep[system_wide],150,ec='k',fc=mp.mydarkviolet,lw=1,marker='*',zorder=3,label='System-size events')
    xl = ax.get_xlim()
    plt.hlines(y=2,xmin=0,xmax=xl[1],linestyles='--',color='0.62',lw=1.5)
    plt.hlines(y=12,xmin=0,xmax=xl[1],linestyles='--',color='0.62',lw=1.5)
    plt.ylim(0,24)
    ax.invert_yaxis()
    plt.xlabel('Event Time [s]',fontsize=17)
    plt.ylabel('Depth [km]',fontsize=17)
    plt.grid(True,alpha=0.5,which='both')

ref_ref = PERTURB('reference')
ref_ref.load_events()
ref_endmem = PERTURB('diffwavelength')
ref_endmem.load_events()
ref_aging = PERTURB('lowres_spinup_aginglaw_reference')
ref_aging.load_events()
ref_slip = PERTURB('lowres_spinup_sliplaw_reference')
ref_slip.load_events()
print()

dirs = glob('/export/dump/jyun/perturb_stress/after_pert*')
tid,ev8 = [],0
# for folders in ['/export/dump/jyun/perturb_stress/after_pert56_vs340']:
for folders in np.array(dirs):
    fign = ''
    branch_n = folders.split('/export/dump/jyun/perturb_stress/')[-1]
    if 'stress_dep' in branch_n or 'X' in branch_n or 'h' in branch_n:
        # print('%s: invalid names - skip'%(branch_n))
        continue

    model = PERTURB(branch_n)
    if model.target_eventid in tid and not (model.target_eventid == 8 and ev8 < 2):
        continue
    elif model.target_eventid == 18 and model.model_tag == 'lowres_spinup_aginglaw_reference' and model.seissol_model_n == 'dipping_slow':
        continue
    print('Event %d from %s'%(model.target_eventid,branch_n))
    tid.append(model.target_eventid)
    if model.target_eventid == 8: 
        ev8 += 1
        fign = '_'+model.model_tag
    model.load_output()
    if model.model_tag == 'reference':
        print('reference')
        ref = ref_ref
    elif model.model_tag == 'diffwavelength':
        print('diffwavelength')
        ref = ref_endmem
    elif model.model_tag == 'lowres_spinup_aginglaw_reference':
        print('lowres_spinup_aginglaw_reference')
        ref = ref_aging
    elif model.model_tag == 'lowres_spinup_sliplaw_reference':
        print('lowres_spinup_sliplaw_reference')
        ref = ref_slip
    
    model.load_events(compute_on=True,save_on=False,print_on=False)
    ref.get_idx(model.target_eventid)

    # ----- 
    fig,ax=plt.subplots(figsize=(8,6))
    plot_all_events(ref.tstart,ref.evdep,ref.system_wide,ref.partial_rupture,ref.lead_fs)
    plt.vlines(x=ref.tstart[ref.idx]-16.2*3600,ymin=0,ymax=24,color=mp.mypink,linestyles='--',lw=2)
    plt.text(ref.tstart[ref.idx]-16.2*3600-1e4,15,'Perturbation Start',color=mp.mypink,fontsize=13,ha='right',va='bottom',fontweight='bold')
    plt.vlines(x=model.tstart[model.system_wide],ymin=0,ymax=24,color=mp.mynavy,linestyles='--',lw=2)
    plt.text(model.tstart[model.system_wide]-1e4,13.5,'Perturbed Event Time',color=mp.mynavy,fontsize=13,ha='right',va='bottom',fontweight='bold')
    if model.target_eventid == 18 and model.model_tag == 'lowres_spinup_aginglaw_reference':
        closest_leadfs = ref.lead_fs[np.argmin(abs(ref.tstart[ref.lead_fs]-ref.tstart[ref.idx]-16.2*3600))]+1
    else:
        closest_leadfs = ref.lead_fs[np.argmin(abs(ref.tstart[ref.lead_fs]-ref.tstart[ref.idx]-16.2*3600))]
    print(closest_leadfs)
    xmin,xmax = ref.tstart[closest_leadfs]-1e5,model.tend[model.system_wide[-1]]+1e5
    for k in range(len(ref.tstart)):
        if ref.tstart[k] >= xmin and ref.tstart[k] <= xmax:
            plt.text(ref.tstart[k],ref.evdep[k]-0.2,'%d'%(k),color='k',fontsize=13,ha='right',va='bottom')
    plt.legend(fontsize=13,loc='lower right')
    plt.xlim(xmin,xmax)
    plt.tight_layout()
    plt.savefig('/export/dump/jyun/perturb_stress/plots/perturbation_loc/event%d%s.png'%(model.target_eventid,fign))
    plt.show()
    print()