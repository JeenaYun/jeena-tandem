# A script to extract variables along the depth profile at certain point of time
# Last modification: 2024.02.26.
# Example usage: python extract_profile.py /export/dump/jyun/perturb_stress/hf10_reference_2 0 --save_on
import numpy as np
import argparse
import os
from read_outputs import load_fault_probe_outputs

# --- Set input parameters
parser = argparse.ArgumentParser()
parser.add_argument("output_dir",type=str,help=": Path where outputs sits")
parser.add_argument("extract_time",type=float,help=": Time at which you want to extract the solution profile. If -1 or 0 is given, it extracts the last or the first written output, respectively.")
parser.add_argument("--short_output",type=int,help=": If given, searches for short output.",default=None)
parser.add_argument("--save_dir",type=str,help=": If given, path where you want to write the extracted profiles. Default is the same as the output_dir.")
parser.add_argument("--save_on",action="store_true",help=": Save on?")
parser.add_argument("--print_off",action="store_true",help=": Print off?")
args = parser.parse_args()

if not args.save_dir:
    if not args.print_off: print('save_dir not given - use output_dir')
    args.save_dir = args.output_dir

if args.extract_time <= 0:
    if args.extract_time == 0:
        flag = 'first'
    else:
        flag = 'last'
    time_summ = flag
else:
    time_summ = '%1.15e'%(args.extract_time)

if args.short_output is None:
    short_out_sum = 'No'
else:
    short_out_sum = 'Yes (indx = %d)'%(args.short_output)


print('============ Input Parameter Summary ============')
print('output_dir         : %s'%(args.output_dir))
print('extract_time (s)   : %s'%(time_summ))
print('short_output       : %s'%(short_out_sum))
print('save_dir           : %s'%(args.save_dir))
print('save_on            : %r'%(args.save_on))
print('print_off          : %r'%(args.print_off))
print('=================================================')

# --- Computation
if args.short_output is None:
    outputs = np.load('%s/outputs.npy'%(args.output_dir))
else:
    if not args.print_off: print('Use short_outputs_%d'%(args.short_output))
    outputs = np.load('%s/short_outputs_%d.npy'%(args.output_dir,args.short_output))
dep = np.load('%s/outputs_depthinfo.npy'%(args.output_dir))


ii = np.flip(np.argsort(abs(dep)))
time = outputs[0,:,0]
state = outputs[ii,:,1]
cumslip = outputs[ii,:,2]
shearT = outputs[ii,:,3]
sliprate = outputs[ii,:,4]
normalT = outputs[ii,:,5]
z = dep[ii]

if args.extract_time <= 0:
    profile_indx = int(args.extract_time)
    if not args.print_off: print('Extraction occurs at the %s time of the output: %1.15e s'%(flag,time[profile_indx]))
else:
    if args.extract_time < np.min(time) or args.extract_time > np.max(time): raise ValueError('Given time is out of the range of the given output file')
    profile_indx = np.argmin(abs(time-args.extract_time))
    if not args.print_off: print('Extraction occurs at time %1.15e s'%(time[profile_indx]))
    flag = '%s'%(profile_indx)

extract_state = state[:,profile_indx]
extract_shearT = shearT[:,profile_indx]
extract_sliprate = sliprate[:,profile_indx]
extract_normalT = normalT[:,profile_indx]


if args.save_on:
    np.savetxt('%s/extract_state_%s.dat'%(args.save_dir,flag),np.c_[z,extract_state])
    np.savetxt('%s/extract_shearT_%s.dat'%(args.save_dir,flag),np.c_[z,extract_shearT])
    np.savetxt('%s/extract_sliprate_%s.dat'%(args.save_dir,flag),np.c_[z,extract_sliprate])
    np.savetxt('%s/extract_normalT_%s.dat'%(args.save_dir,flag),np.c_[z,extract_normalT])