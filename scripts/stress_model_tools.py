#!/usr/bin/env python3
"""
Tools for comparing stress perturbation models
Last modification: 2024.03.21.
Example usage: python stress_model_tools.py --seissol_model_n vert_fast vert_fast vert_fast vert_fast vert_slow vert_slow vert_slow vert_slow dipping_fast dipping_fast dipping_fast dipping_fast dipping_slow dipping_slow dipping_slow dipping_slow --strike 320 330 340 350 320 330 340 350 320 330 340 350 320 330 340 350 --target_depth 7.82
by Jeena Yun
"""
from scipy import interpolate
import numpy as np
import argparse
import change_params
import setup_shortcut
ch = change_params.variate()
sc = setup_shortcut.setups()

def get_vars(delPn,delTs,depth_range,target_depth,multiply,mu):
    dCFSt = delTs*multiply + mu*(delPn*multiply)
    dcfs_at_D = [interpolate.interp1d(depth_range,dCFSt[ti])(-target_depth) for ti in range(dCFSt.shape[0])]
    peak_dynamic = np.max(dcfs_at_D)
    static = np.mean(dcfs_at_D[-10:])
    return peak_dynamic,static

def fixed_model(save_dir,model_n,receivef_strike,target_depths,multiplies,mu,print_off):
    if not print_off: 
        if len(target_depths) == 1 and len(multiplies) == 1: 
            print('Single event and model: model %s%d & event depth %1.2f km'%(sc.model_code(model_n),receivef_strike,target_depths[0]))
        else:
            print('Fixed model: %s%d'%(sc.model_code(model_n),receivef_strike))
    if not print_off: print('--------------------------------------------------------------------------------')
    if not print_off: print('       Depth    |    Multiply   |    Peak dCFS [MPa]    |   Static dCFS [MPa]   ')
    if not print_off: print('----------------+---------------+-----------------------+-----------------------')
    delPn = np.load('%s/ssaf_%s_Pn_pert_mu%02d_%d.npy'%(save_dir,model_n,int(mu*10),receivef_strike))
    delTs = np.load('%s/ssaf_%s_Ts_pert_mu%02d_%d.npy'%(save_dir,model_n,int(mu*10),receivef_strike))
    depth_range = np.load('%s/ssaf_%s_dep_stress_pert_mu%02d_%d.npy'%(save_dir,model_n,int(mu*10),receivef_strike))
    mlen = max([len(target_depths),len(multiplies)])
    if len(target_depths) == 1: target_depths = target_depths[0]*np.ones(mlen)
    if len(multiplies) == 1: multiplies = multiplies[0]*np.ones(mlen)
    peak_dynamic,static = np.zeros(mlen),np.zeros(mlen)
    for it in range(mlen):
        target_depth = target_depths[it]
        multiply = multiplies[it]
        pd,st = get_vars(delPn,delTs,depth_range,target_depth,multiply,mu)
        peak_dynamic[it] = pd
        static[it] = st
        if not print_off: print('\t%1.2f\t|\tX%d\t|\t%1.4f\t\t|\t%1.4f'%(target_depth,multiply,pd,st))
    return peak_dynamic,static

def fixed_event(save_dir,model_ns,receivef_strikes,target_depth,multiplies,mu,print_off):
    if not print_off: print('Fixed event at depth = %1.2f km'%(target_depth))
    if not print_off: print('--------------------------------------------------------------------------------------------------------')
    if not print_off: print('       Model Name       |      Strike   |    Multiply   |    Peak dCFS [MPa]    |   Static dCFS [MPa]   ')
    if not print_off: print('------------------------+---------------+---------------+-----------------------+-----------------------')
    mlen = max([len(model_ns),len(receivef_strikes),len(multiplies)])
    if len(receivef_strikes) == 1: receivef_strikes = receivef_strikes[0]*np.ones(mlen)
    if len(multiplies) == 1: multiplies = multiplies[0]*np.ones(mlen)

    if len(model_ns) != len(receivef_strikes) != len(multiplies):
        print('len(model_ns) = %d; len(receivef_strikes) = %d; len(multiplies) = %d'%(len(model_ns),len(receivef_strikes),len(multiplies)))
        raise SyntaxError('Lengthx of models do not match!')
    peak_dynamic,static = np.zeros(len(model_ns)),np.zeros(len(model_ns))
    for it in range(len(model_ns)):
        model_n = model_ns[it]
        receivef_strike = receivef_strikes[it]
        multiply = multiplies[it]
        delPn = np.load('%s/ssaf_%s_Pn_pert_mu%02d_%d.npy'%(save_dir,model_n,int(mu*10),receivef_strike))
        delTs = np.load('%s/ssaf_%s_Ts_pert_mu%02d_%d.npy'%(save_dir,model_n,int(mu*10),receivef_strike))
        depth_range = np.load('%s/ssaf_%s_dep_stress_pert_mu%02d_%d.npy'%(save_dir,model_n,int(mu*10),receivef_strike))
        pd,st = get_vars(delPn,delTs,depth_range,target_depth,multiply,mu)
        peak_dynamic[it] = pd
        static[it] = st
        if not print_off: print('\t%s\t|\t%d\t|\tX%d\t|\t%1.4f\t\t|\t%1.4f'%(model_n,receivef_strike,multiply,pd,st))
    return peak_dynamic,static

# ---------------------- Set input parameters
def main(raw_args=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--seissol_model_n",nargs='+',type=str.lower,help=": Name of the SeisSol model")
    parser.add_argument("--strike",nargs='+',type=int,help=": Strike of the SeisSol model")
    parser.add_argument("--target_depths",nargs='+',type=float,help=": Depth of interest in km")
    parser.add_argument("--multiply",nargs='+',type=int,help=": If given, the integer is multiplied to the given perturbation model")
    parser.add_argument("--save_dir",type=str,help=": If given, directory where stress models are saved",default='perturb_stress/seissol_outputs')
    parser.add_argument("--mu",type=float,help=": If given, friction coefficient used for stress computation",default=0.4)
    parser.add_argument("--print_off", action="store_true", help=": ON/OFF cumulative slip profile",default=False)
    args = parser.parse_args()
    if args.multiply is None:
        multiply = np.ones(len(args.seissol_model_n))
    else:
        multiply = args.multiply
    print()
    if len(args.seissol_model_n) == 1:
        fixed_model(args.save_dir,args.seissol_model_n[0],args.strike[0],args.target_depths,multiply,args.mu,args.print_off)
    elif len(args.target_depths) == 1:
        fixed_event(args.save_dir,args.seissol_model_n,args.strike,args.target_depths[0],multiply,args.mu,args.print_off)
    print()

if __name__ == '__main__':
    main()