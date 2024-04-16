#!/usr/bin/env python3
'''
Extract informations from the checkpoint csv file
By Jeena Yun
Last modification: 2024.03.26.
'''
import numpy as np
import pandas as pd
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("output_root_dir",type=str,help=": Output directory")
parser.add_argument("output_branch_name",type=str,help=": Branch name of the output")
parser.add_argument("--max_time", action="store_true", help=": Display maximum time of the written checkpoint",default=False)
parser.add_argument("--min_time", action="store_true", help=": Display minimum time of the written checkpoint",default=False)
parser.add_argument("--max_timestep", action="store_true", help=": Display maximum time step of the written checkpoint",default=False)
parser.add_argument("--min_timestep", action="store_true", help=": Display minimum time step of the written checkpoint",default=False)
parser.add_argument("--time_at_step_N", type=int, help=": Display the time at certain step",default=-1)
args = parser.parse_args()

dat = pd.read_csv('/export/dump/jyun/%s/%s/checkpoint_info.csv'%(args.output_root_dir,args.output_branch_name))
ts,time = dat.values[:,0],dat.values[:,1]

if args.max_time: print('Maximum time of the written checkpoint: %1.18e'%(np.max(time)))
if args.max_timestep: print('Maximum timestep of the written checkpoint: %d'%(np.max(ts)))
if args.min_time: print('Minimum time of the written checkpoint: %1.18e'%(np.min(time)))
if args.min_timestep: print('Minimum timestep of the written checkpoint: %d'%(np.min(ts)))
if args.time_at_step_N > 0:
    ii = np.argmin(abs(ts-args.time_at_step_N))
    print('Time at step %d: %1.18e'%(ts[ii],time[ii]))