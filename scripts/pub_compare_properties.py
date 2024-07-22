'''
(Publication) Compare some properties during perturbation
By Jeena Yun
Last modification: 2024.04.27.
'''
import numpy as np
import pandas as pd
from glob import glob
from perturb_tools import PERTURB
import matplotlib.pylab as plt
import myplots
from string import ascii_lowercase
mp = myplots.Figpref()
plt.rcParams['font.size'] = '14'

save_on = 0
print_on = 0
delay_model = False
plot_corr = 1
law = 'aging'
abs_time_diff = False
if abs_time_diff: print('Absolute time mode')
axislab_fs = 15
figlab_fs = 17
txt_fs = 14
symbol_size=125
symbol_lw = 1

tvars = ['max_dCFS','static_dCFS','slip','sliprate','integrated_work']
colset = {'max_dCFS':mp.mylilac,'static_dCFS':'lemonchiffon','slip':mp.pptlightgreen,'sliprate':mp.mylightblue,'integrated_work':mp.mypalepink}
colset_delay = {'max_dCFS':mp.mydarkviolet,'static_dCFS':mp.pptorange,'slip':mp.myolive,'sliprate':mp.myblue,'integrated_work':mp.myburgundy}
# colset = {'max_dCFS':mp.pptlightorange,'min_dCFS':mp.mylightblue,'static_dCFS':mp.myashblue,\
#     'max_shearT':mp.mylilac,'min_shearT':'lemonchiffon','static_shearT':mp.pptlightgreen,\
#         'slip':'0.8','sliprate':mp.mylightmint,'integrated_work':mp.mypalepink}
# colset_delay = {'max_dCFS':mp.myorange,'min_dCFS':mp.myblue,'static_dCFS':mp.myteal,\
#     'max_shearT':mp.mydarkviolet,'min_shearT':mp.pptorange,'static_shearT':mp.mygreen,\
#         'slip':'0.3','sliprate':mp.mymint,'integrated_work':mp.myburgundy}

def compute_indicators(model,target_var,base_model):
    if not np.all(np.argsort(abs(model.dep)) == np.arange(len(model.dep))):
        print('Need sorting!!')
        model.dep = np.sort(model.dep)
    if not np.all(np.argsort(abs(model.dep)) == np.arange(len(model.dep))):
        raise SyntaxError('Need sorting!!')
    if target_var == 'work':
        shearT = abs(model.variables['shearT'].data)
        cumslip = model.variables['slip'].data[:,1:]
    elif target_var != 'dCFS': 
        var = model.variables[target_var].data

    if target_var == 'sliprate':
        value = np.log10(np.max(var))
    elif target_var == 'slip':
        value = max(var[:,-1]-var[:,0])*1e3
    elif target_var  in ['state','shearT','dCFS']:
        cumslip = model.variables['slip'].data[:,1:]
        netslip = np.array([cumslip[k,-1]-cumslip[k,0] for k in range(len(model.dep))])
        idx = base_model.system_wide[base_model.system_wide>=base_model.spin_up_idx][model.target_eventid]
        if len(np.where(base_model.system_wide == idx)[0]) == 1:
            lead_fs_idx = base_model.lead_fs[np.where(base_model.system_wide == idx)[0][0]]
        # target_depth = base_model.evdep[idx] # hypocenter depth location
        # target_depth = base_model.evdep[lead_fs_idx] # depth of leading foreshock
        # di = np.argmin(abs(abs(model.dep) - abs(target_depth)))
        di = np.argmax(netslip) # depth of max. slip
        target_depth = model.dep[di]
        if target_var == 'shearT': var = -var
        elif target_var == 'dCFS':
            var = model.get_output_dCFS(target_depth,print_on=False)[0]
        if mode == 'max':
            if target_var == 'dCFS': value = np.max(var)  # Peak, at hypocenter depth
            else:
                value = np.max(var[di,:]) - var[di,0]  # Peak, at hypocenter depth
                # value = np.max(var)  # Peak, globally
        elif mode == 'min':
            if target_var == 'dCFS': value = np.min(var)  # Peak neg., at hypocenter depth
            else:  
                value = np.min(var[di,:]) - var[di,0]  # Peak neg., at hypocenter depth
                # value = np.min(var)  # Peak, globally
        elif mode == 'static':
            if target_var == 'dCFS': value = np.mean(var[-10:])  # Peak neg., at hypocenter depth
            else: value = np.mean(var[di,-10:]) - var[di,0]   # Static, at hypocenter depth
    elif target_var == 'work':
        from scipy import integrate
        G = []
        for di in range(len(model.dep)):
            target_depth = model.dep[di]
            slip = cumslip[di,:] - cumslip[di,0]
            ts = -model.get_output_dCFS(target_depth,print_on=False)[-1]
            x = slip[:400]
            y = ts[:400]*1e6
            area = integrate.simpson(y,x)
            G.append(area)
        if mode == 'integrated': 
            value = integrate.simpson(G,-model.dep*1e3)
        elif mode == 'average':
            value = np.mean(G)
        elif mode == 'hypo':
            idx = base_model.system_wide[base_model.system_wide>=base_model.spin_up_idx][model.target_eventid]
            target_depth = base_model.evdep[idx]
            di = np.argmin(abs(abs(model.dep) - abs(target_depth)))
            # value = G[di]
            inc = 500
            lb,ub = di-inc,di+inc+1
            if di-inc < 0: lb = 0 #; print('di = %d; di-inc < 0'%(di))
            if di+inc+1 >= len(G): ub = len(G)-1 #; print('di = %d; di+inc+1 >= %d'%(di,len(G)))
            value = integrate.simpson(G[lb:ub],-model.dep[lb:ub]*1e3)
    else:
        raise SyntaxError('No definition for the target variable')
    return value

# --------- Load triggring responses
if law == 'aging': resp = pd.read_csv('perturb_stress/triggering_response_aging.csv',skiprows=1)
elif law == 'LnDaging': resp = pd.read_csv('perturb_stress/triggering_response_LnDaging.csv',skiprows=1)
target_IDs = resp['ID']
model_names = resp['Model\n Name']
strikes = resp['Strike\n [˚]']
triggering_responses = resp['Time \n Difference [h]']
if abs_time_diff: triggering_responses = abs(triggering_responses)

base_model = PERTURB('reference')
base_model.load_events()

dirs = glob('/export/dump/jyun/perturb_stress/pert*')
c = []

panel_margin = 0.08
panel_margin2 = 0.13
left_margin = 0.13
right_margin = 0.0
bottom_margin = 0.1
top_margin = 0.05
width = (1-panel_margin*2-right_margin-left_margin)/3
height = (1-panel_margin2-top_margin-bottom_margin)/2
margin1 = (1-width*2-panel_margin)/2
margin2 = (1-width*3-panel_margin*2)/2

fig, ax = plt.subplots(figsize=(12.2,8.5))
ax1 = fig.add_axes([margin1,bottom_margin+height+panel_margin2,width,height])
ax2 = fig.add_axes([margin1+width+panel_margin,bottom_margin+height+panel_margin2,width,height])
ax3 = fig.add_axes([margin2,bottom_margin,width,height])
ax4 = fig.add_axes([margin2+width+panel_margin,bottom_margin,width,height])
ax5 = fig.add_axes([margin2+width*2+panel_margin*2,bottom_margin,width,height])
ax.set_axis_off()

axset = {'max_dCFS':ax1,'static_dCFS':ax2,'slip':ax3,'sliprate':ax4,'integrated_work':ax5}
for kk in range(len(tvars)):
    target_var = tvars[kk]
    col = colset[target_var]
    col_delay = colset_delay[target_var]
    fign = target_var
    if abs_time_diff: fign += '_abs'
    mode = ''
    quant = 1e6*np.ones(triggering_responses.shape)
    print(target_var)
    if 'state' in target_var or 'shearT' in target_var or 'dCFS' in target_var or 'work' in target_var:
        if len(target_var.split('_')) > 1:
            mode = target_var.split('_')[0]
        target_var = target_var.replace(mode+'_','')

    for folders in np.array(dirs):
        branch_n = folders.split('/export/dump/jyun/perturb_stress/')[-1]
        if 'stress_dep' in branch_n or 'sliplaw' in branch_n or 'lowres' in branch_n or 'X' in branch_n or 'diffwavelength' in branch_n or 'h' in branch_n:
        # if 'pert18_vs340_lowres_spinup_aginglaw_reference' == branch_n:
        #     delay_model = True
        #     delay = 5.9550
        # elif 'stress_dep' in branch_n or 'sliplaw' in branch_n or 'lowres' in branch_n or 'X' in branch_n or 'diffwavelength' in branch_n or 'h' in branch_n:
            if print_on: print('%s: invalid names - skip'%(branch_n))
            continue

        model = PERTURB(branch_n)

        if not delay_model:
            crit1 = np.where(model_names == model.seissol_model_n)[0]
            crit2 = np.where(strikes == model.receivef_strike)[0]
            crit3 = np.where(target_IDs == model.target_eventid)[0]

            csv_idx = np.intersect1d(np.intersect1d(crit1,crit2),crit3)
            if len(csv_idx) == 0:
                if print_on: print('No matching data in the csv file for "%s"'%(branch_n))
                continue
            elif len(csv_idx) > 1:
                if print_on: print('More than one matching data in the csv file for "%s":'%(branch_n),csv_idx)
                continue
            csv_idx = csv_idx[0]

            model.load_output(print_on=False)
            quant[csv_idx] = compute_indicators(model,target_var,base_model)
            # print(branch_n,'(%d)'%(csv_idx),'->',quant[csv_idx])
        else:
            model.load_output(print_on=False)
            delay_quant = compute_indicators(model,target_var,base_model)
            # print(branch_n,'->',delay_quant)
            delay_model = False

    # ---------- Compute correlation coefficient, R
    X = np.stack((quant,-triggering_responses), axis=0)
    R = np.cov(X)[0,1]/(np.std(quant)*np.std(-triggering_responses))
    # X = np.stack((quant,triggering_responses), axis=0)
    # R = np.cov(X)[0,1]/(np.std(quant)*np.std(triggering_responses))

    # ---------- Plot
    if 'delay_quant' not in locals():
        axset[fign].scatter(quant,-triggering_responses,s=symbol_size,fc=col,ec='k',lw=symbol_lw,marker='s',zorder=3)
    else:
        axset[fign].scatter(quant,-triggering_responses,s=symbol_size,fc=col,ec='k',lw=symbol_lw,marker='s',zorder=3)
        axset[fign].scatter(delay_quant,-delay,s=symbol_size,fc=col_delay,ec='k',lw=symbol_lw,marker='^',zorder=3)
    if mode in ['static','min','max'] and target_var != 'dCFS':
        label = model.variables[target_var].label.split(' [')[0]
        unit = '[%s]'%(model.variables[target_var].label.split('[')[-1].split(']')[0])
    # if 'delay_quant' not in locals() and target_var in ['slip','work']: axset[fign].set_xscale('log')
    if target_var == 'sliprate':
        axset[fign].set_xlabel(r'$\log_{10}$(Peak '+model.variables[target_var].label+')',fontsize=axislab_fs)
    elif mode == 'static':
        if target_var == 'dCFS': axset[fign].set_xlabel(r'Static $\Delta$CFS [MPa]',fontsize=axislab_fs)
        else: axset[fign].set_xlabel('Static '+label+' Change '+unit,fontsize=axislab_fs)
    elif mode == 'min':
        if target_var == 'dCFS': axset[fign].set_xlabel(r'Peak Negative Dynamic $\Delta$CFS [MPa]',fontsize=axislab_fs)
        else: axset[fign].set_xlabel('Peak Negative '+label+' Change '+unit,fontsize=axislab_fs)
    elif target_var == 'work':
        if mode in 'integrated':
            axset[fign].set_xlabel('Work per Distance [J/m]',fontsize=axislab_fs)
        elif mode == 'average':
            axset[fign].set_xlabel('Average Work Density [J/m$^2$]',fontsize=axislab_fs)
        elif mode == 'hypo':
            axset[fign].set_xlabel('Work Density at Hypocenter [J/m$^2$]',fontsize=axislab_fs)
    elif target_var == 'slip': axset[fign].set_xlabel('Peak Slip [mm]',fontsize=axislab_fs)
    else:
        if target_var == 'dCFS': axset[fign].set_xlabel(r'Peak Dynamic $\Delta$CFS [MPa]',fontsize=axislab_fs)
        else: axset[fign].set_xlabel('Peak '+label+' Change '+unit,fontsize=axislab_fs)
    if abs_time_diff: 
        axset[fign].set_ylabel('$|\Delta t|$ [h]',fontsize=axislab_fs)
    else:
        axset[fign].set_ylabel('$\Delta t$ [h]',fontsize=axislab_fs)
        # axset[fign].set_ylabel('Mainshock Time difference ($\Delta t$) [h]',fontsize=axislab_fs)
    xl = axset[fign].get_xlim()
    yl = axset[fign].get_ylim()
    axset[fign].text(xl[0]-(xl[1]-xl[0])*0.25,yl[1]+(yl[1]-yl[0])*0.05,'(%s)'%(ascii_lowercase[kk]),fontsize=figlab_fs,fontweight='bold')
    if plot_corr: axset[fign].text(xl[1]-(xl[1]-xl[0])*0.05,yl[0]+(yl[1]-yl[0])*0.02,'R = %1.2f'%(R),fontsize=txt_fs,color=mp.myburgundy,ha='right',va='bottom')
    # if plot_corr: axset[fign].text(xl[1]-(xl[1]-xl[0])*0.05,yl[1]-(yl[1]-yl[0])*0.05,'R = %1.2f'%(R),fontsize=txt_fs,color=mp.myburgundy,ha='right',va='top')
    axset[fign].grid(True,alpha=0.5)
    
plt.tight_layout()
if save_on:
    if 'delay_quant' in locals():
        # plt.savefig('/export/dump/jyun/perturb_stress/plots/time_advance_vs_delay/trigger_response_alltogether.png',bbox_inches='tight',dpi=350)
        plt.savefig('/export/dump/jyun/perturb_stress/plots/time_advance_vs_delay/trigger_response_at_max_slip.png',bbox_inches='tight',dpi=350)
    else:
        # plt.savefig('/export/dump/jyun/perturb_stress/plots/basic_aging_law_summary/trigger_response_alltogether.png',bbox_inches='tight',dpi=350)
        plt.savefig('/export/dump/jyun/perturb_stress/plots/basic_aging_law_summary/trigger_response_at_max_slip.png',bbox_inches='tight',dpi=350)