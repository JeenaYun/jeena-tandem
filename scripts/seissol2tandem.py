#!/usr/bin/env python3
'''
Convert SeisSol output to ascii data file for tandem
By Jeena Yun
Last modification: 2024.06.13.
'''
import numpy as np
import os
import argparse

# Set input parameters -------------------------------------------------------------------------------------------------------------------
parser = argparse.ArgumentParser()
parser.add_argument("mode",type=int,help="Mode of the seissol -> tandem conversion")
parser.add_argument("--seissol_model_n",nargs='+',type=str.lower,help=": Name of the SeisSol model",default=['vert_slow'])
parser.add_argument("--strike",nargs='+',type=int,help=": Strike of the SeisSol model",default=[340])
parser.add_argument("-X","--X",type=int,help=": If given, the integer is multiplied to the given perturbation model")
parser.add_argument("--save_dir",type=str,help=": If given, directory where stress models are saved",default='perturb_stress/seissol_outputs')
args = parser.parse_args()

mode = args.mode
save_dir = args.save_dir
range_model_n = args.seissol_model_n
range_receivef_strike = args.strike
if mode == 5:
    if not args.X:
        parser.error('Required field \'X\' is not defined - check again')
    else:
        multiply = args.X
mu = 0.4
dt=0.01

# ---------------- Define function
def gaussian(x,a,b,c):
    return a*np.exp(-((x-b)**2/(2*c**2)))

def process_seissol_output(mode,delPn,delTs,dt,mult):
    t = np.arange(0,delPn.shape[0]/100,dt)
    if mode == 1:
        new_dsn,new_dtau = delPn,delTs
    if mode in [2,5]:
        # Dynamic only
        char_decay_t = 1.5
        ti = np.where(t>=10)[0][0]
        new_dsn = np.array([np.hstack((delPn[:ti,di],gaussian(t[ti:],delPn[ti,di],t[ti],char_decay_t))) for di in range(delPn.shape[1])]).T
        new_dtau = np.array([np.hstack((delTs[:ti,di],gaussian(t[ti:],delTs[ti,di],t[ti],char_decay_t))) for di in range(delTs.shape[1])]).T
        if mode == 5:
            # Amplify amplitude
            new_dsn = mult*new_dsn
            new_dtau = mult*new_dtau
        ti = np.where(t>=14.5)[0][0]
        new_dsn[ti:,:] = np.zeros(new_dsn[ti:,:].shape)
        new_dtau[ti:,:] = np.zeros(new_dtau[ti:,:].shape)
    elif mode in [3,4]:
        # Static only
        char_decay_t = 2.25
        ti = np.where(t<=10)[0][-1]
        new_dsn = np.array([np.hstack((gaussian(t[:ti],delPn[ti,di],t[ti],char_decay_t),delPn[ti:,di])) for di in range(delPn.shape[1])]).T
        new_dtau = np.array([np.hstack((gaussian(t[:ti],delTs[ti,di],t[ti],char_decay_t),delTs[ti:,di])) for di in range(delTs.shape[1])]).T
        if mode == 4:
            # Artificially flip sign
            new_dsn = -new_dsn
            new_dtau = -new_dtau
        ti = np.where(t<=2)[0][-1]
        new_dsn[:ti,:] = np.zeros(new_dsn[:ti,:].shape)
        new_dtau[:ti,:] = np.zeros(new_dtau[:ti,:].shape)
    else:
        raise ValueError('Mode %d not detected - check your input'%(mode))
    return new_dsn,new_dtau

def routine_seissol2tandem(save_dir,model_n,string,mu,receivef_strike,mult=None):
    if not os.path.exists("%s/ssaf_%s%s_Pn_pert_mu%02d_%d.dat"%(save_dir,model_n,string,int(mu*10),receivef_strike)):
        delPn = np.load('%s/ssaf_%s_Pn_pert_mu%02d_%d.npy'%(save_dir,model_n,int(mu*10),receivef_strike))
        delTs = np.load('%s/ssaf_%s_Ts_pert_mu%02d_%d.npy'%(save_dir,model_n,int(mu*10),receivef_strike))
        depth_range = np.load('%s/ssaf_%s_dep_stress_pert_mu%02d_%d.npy'%(save_dir,model_n,int(mu*10),receivef_strike))
        new_dsn,new_dtau = process_seissol_output(mode,delPn,delTs,dt,mult)
        np.savetxt("%s/ssaf_%s%s_Pn_pert_mu%02d_%d.dat"%(save_dir,model_n,string,int(mu*10),receivef_strike),X=new_dsn,fmt='%.6f',delimiter='\t',newline='\n') 
        np.savetxt("%s/ssaf_%s%s_Ts_pert_mu%02d_%d.dat"%(save_dir,model_n,string,int(mu*10),receivef_strike),X=new_dtau,fmt='%.6f',delimiter='\t',newline='\n') 
        np.savetxt("%s/ssaf_%s%s_dep_stress_pert_mu%02d_%d.dat"%(save_dir,model_n,string,int(mu*10),receivef_strike),X=depth_range,fmt='%.6f',newline='\n') 
        print(' - saved')
    else:
        print(' exists - skip')

# ---------------- 1. Regular conversion
if mode == 1:
    print('Mode 1: Regular conversion')
    string = ''
    for model_n in range_model_n:
        for receivef_strike in range_receivef_strike:
            print('%s; %d'%(model_n,receivef_strike),end='')
            routine_seissol2tandem(save_dir,model_n,string,mu,receivef_strike)

# ---------------- 2-5. Ignore static change
if mode == 2 or mode == 5:
    if mode == 2: 
        print('Mode 2: Ignore static change')
        string = '_dyn'
        multiply = 1
    elif mode == 5:
        print('Mode 5: Ignore static change & amplify')
        string = '_dyn_X%d'%(multiply)
    for model_n in range_model_n:
        for receivef_strike in range_receivef_strike:
            print('%s; %d; dynamic only'%(model_n,receivef_strike),end='')
            routine_seissol2tandem(save_dir,model_n,string,mu,receivef_strike,multiply)

# ---------------- 3-4. Ignore dynamic change
if mode == 3 or mode == 4:
    if mode == 3: 
        print('Mode 3: Ignore dynamic change')
        string = '_static'
    elif mode == 4: 
        print('Mode 4: Ignore dynamic change & flip sign')
        string = '_flipstat'
    for model_n in range_model_n:
        for receivef_strike in range_receivef_strike:
            if mode == 3: print('%s; %d; static only'%(model_n,receivef_strike),end='')
            elif mode == 4: print('%s; %d; static only, flipped'%(model_n,receivef_strike),end='')
            routine_seissol2tandem(save_dir,model_n,string,mu,receivef_strike)
