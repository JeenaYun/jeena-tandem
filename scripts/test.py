from perturb_tools import PERTURB
import numpy as np

def compute_indicators(model,target_var,base_model):
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
        idx = model.target_eventid
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
    else:
        raise SyntaxError('No definition for the target variable')
    return value

tvars = ['max_dCFS','min_dCFS','static_dCFS','max_shearT','min_shearT','static_shearT','slip','sliprate','integrated_work']

base_model = PERTURB('lowres_spinup_aginglaw_reference')
base_model.load_events()
for kk in range(len(tvars)):
    target_var = tvars[kk]
    fign = target_var
    mode = ''
    if 'state' in target_var or 'shearT' in target_var or 'dCFS' in target_var or 'work' in target_var:
        if 'max' in target_var: 
            mode = 'max'
        elif 'static' in target_var:
            mode = 'static'
        elif 'min' in target_var: 
            mode = 'min'
        elif 'integrated' in target_var: 
            mode = 'integrated'
        elif 'average' in target_var: 
            mode = 'average'
        target_var = target_var.replace(mode+'_','')

    branch_n = 'pert18_vs340_lowres_spinup_aginglaw_reference'
    model = PERTURB(branch_n)
    model.load_output(print_on=False)

    out_val = compute_indicators(model,target_var,base_model)
    print('%s = %g'%(fign,out_val))