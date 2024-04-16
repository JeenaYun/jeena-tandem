'''
Compare some properties during perturbation
By Jeena Yun
Last modification: 2024.04.11.
'''
import numpy as np
import pandas as pd
from glob import glob
from perturb_tools import PERTURB
import matplotlib.pylab as plt
import myplots
mp = myplots.Figpref()
plt.rcParams['font.size'] = '15'

save_on = 1
print_on = 0
delay_model = False
law = 'aging'
abs_time_diff = True
if abs_time_diff: print('Absolute time mode')

# tvars = ['static_shearT']
tvars = ['max_dCFS','min_dCFS','static_dCFS','max_shearT','min_shearT','static_shearT','slip','sliprate','integrated_work']
colset = {'max_dCFS':mp.pptlightorange,'min_dCFS':mp.mylightblue,'static_dCFS':mp.myashblue,\
    'max_shearT':mp.mylilac,'min_shearT':'lemonchiffon','static_shearT':mp.pptlightgreen,\
        'slip':'0.8','sliprate':mp.mylightmint,'integrated_work':mp.mypalepink}
colset_delay = {'max_dCFS':mp.myorange,'min_dCFS':mp.myblue,'static_dCFS':mp.myteal,\
    'max_shearT':mp.mydarkviolet,'min_shearT':mp.pptorange,'static_shearT':mp.mygreen,\
        'slip':'0.3','sliprate':mp.mymint,'integrated_work':mp.myburgundy}

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
        value = max(var[:,-1]-var[:,0])
    elif target_var  in ['state','shearT','dCFS']:
        idx = base_model.system_wide[base_model.system_wide>=base_model.spin_up_idx][model.target_eventid]
        target_depth = base_model.evdep[idx]
        di = np.argmin(abs(abs(model.dep) - abs(target_depth)))
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
        # if 'stress_dep' in branch_n or 'sliplaw' in branch_n or 'lowres' in branch_n or 'X' in branch_n or 'diffwavelength' in branch_n or 'h' in branch_n:
        if 'pert18_vs340_lowres_spinup_aginglaw_reference' == branch_n:
            delay_model = True
            delay = 5.9550
        elif 'stress_dep' in branch_n or 'sliplaw' in branch_n or 'lowres' in branch_n or 'X' in branch_n or 'diffwavelength' in branch_n or 'h' in branch_n:
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

    # ----------
    if save_on: 
        plt.figure(figsize=(7,6))
        if 'delay_quant' not in locals():
            plt.scatter(quant,triggering_responses,175,fc=col,ec='k',lw=1.5,marker='s',zorder=3)
        else:
            plt.scatter(quant,triggering_responses,175,fc=col,ec='k',lw=1.5,marker='s',zorder=3)
            plt.scatter(delay_quant,delay,175,fc=col_delay,ec='k',lw=1.5,marker='^',zorder=3)
        if mode in ['static','min','max'] and target_var != 'dCFS':
            label = model.variables[target_var].label.split(' [')[0]
            unit = '[%s]'%(model.variables[target_var].label.split('[')[-1].split(']')[0])
        if 'delay_quant' not in locals() and target_var in ['slip','work']: plt.xscale('log')
        if target_var == 'sliprate':
            plt.xlabel(r'$\log_{10}$(Peak '+model.variables[target_var].label+')',fontsize=17)
        elif mode == 'static':
            if target_var == 'dCFS': plt.xlabel('Static dCFS [MPa]',fontsize=17)
            else: plt.xlabel('Static '+label+' Change '+unit,fontsize=17)
        elif mode == 'min':
            if target_var == 'dCFS': plt.xlabel('Min. dCFS [MPa]',fontsize=17)
            else: plt.xlabel('Peak Negative '+label+' Change '+unit,fontsize=17)
        elif target_var == 'work':
            if mode in 'integrated':
                plt.xlabel('Work per Distance [J/m]',fontsize=17)
            elif mode == 'average':
                plt.xlabel('Average Work Density [J/m$^2$]',fontsize=17)
            elif mode == 'hypo':
                plt.xlabel('Work Density at Hypocenter [J/m$^2$]',fontsize=17)
        else:
            if target_var == 'dCFS': plt.xlabel('Max. dCFS [MPa]',fontsize=17)
            elif target_var == 'slip': plt.xlabel('Max. '+model.variables[target_var].label,fontsize=17)
            else: plt.xlabel('Peak '+label+' Change '+unit,fontsize=17)
        if abs_time_diff: 
            plt.ylabel('$|t_{diff}|$ [hr]',fontsize=17)
        else:
            plt.ylabel('Mainshock Time difference ($t_{diff}$) [hr]',fontsize=17)
        plt.grid(True,alpha=0.5)
        plt.tight_layout()
        if 'delay_quant' in locals():
            plt.savefig('/export/dump/jyun/perturb_stress/plots/time_advance_vs_delay/trigger_response_vs_%s.png'%(fign))
        else:
            plt.savefig('/export/dump/jyun/perturb_stress/plots/basic_aging_law_summary/trigger_response_vs_%s.png'%(fign))
    # c+=1
# print(c)