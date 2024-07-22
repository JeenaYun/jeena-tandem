'''
(Publication) Generate combined slip rate images for each reference models
By Jeena Yun
Last modification: 2024.04.29.
'''
import numpy as np
import matplotlib.pylab as plt
from pub_faultoutputs_image import *
import myplots
import setup_shortcut
from read_outputs import load_fault_probe_outputs,load_cumslip_outputs
mp = myplots.Figpref()
sc = setup_shortcut.setups()

save_on = 1
testmode = False

horz_size = 12
vert_size = 12

image = 'sliprate'
yr2sec = 60*60*24*365

plt.rcParams['font.size'] = '12'
fig = plt.figure(figsize=(horz_size,vert_size),layout='constrained')

vmin,vmax,Vths,intv,Vlb,dt_interm,cuttime,rths,dt_creep,dt_coseismic = sc.base_event_criteria('/export/dump/jyun/perturb_stress/reference',image)

# --------- 1. Aging law, most complex
if not testmode:
    prefix = 'perturb_stress/reference'
    save_dir = '/export/dump/jyun/'+prefix
    outputs,dep,params = load_fault_probe_outputs(save_dir)
    cumslip_outputs,_ = load_cumslip_outputs(save_dir,image)
    zf = [800000,950000]

plt.subplot(3, 1, 1)
if not testmode:
    fout_image(image,outputs,dep,params,cumslip_outputs,save_dir,prefix,rths,vmin,vmax,Vths,zf,plot_in_timestep=True,plot_in_sec=False,cb_off=True,publish=True,no_scatter=False,save_on=False)
    plt.legend(fontsize=9,loc='lower right')
    xl = plt.xlim()
    plt.text(-xl[1]*0.08,-1.25,'(a)',color='k',fontsize=17,fontweight='bold')
    plt.title(r'Aging Law ($\bf\overline{D_{RS}}$ = 2 mm)',fontsize=15,fontweight='bold')
    plt.xlim([0,150000])

# --------- 2. Slip law, less complex
prefix = 'perturb_stress/lowres_spinup_sliplaw_reference'
save_dir = '/export/dump/jyun/'+prefix
outputs,dep,params = load_fault_probe_outputs(save_dir)
cumslip_outputs,_ = load_cumslip_outputs(save_dir,image)
zf = [5500,30000]

plt.subplot(3, 1, 2)
im = fout_image(image,outputs,dep,params,cumslip_outputs,save_dir,prefix,rths,vmin,vmax,Vths,zf,plot_in_timestep=True,plot_in_sec=False,cb_off=True,publish=True,no_scatter=False,save_on=False)
xl = plt.xlim()
plt.text(-xl[1]*0.08,-1.25,'(b)',color='k',fontsize=17,fontweight='bold')
plt.title(r'Slip Law ($\bf\overline{D_{RS}}$ = 10 mm)',fontsize=13,fontweight='bold')
plt.xlim([0,22000])

# --------- 3. Aging law, less complex
if not testmode:
    prefix = 'perturb_stress/lowres_spinup_aginglaw_reference'
    save_dir = '/export/dump/jyun/'+prefix
    outputs,dep,params = load_fault_probe_outputs(save_dir)
    cumslip_outputs,_ = load_cumslip_outputs(save_dir,image)
    zf = [20000,120000]
    
ax2=plt.subplot(3, 1, 3)
if not testmode:
    im = fout_image(image,outputs,dep,params,cumslip_outputs,save_dir,prefix,rths,vmin,vmax,Vths,zf,plot_in_timestep=True,plot_in_sec=False,cb_off=True,publish=True,no_scatter=False,save_on=False)
    xl = ax2.get_xlim()
    plt.text(-xl[1]*0.08,-1.25,'(c)',color='k',fontsize=17,fontweight='bold')
    plt.title(r'Aging Law ($\bf\overline{D_{RS}}$ = 10 mm)',fontsize=13,fontweight='bold')
    plt.xlim(xl)

# --------- 4. Add colorbar
cb = fig.colorbar(im,ax=ax2,location='bottom',shrink=0.5,extend='both',orientation='horizontal')
cb.ax.set_title('Slip Rate [m/s]',fontsize=13)

if save_on: 
    if not testmode:
        plt.savefig('/export/dump/jyun/perturb_stress/plots/all_reference_models.png',dpi=350)
    else:
        plt.savefig('/home/jyun/Tandem/test.png')
print('saving png done')
