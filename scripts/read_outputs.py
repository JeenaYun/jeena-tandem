#!/usr/bin/env python3
'''
Functions related to reading tandem outputs: fault/fault_probe/domain_probe
By Jeena Yun
Last modification: 2024.03.28.
'''
import numpy as np
from glob import glob
import os
import time
import change_params
import setup_shortcut

sc = setup_shortcut.setups()
ch = change_params.variate()

def extract_from_lua(save_dir,save_on=True):
    prefix = ch.extract_prefix(save_dir)
    fname = 'matfric_Fourier_main'
    sep = 'BP1.'
    if len(prefix.split('/')) == 1:
        fname = prefix + '/' + fname + '.lua'
    elif 'hetero_stress' in prefix and ch.get_model_n(prefix,'v') == 0:
        fname = prefix.split('/')[0] + '/' + fname + '.lua'
    elif '_long' in prefix.split('/')[-1]:
        strr = prefix.split('/')[-1].split('_long')
        fname = prefix.split('/')[0] + '/' + fname + '_'+strr[0]+'.lua'
    elif 'hetero_stress' in prefix and 'n' in prefix.split('/')[-1]:
        strr = prefix.split('/')[-1].split('_')
        tails = ''
        for k in range(1,len(strr)):
            tails += '_%s'%(strr[k])
        fname = prefix.split('/')[0] + '/' + fname + tails +'.lua'
    elif 'mtmod' in prefix:
        fname = prefix.split('/')[0] + '/' + fname + '.lua'
        sep = 'mtmod.'
    elif 'BP1' in prefix:
        if 'delsn' in prefix.split('/')[-1]:
            fname = prefix.split('/')[0] + '/' + 'bp1_deltasn.lua'
        else:
            fname = prefix.split('/')[0] + '/' + 'bp1.lua'
    elif 'perturb_stress' in prefix:
        if 'slowVpl' in prefix:
            fname = prefix.split('/')[0] + '/' + fname + '_reference_slowVpl.lua'
        elif 'reference' in prefix:
            fname = prefix.split('/')[0] + '/' + fname + '_reference.lua'
        else:
            fname = prefix.split('/')[0] + '/' + fname + '_perturb.lua'
            sep = 'ridgecrest.'
    else:
        fname = prefix.split('/')[0] + '/' + fname + '_'+prefix.split('/')[-1]+'.lua'
    ch.get_setup_dir()
    fname = ch.setup_dir + '/' + fname
    print(fname)

    here = False
    try:
        fid = open(fname,'r')
    except FileNotFoundError:
        new_fname_list = fname.split('/supermuc')
        fname = new_fname_list[0] + new_fname_list[1]
        fid = open(fname,'r')
    lines = fid.readlines()
    params = {}
    for line in lines:
        if here:
            var = line.split('return ')[-1]
            try:
                params['mu'] = params['cs']**2 * params['rho0']
            except KeyError:
                params['mu'] = float(var.strip())
            here = False
        if sep in line and 'index' not in line and 'new' not in line:
            var = line.split(sep)[1].split(' = ')
            if len(var[1].split('--')) > 1:
                if var[0] == 'dip':
                    params[var[0]] = float(var[1].split('--')[0].split('*')[0])
                # elif var[0].lower() == 'h' or var[0].lower() == 'h2':
                elif '*' in var[1]:
                    params[var[0]] = float(var[1].split('--')[0].split('*')[0]) * np.sin(params['dip'])
                else:
                    params[var[0]] = float(var[1].split('--')[0])            
            else:
                if var[0] == 'dip':
                    params[var[0]] = float(var[1].split('*')[0])
                elif '*' in var[1]:
                # elif var[0].lower() == 'h' or var[0].lower() == 'h2':
                    params[var[0]] = float(var[1].split('*')[0]) * np.sin(params['dip'])
                else:
                    params[var[0]] = float(var[1])
        elif ':mu' in line and 'DZ' not in prefix and 'self:mu' not in line:
            here = True
        # elif sep in line:
        #     var = line.split(sep)[1].split(' = ')
        #     if len(var[1].split('--')) > 1:
        #         params[var[0]] = float(var[1].split('--')[0])            
        #     else:
        #         params[var[0]] = float(var[1])
    fid.close()
    if save_on:
        print('Save data...',end=' ')
        np.save('%s/const_params'%(save_dir),params)
        print('done!')
    return np.array(params)
    
def read_fault_probe_outputs(save_dir,save_on=True):
    import pandas as pd
    fnames = glob('%s/outputs/faultp_*.csv'%(save_dir))
    if len(fnames) == 0:
        print('Cannot find faultp_*.csv - try finding receiver_*.csv')
        fnames = glob('%s/outputs/receiver_*.csv'%(save_dir))
    if len(fnames) == 0:
        print('Cannot find receiver_*.csv either - try finding fltst_*.csv')
        fnames = glob('%s/outputs/fltst_*.csv'%(save_dir))
    if len(fnames) == 0:
        raise NameError('No fault probe output found - check the input')
    outputs,dep=[],[]
    print('Start computing output... ',end='')
    ti = time.time()
    for fname in np.sort(fnames):
        # dat = pd.read_csv(fname,delimiter=',',skiprows=1,nrows=255398) # only for hf10_reference_5
        dat = pd.read_csv(fname,delimiter=',',skiprows=1)
        stloc = pd.read_csv(fname,nrows=1,header=None)
        dep.append(float(stloc.values[0][-1].split(']')[0]))
        outputs.append(dat.values)
    print('Done! (%2.4f s)'%(time.time()-ti))
    outputs = np.array(outputs)
    dep = np.array(dep)

    # --- Extract input constants
    params = extract_from_lua(save_dir)
    if save_on:
        print('Save data...',end=' ')
        np.save('%s/outputs'%(save_dir),outputs)
        np.save('%s/outputs_depthinfo'%(save_dir),dep)
        print('done!')
    return outputs,dep,params

def read_domain_probe_outputs(save_dir,save_on=True):
    import pandas as pd
    fnames = glob('%s/outputs/domainp_*.csv'%(save_dir))
    if len(fnames) == 0:
        raise NameError('No domain probe output found - check the input')
    outputs,xyloc=[],[]
    for fname in np.sort(fnames):
        dat = pd.read_csv(fname,delimiter=',',skiprows=2)
        stloc = pd.read_csv(fname,nrows=1,header=None)
        xyloc.append([float(stloc.values[0][0].split('[')[-1]),float(stloc.values[0][-1].split(']')[0])])
        outputs.append(dat.values)
    outputs = np.array(outputs)
    xyloc = np.array(xyloc)
    if save_on:
        print('Save data...',end=' ')
        np.save('%s/domain_probe_outputs'%(save_dir),outputs)
        np.save('%s/domain_probe_outputs_xyloc'%(save_dir),xyloc)
        print('done!')
    return outputs,xyloc

def read_fault_outputs(save_dir,save_on=True):
    from vtk import vtkXMLUnstructuredGridReader
    # --- Read time info from pvd file
    time = read_pvd('%s/outputs/fault.pvd'%(save_dir))

    # --- Load individual vtu files and extract fault outputs
    fnames = glob('%s/outputs/fault_*.vtu'%(save_dir))
    if len(fnames) == 0:
        raise NameError('No such file found - check the input')
    sliprate,slip,shearT,normalT,state_var,dep = \
    [np.array([]) for k in range(time.shape[0])],[np.array([]) for k in range(time.shape[0])],[np.array([]) for k in range(time.shape[0])],\
    [np.array([]) for k in range(time.shape[0])],[np.array([]) for k in range(time.shape[0])],[np.array([]) for k in range(time.shape[0])]
    for file_name in fnames:
        if 'static' in file_name:
            continue
        # --- Read the source file
        reader = vtkXMLUnstructuredGridReader()
        reader.SetFileName(file_name)
        reader.Update()  # Needed because of GetScalarRange
        output = reader.GetOutput()
        k = int(file_name.split('fault_')[-1].split('_')[0])
        # --- Save into local variable
        sliprate[k] = np.hstack((sliprate[k],np.array(output.GetPointData().GetArray('slip-rate0'))))
        slip[k] = np.hstack((slip[k],np.array(output.GetPointData().GetArray('slip0'))))
        shearT[k] = np.hstack((shearT[k],np.array(output.GetPointData().GetArray('traction0'))))
        normalT[k] = np.hstack((normalT[k],np.array(output.GetPointData().GetArray('normal-stress'))))
        state_var[k] = np.hstack((state_var[k],np.array(output.GetPointData().GetArray('state'))))
        dep[k] = np.hstack((dep[k],np.array([output.GetPoint(k)[1] for k in range(output.GetNumberOfPoints())])))

    # --- Convert the outputs into numpy array
    sliprate = np.array(sliprate)
    slip = np.array(slip)
    shearT = np.array(shearT)
    normalT = np.array(normalT)
    state_var = np.array(state_var)
    dep = np.array(dep)
    print(sliprate.shape,slip.shape,shearT.shape,normalT.shape,state_var.shape,dep.shape)

    # --- Sort them along depth
    ind = np.argsort(dep,axis=1)
    sliprate = np.take_along_axis(sliprate, ind, axis=1)
    slip = np.take_along_axis(slip, ind, axis=1)
    shearT = np.take_along_axis(shearT, ind, axis=1)
    normalT = np.take_along_axis(normalT, ind, axis=1)
    state_var = np.take_along_axis(state_var, ind, axis=1)
    dep = np.sort(dep,axis=1)

    # --- Finally, arrange their shape to match with the fault probe output
    outputs = np.array([np.vstack((time,state_var.T[dp],slip.T[dp],shearT.T[dp],sliprate.T[dp],normalT.T[dp])).T for dp in range(dep.shape[1])])

    # --- Extract input constants
    params = extract_from_lua(save_dir)
    if save_on:
        print('Save data...',end=' ')
        np.save('%s/fault_outputs'%(save_dir),outputs)
        np.save('%s/fault_outputs_depthinfo'%(save_dir),dep)
        print('done!')
    return outputs,dep,params

def load_fault_probe_outputs(save_dir,print_on=True):
    if print_on: print('Load saved data: %s/outputs.npy'%(save_dir))
    outputs = np.load('%s/outputs.npy'%(save_dir))
    if print_on: print('Load saved data: %s/outputs_depthinfo.npy'%(save_dir))
    dep = np.load('%s/outputs_depthinfo.npy'%(save_dir))
    if print_on: print('Load saved data: %s/const_params.npy'%(save_dir))
    params = np.load('%s/const_params.npy'%(save_dir),allow_pickle=True)
    return outputs,dep,params

def load_fault_outputs(save_dir,print_on=True):
    if print_on: print('Load saved data: %s/fault_outputs.npy'%(save_dir))
    outputs = np.load('%s/fault_outputs.npy'%(save_dir))
    if print_on: print('Load saved data: %s/fault_outputs_depthinfo.npy'%(save_dir))
    dep = np.load('%s/fault_outputs_depthinfo.npy'%(save_dir))
    if print_on: print('Load saved data: %s/const_params.npy'%(save_dir))
    params = np.load('%s/const_params.npy'%(save_dir),allow_pickle=True)
    return outputs,dep,params

def load_domain_probe_outputs(save_dir,print_on=True):
    if print_on: print('Load saved data: %s/domain_probe_outputs.npy'%(save_dir))
    outputs = np.load('%s/domain_probe_outputs.npy'%(save_dir))
    if print_on: print('Load saved data: %s/domain_probe_outputs_xyloc.npy'%(save_dir))
    xyloc = np.load('%s/domain_probe_outputs_xyloc.npy'%(save_dir))
    return outputs,xyloc

def load_checkpoint_info(save_dir,print_on=True):
    import pandas as pd
    dat = pd.read_csv('%s/checkpoint_info.csv'%(save_dir),delimiter=',').values
    return dat

def load_short_fault_probe_outputs(save_dir,indx,print_on=True):
    if print_on: print('Load saved data: %s/short_outputs_%d'%(save_dir,indx))
    outputs = np.load('%s/short_outputs_%d.npy'%(save_dir,indx))
    if print_on: print('Load saved data: %s/outputs_depthinfo'%(save_dir))
    dep = np.load('%s/outputs_depthinfo.npy'%(save_dir))
    if print_on: print('Load saved data: %s/const_params.npy'%(save_dir))
    params = np.load('%s/const_params.npy'%(save_dir),allow_pickle=True)
    return outputs,dep,params

def load_cumslip_outputs(save_dir,image='sliprate',Vths=None,SRvar=None,rths=None,dt_creep=None,dt_coseismic=None,print_on=True):
    _,_,tmp_Vths,tmp_SRvar,_,_,_,tmp_rths,tmp_dt_creep,tmp_dt_coseismic = sc.base_event_criteria(save_dir,image)
    if Vths is None: Vths = tmp_Vths
    if SRvar is None: SRvar = tmp_SRvar
    if rths is None: rths = tmp_rths
    if dt_creep is None: dt_creep = tmp_dt_creep
    if dt_coseismic is None: dt_coseismic = tmp_dt_coseismic
    if print_on: print('Load saved data: %s/cumslip_outputs_Vths_%1.0e_srvar_%03d_rths_%d_tcreep_%d_tseis_%02d.npy'%(save_dir,Vths,SRvar*100,rths,dt_creep/ch.yr2sec,dt_coseismic*10))
    cumslip_outputs = np.load('%s/cumslip_outputs_Vths_%1.0e_srvar_%03d_rths_%d_tcreep_%d_tseis_%02d.npy'%(save_dir,Vths,SRvar*100,rths,dt_creep/ch.yr2sec,dt_coseismic*10),allow_pickle=True)
    if print_on: print('Load saved data: %s/spin_up_idx_Vths_%1.0e_srvar_%03d_rths_%d_tcreep_%d_tseis_%02d.npy'%(save_dir,Vths,SRvar*100,rths,dt_creep/ch.yr2sec,dt_coseismic*10))
    spin_up_idx = np.load('%s/spin_up_idx_Vths_%1.0e_srvar_%03d_rths_%d_tcreep_%d_tseis_%02d.npy'%(save_dir,Vths,SRvar*100,rths,dt_creep/ch.yr2sec,dt_coseismic*10))
    return cumslip_outputs,spin_up_idx
    
def read_pvd(fname):
    if not os.path.exists(fname):
        raise NameError('No such file found - check the input')
    fid = open(fname,'r')
    lines = fid.readlines()
    time = []
    for line in lines:
        if line.split('<')[1].split()[0] == 'DataSet':
            time.append(float(line.split('\"')[1]))
    fid.close()
    time = np.array(time)
    return time


class OUTPUTS:
    def __init__(self,outputs,dep,target_var):
        idx = {'time': 0, 'state': 1, 'slip': 2, 'shearT': 3, 'sliprate': 4, 'normalT': 5}
        label = {'time': 'Time [s]', \
            'state': r'State Variable $\psi$', \
            'slip': 'Slip [m]', \
            'shearT': 'Shear Traction [MPa]', \
            'sliprate': 'Slip Rate [m/s]', \
            'normalT': 'Normal Stress [MPa]'} 
        ii = np.argsort(abs(dep))
        if target_var == 'shearT' or target_var == 'sliprate':
            var = outputs[ii,1:,idx[target_var]]
        elif target_var == 'time':
            var = outputs[0,:,idx[target_var]]
        else:
            var = outputs[ii,:,idx[target_var]]
        self.data = var
        self.label = label[target_var]
        