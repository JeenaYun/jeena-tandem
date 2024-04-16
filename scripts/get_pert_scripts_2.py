#!/usr/bin/env python3
'''
Automatically write scripts for stress perturbation
Example usage: python get_pert_scripts.py perturb_stress reference 31 vert_fast 330 --streess_dep_law --write_on
By Jeena Yun
Last modification: 2024.04.08.
'''

import numpy as np
import argparse
import os
import change_params
import setup_shortcut
ch = change_params.variate()
sc = setup_shortcut.setups()

# ---------------------- Set input parameters
parser = argparse.ArgumentParser()
parser.add_argument("model_n",type=str.lower,help=": Name of big group of the model")
parser.add_argument("output_branch_n",type=str.lower,help=": Name of the branch where outputs reside")
parser.add_argument("target_sys_evID",type=int,help=": System-wide event index")
parser.add_argument("seissol_model_n",type=str.lower,help=": Name of the SeisSol model")
parser.add_argument("strike",type=int,help=": Strike of the SeisSol model")
parser.add_argument("--write_on",action="store_true",help=": Write lua, toml, and shell script?",default=False)
parser.add_argument("--dt",type=float,help=": If given, time interval of the SeisSol output",default=0.01)
parser.add_argument("--n_node",type=int,help=": Number of nodes for tandem simulation",default=40)
parser.add_argument("--time_diff_in_sec",type=float,help=": If given, time difference between the perturbation point and the mainshock",default=58320)
parser.add_argument("--ckp_freq_step",type=int,help=": If given, step interval for checkpointing",default=50)
parser.add_argument("--ckp_freq_ptime",type=float,help=": If given, physical time interval for checkpointing",default=10000000000)
parser.add_argument("--ckp_freq_cputime",type=float,help=": If given, CPU time interval for checkpointing",default=60)
parser.add_argument("--dstep",type=int,help=": If given, number of steps to run for the after perturbation model",default=50000)
parser.add_argument("--add_fintime",type=int,help=": If given, additional hours after the unperturbed event start time",default=4)
parser.add_argument("--multiply",type=int,help=": If given, the integer is multiplied to the given perturbation model",default=1)
parser.add_argument("--no_pert_period",action="store_true",help=": If given, do not write perturbation period",default=False)
parser.add_argument("--no_after_pert_period",action="store_true",help=": If given, do not write after perturbation period",default=False)
parser.add_argument("--streess_dep_law",action="store_true",help=": If given, use stress dependent law",default=False)
args = parser.parse_args()

fcoeff = 0.4 # Perturbation related parameters

# -------- 0. Generate multiplied model if given
if args.multiply != 1:
    print('MULTIPLY ON: SeisSol model %s multiplied by %d'%(args.seissol_model_n,args.multiply))
    seissol_model_n = args.seissol_model_n + '_X%d'%(args.multiply)
    if args.write_on and not os.path.exists("/home/jyun/Tandem/%s/seissol_outputs/ssaf_%s_Pn_pert_mu%02d_%d.dat"%(args.model_n,seissol_model_n,int(fcoeff*10),args.strike)):
        print('XXX Writing multiplied model %s XXX'%(seissol_model_n))
        delPn = np.loadtxt("/home/jyun/Tandem/%s/seissol_outputs/ssaf_%s_Pn_pert_mu%02d_%d.dat"%(args.model_n,args.seissol_model_n,int(fcoeff*10),args.strike))
        delTs = np.loadtxt("/home/jyun/Tandem/%s/seissol_outputs/ssaf_%s_Ts_pert_mu%02d_%d.dat"%(args.model_n,args.seissol_model_n,int(fcoeff*10),args.strike))
        depth_range = np.loadtxt("/home/jyun/Tandem/%s/seissol_outputs/ssaf_%s_dep_stress_pert_mu%02d_%d.dat"%(args.model_n,args.seissol_model_n,int(fcoeff*10),args.strike))
        np.savetxt("/home/jyun/Tandem/%s/seissol_outputs/ssaf_%s_Pn_pert_mu%02d_%d.dat"%(args.model_n,seissol_model_n,int(fcoeff*10),args.strike),X=delPn*args.multiply,fmt='%.20f',delimiter='\t',newline='\n')
        np.savetxt("/home/jyun/Tandem/%s/seissol_outputs/ssaf_%s_Ts_pert_mu%02d_%d.dat"%(args.model_n,seissol_model_n,int(fcoeff*10),args.strike),X=delTs*args.multiply,fmt='%.20f',delimiter='\t',newline='\n')
        np.savetxt("/home/jyun/Tandem/%s/seissol_outputs/ssaf_%s_dep_stress_pert_mu%02d_%d.dat"%(args.model_n,seissol_model_n,int(fcoeff*10),args.strike),X=depth_range,fmt='%.20f',newline='\n')
else:
    seissol_model_n = args.seissol_model_n

# -------- Adjust inputs 
# Set path and file names
output_save_dir = '/export/dump/jyun/%s/%s'%(args.model_n,args.output_branch_n)
decor = ''
if args.time_diff_in_sec != 58320:
    decor += '_%dh'%(args.time_diff_in_sec/3600)
if args.output_branch_n != 'reference':
    decor += '_%s'%(args.output_branch_n)

matched_save_dir = '/export/dump/jyun/%s/match%d%s'%(args.model_n,args.target_sys_evID,decor)
matched_ckp = 'match%d%s/outputs/checkpoint'%(args.target_sys_evID,decor)
run_branch_n = 'pert%d_%s%d%s'%(args.target_sys_evID,sc.model_code(seissol_model_n),args.strike,decor)
if args.streess_dep_law:
    run_branch_n += '_stress_dep'

fname_lua = '/home/jyun/Tandem/%s/scenario_perturb_2.lua'%(args.model_n)
fname_toml = '/home/jyun/Tandem/%s/parameters_perturb_scenario_2.toml'%(args.model_n)
fname_shell = '/home/jyun/Tandem/routine_perturb_2.sh'

execution = '$tandem_aging'
hf = '25'
ckp_options = '-ts_checkpoint_path checkpoint'
if 'sliplaw' in args.output_branch_n:
    args.n_node = 80
    hf = '10'
    execution = '$tandem_latest_slip'
    ckp_options += ' -ts_checkpoint_storage_type unlimited'
elif 'lowres' in args.output_branch_n and 'aginglaw' in args.output_branch_n:
    args.n_node = 10
    hf = '125'
    
print('====================== Summary of Input Parameters =======================')
print('output_save_dir = %s'%(output_save_dir))
print('matched_save_dir = %s'%(matched_save_dir))
print('run_branch_n = %s'%(run_branch_n))
print('seissol_model_n = %s'%(seissol_model_n))
print('strike = %d'%(args.strike))
print('fcoeff = %1.1f'%(fcoeff))
print('dt = %1.2f'%(args.dt))
print('n_node = %d'%(args.n_node))
print('ckp_freq_step = %d'%(args.ckp_freq_step))
print('ckp_freq_ptime = %d'%(args.ckp_freq_ptime))
print('ckp_freq_cputime = %d'%(args.ckp_freq_cputime))
# print('dstep = %d'%(args.dstep))
print('fin_time = unperturb_tstart + %d'%(args.add_fintime))
if args.no_pert_period:
    print('*** Not writing perturbation period ***')
if args.no_after_pert_period:
    print('*** Not writing after perturbation period ***')

# -------- 1. Check if the matched checkpoint exists - if not, run make_closer
if not os.path.exists(matched_save_dir):
    import subprocess
    print('##### %s NOT FOUND - Need time matching #####'%(matched_save_dir))
    if args.write_on:
        print('XXX Writing file make_closer.py XXX\n')
        # Syntax e.g., python /home/jyun/Tandem/make_closer.py perturb_stress reference 6 --write_on
        if args.time_diff_in_sec == 58320:
            subprocess.run(["python","/home/jyun/Tandem/make_closer.py",args.model_n,args.output_branch_n,"%d"%(args.target_sys_evID),"--write_on"])
        else:
            subprocess.run(["python","/home/jyun/Tandem/make_closer.py",args.model_n,args.output_branch_n,"%d"%(args.target_sys_evID),"--write_on","--time_diff_in_sec",args.time_diff_in_sec])
        print('\nXXX Done writing make_closer.py -> run it first! XXX')
    else:
        if args.time_diff_in_sec == 58320:
            subprocess.run(["python","/home/jyun/Tandem/make_closer.py",args.model_n,args.output_branch_n,"%d"%(args.target_sys_evID)])
        else:
            subprocess.run(["python","/home/jyun/Tandem/make_closer.py",args.model_n,args.output_branch_n,"%d"%(args.target_sys_evID),"--time_diff_in_sec",args.time_diff_in_sec])
    raise SyntaxError('Run match time first')

# -------- 2. Load event outputs
from cumslip_compute import analyze_events
from read_outputs import load_cumslip_outputs

vmin,vmax,Vths,intv,Vlb,dt_interm,cuttime,rths,dt_creep,dt_coseismic = sc.base_event_criteria(output_save_dir,'sliprate')
cumslip_outputs,spin_up_idx = load_cumslip_outputs(output_save_dir,'sliprate')
tstart,tend,evdep = cumslip_outputs[0][0],cumslip_outputs[0][1],cumslip_outputs[1][1]
system_wide = analyze_events(cumslip_outputs,rths)[2]
if args.output_branch_n == 'reference':
    idx = system_wide[system_wide>=spin_up_idx][args.target_sys_evID]
else:
    idx = args.target_sys_evID

# -------- 3. Extract exact init time at the time of the checkpoint
from read_outputs import load_checkpoint_info
ckp_dat = load_checkpoint_info(matched_save_dir)
stepnum = int(np.sort(ckp_dat,axis=0)[-1][0])
init_time = np.sort(ckp_dat,axis=0)[-1][-1]
maxstep = int(stepnum + 15/args.dt + 1)
print('System-size Event Index = %d; Event %d; Hypocenter Depth: %1.2f [km]'%(args.target_sys_evID,idx,evdep[idx]))
print('Nearest checkpoint #: %d'%(stepnum))
print('Difference in time between the perturbation point and the checkpoint: %1.4f s'%(tstart[idx]-args.time_diff_in_sec - init_time))
print('==========================================================================')

if args.write_on:
    # -------- 4. Generate Lua scenario
    # scenarios = np.genfromtxt('perturb_stress/scenario_perturb.lua',skip_header=4,delimiter=' =',usecols=0,dtype='str')
    scenario_name = '%s%d_%d'%(sc.model_code(seissol_model_n),args.strike,stepnum)
    fsn,_ = ch.get_model_n('%s/%s'%(args.model_n,args.output_branch_n),'v')
    fab,_ = ch.get_model_n('%s/%s'%(args.model_n,args.output_branch_n),'ab')
    fdc,_ = ch.get_model_n('%s/%s'%(args.model_n,args.output_branch_n),'Dc')
    lowres,Vp = 1,1e-9
    if 'lowres' in args.output_branch_n: lowres = 5
    if 'slowVpl' in args.output_branch_n: Vp = 3.2e-11

    if args.streess_dep_law:
        scenario_name += '_stress_dep'
    if args.output_branch_n != 'reference':
        scenario_name += '_%s'%(args.output_branch_n)

    print('XXX Writing file %s XXX'%(fname_lua))
    flua = open(fname_lua,'w')
    flua.write('package.path = package.path .. ";/home/jyun/Tandem"\n')
    flua.write('local ridgecrest54 = require "matfric_Fourier_main_perturb"\n')
    flua.write('local ridgecrest54_stress_dep = require "matfric_Fourier_main_perturb_stress_dep"\n')
    flua.write('local ridgecrest54_spinup = require "matfric_Fourier_main_perturb_spinup"\n\n')
    if args.streess_dep_law:
        flua.write('%s = ridgecrest54_stress_dep.new{model_n=\'%s\',strike=%d,fcoeff=%1.1f,dt=%1.2f,init_time=%1.18e,fsn=%d,fab=%d,fdc=%d,lowres=%d,Vp=%g}'\
                    %(scenario_name,seissol_model_n,args.strike,fcoeff,args.dt,init_time,fsn,fab,fdc,lowres,Vp))
    elif 'spinup' in args.output_branch_n:
        flua.write('%s = ridgecrest54_spinup.new{model_n=\'%s\',strike=%d,fcoeff=%1.1f,dt=%1.2f,init_time=%1.18e,fsn=%d,fab=%d,fdc=%d,lowres=%d,Vp=%g}'\
                    %(scenario_name,seissol_model_n,args.strike,fcoeff,args.dt,init_time,fsn,fab,fdc,lowres,Vp))
    else:
        flua.write('%s = ridgecrest54.new{model_n=\'%s\',strike=%d,fcoeff=%1.1f,dt=%1.2f,init_time=%1.18e,fsn=%d,fab=%d,fdc=%d,lowres=%d,Vp=%g}'\
                    %(scenario_name,seissol_model_n,args.strike,fcoeff,args.dt,init_time,fsn,fab,fdc,lowres,Vp))
    flua.close()

    # -------- 5. Generate parameter file
    print('XXX Writing file %s XXX'%(fname_toml))
    fpar = open(fname_toml,'w')
    fpar.write('final_time = 157680000000\n')
    fpar.write('mesh_file = "ridgecrest_hf%s.msh"\n'%(hf))
    fpar.write('mode = "QDGreen"\n')
    fpar.write('type = "poisson"\n')
    fpar.write('lib = "%s"\n'%(fname_lua.split('/')[-1]))
    fpar.write('scenario = "%s"\n'%(scenario_name))
    fpar.write('ref_normal = [-1, 0]\n')
    fpar.write('boundary_linear = true\n\n')

    if 'slowVpl' in args.output_branch_n:
        fpar.write('gf_checkpoint_prefix = "/export/dump/jyun/GreensFunctions/ridgecrest_hf%s_slowVpl"\n\n'%(hf))
    else:
        fpar.write('gf_checkpoint_prefix = "/export/dump/jyun/GreensFunctions/ridgecrest_hf%s"\n\n'%(hf))

    fpar.write('[fault_probe_output]\n')
    fpar.write('prefix = "faultp_"\n')
    fpar.write('t_max = 0.009\n')
    sc.write_faultprobe_loc(ch.extract_prefix(output_save_dir),fpar,dmin=0.02,dmax=1.,dip=90,write_on=args.write_on)

    fpar.write('[domain_probe_output]\n')
    fpar.write('prefix = "domainp_"\n')
    fpar.write('t_max = 0.009\n')
    sc.write_domainprobe_loc(fpar,xmax=100,dx=5,write_on=args.write_on)
    fpar.close()

    # -------- 6. Generate a shell file to operate everything
    print('XXX Writing file %s XXX'%(fname_shell))
    fshell = open(fname_shell,'w')
    fshell.write('#!/bin/bash\n')
    # 6.0. Define some useful functions and paths
    fshell.write('# Define some useful functions\n')
    fshell.write('process_output_full() { echo "/export/dump/jyun/$1/$2"; '
                    'mkdir -p "/export/dump/jyun/$1/$2"; '
                    'mv "/export/dump/jyun/$1/outputs_$2" "/export/dump/jyun/$1/$2"; '
                    'mv "/export/dump/jyun/$1/$2/outputs_$2" "/export/dump/jyun/$1/$2/outputs"; '
                    'python /home/jyun/Tandem/get_plots.py /export/dump/jyun/$1/$2 -c; }\n')
    fshell.write('read_time_full() { /home/jyun/Tandem/read_time_recursive "/export/dump/jyun/$1/$2"; }\n')
    fshell.write('existckp_full() { ls "/export/dump/jyun/$1/$2"; }\n')
    fshell.write('''tandem_aging='/home/jyun/softwares/project-tandem/build-cp-test-complete/app/tandem'\n''')
    fshell.write('''tandem_latest_slip='/home/jyun/softwares/project-tandem/build-tsckp-slip/app/tandem'\n\n''')

    fshell.write('model_n=%s\n'%(args.model_n))
    fshell.write('tdhome=/home/jyun/Tandem\n')
    fshell.write('setup_dir=$tdhome/$model_n\n\n')
    
    if not args.no_pert_period:
        # 6.1. Run the perturbation period
        fshell.write('# Run the perturbation period\n')
        fshell.write('branch_n=%s\n'%(run_branch_n))
        fshell.write('mkdir -p /export/dump/jyun/$model_n\n')
        fshell.write('cd /export/dump/jyun/$model_n\n')
        fshell.write('mkdir -p outputs_$branch_n\n')
        fshell.write('cd outputs_$branch_n\n')
        fshell.write('echo "Tandem running in a directory: " $setup_dir\n\n')

        # 6.1.0. Run a safety check
        fshell.write('# Safety check\n')
        fshell.write('existckp_full $model_n %s/step%d\n\n'%(matched_ckp,stepnum))

        # 6.1.2. If safe, proceed
        fshell.write('# If safe, proceed\n')
        if args.multiply == 30:
            # -- Below lines are for X30 model that nucleates immediately
            fshell.write('mpiexec -bind-to core -n %d %s $setup_dir/%s --petsc -ts_checkpoint_load ../%s/step%d '
                        '-ts_adapt_dt_max %.2f -ts_max_steps %d %s '
                        '-ts_checkpoint_freq_step 1 -ts_checkpoint_freq_physical_time %d -ts_checkpoint_freq_cputime %d '
                        '-options_file $tdhome/options/ridgecrest.cfg > $setup_dir/messages_$branch_n.log\n\n'\
                        %(args.n_node,execution,fname_toml.split('/')[-1],matched_ckp,stepnum,args.dt,maxstep,ckp_options,args.ckp_freq_ptime,args.ckp_freq_cputime))
        else:
            fshell.write('mpiexec -bind-to core -n %d %s $setup_dir/%s --petsc -ts_checkpoint_load ../%s/step%d '
                        '-ts_adapt_type none -ts_dt %.2f -ts_max_steps %d %s '
                        '-ts_checkpoint_freq_step 1 -ts_checkpoint_freq_physical_time %d -ts_checkpoint_freq_cputime %d '
                        '-options_file $tdhome/options/ridgecrest.cfg > $setup_dir/messages_$branch_n.log\n\n'\
                        %(args.n_node,execution,fname_toml.split('/')[-1],matched_ckp,stepnum,args.dt,maxstep,ckp_options,args.ckp_freq_ptime,args.ckp_freq_cputime))

        # 6.2. Process the perturation period output and generate checkpoint time info
        fshell.write('# Process the perturbation period output, change the directory name, and generate checkpoint time info\n')
        fshell.write('process_output_full $model_n $branch_n\n')
        fshell.write('read_time_full $model_n $branch_n\n\n')
    
    if not args.no_after_pert_period:
        fin_time = tstart[idx] + args.add_fintime*3600
        print('Final time: %g s'%(fin_time))
        # 6.3. Run the after perturbation period
        fshell.write('# Run the after perturbation period\n')
        fshell.write('branch_n=after_%s\n'%(run_branch_n))
        fshell.write('cd /export/dump/jyun/$model_n\n')
        fshell.write('mkdir -p outputs_$branch_n\n')
        fshell.write('cd outputs_$branch_n\n')
        fshell.write('echo "Tandem running in a directory: " $setup_dir\n\n')

        # 6.3.0. Run a safety check
        fshell.write('# Safety check\n')
        fshell.write('existckp_full $model_n %s/outputs/checkpoint/step%d\n\n'%(run_branch_n,maxstep))
        
        # 6.3.1. If safe, proceed
        fshell.write('# If safe, proceed\n')
        fshell.write('mpiexec -bind-to core -n %d %s $setup_dir/%s --final_time %1.15e --petsc -ts_checkpoint_load ../%s/outputs/checkpoint/step%d '
                    '-ts_adapt_type basic %s '
                    '-ts_checkpoint_freq_step %d -ts_checkpoint_freq_physical_time %d -ts_checkpoint_freq_cputime %d '
                    '-options_file $tdhome/options/ridgecrest.cfg > $setup_dir/messages_$branch_n.log\n\n'\
                    %(args.n_node,execution,fname_toml.split('/')[-1],fin_time,run_branch_n,maxstep,ckp_options,args.ckp_freq_step,args.ckp_freq_ptime,args.ckp_freq_cputime))
        
        # 6.4. Finally, process the after perturation period output
        fshell.write('# Finally, Process the after perturbation period output, change the directory name, and generate checkpoint time info\n')
        fshell.write('process_output_full $model_n $branch_n\n')
        fshell.write('read_time_full $model_n $branch_n\n\n')
    fshell.close()
