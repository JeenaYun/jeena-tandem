#!/usr/bin/env python3
'''
Concatenate truncated outputs due to the checkpointing feature (fault output)
By Jeena Yun
Last modification: 2024.05.03.
'''

import numpy as np
import pandas as pd
import time
from glob import glob
import os

write_on = 1
dir1 = '/export/dump/jyun/perturb_stress/first_after_pert8_vs340_262800h/outputs'
dir2 = '/export/dump/jyun/perturb_stress/outputs_continue_after_pert8_vs340_262800h'
save_dir = '/export/dump/jyun/perturb_stress/outputs_after_pert8_vs340_262800h'
# dir1 = '/export/dump/jyun/perturb_stress/hf10_reference_1/outputs'
# dir2 = '/export/dump/jyun/perturb_stress/hf10_reference_2/outputs'
# dir3 = '/export/dump/jyun/perturb_stress/hf10_reference_3/outputs'
# dir4 = '/export/dump/jyun/perturb_stress/hf10_reference_4/outputs'
# dir5 = '/export/dump/jyun/perturb_stress/hf10_reference_5/outputs'
# dir6 = '/export/dump/jyun/perturb_stress/outputs_hf10_reference_6'
# save_dir = '/export/dump/jyun/perturb_stress/hf10_reference/outputs'

if write_on: 
    os.system('rm -f finished_concate_fault.dat')
    flog = open('messages/faultp_concat.log','w')
    flog.write('*** Concate fault output summary ***\n')
    flog.write('Source directories:\n')
    flog.write('%s\n'%(dir1))
    flog.write('%s\n'%(dir2))
    # flog.write('%s\n'%(dir3))
    # flog.write('%s\n'%(dir4))
    # flog.write('%s\n'%(dir5))
    # flog.write('%s\n'%(dir6))
    flog.write('Output directory:\n')
    flog.write('%s\n\n'%(save_dir))

fnames = glob('%s/faultp_*.csv'%(dir1))

if not os.path.exists(save_dir): 
    if write_on: flog.write('Warning: output directory does not exist -> create directory %s\n\n'%(save_dir))
    else: print('Warning: save_dir does not exist -> create directory %s'%(save_dir))
    os.mkdir(save_dir)

if write_on: flog.write('*** Start processing ***\n')
ti = time.time()
for fn_template in np.sort(fnames):
    csv_name = fn_template.split('/outputs')[-1]
    if write_on: flog.write('Processing file %s\n'%(csv_name[1:]))
    else: print('Processing file %s'%(csv_name[1:]))
    fname1 = dir1+csv_name
    fname2 = dir2+csv_name
    # fname3 = dir3+csv_name
    # fname4 = dir4+csv_name
    # fname5 = dir5+csv_name
    # fname6 = dir6+csv_name

    dat1 = pd.read_csv(fname1,delimiter=',',skiprows=1)
    dat2 = pd.read_csv(fname2,delimiter=',',skiprows=[0,2])
    # dat3 = pd.read_csv(fname3,delimiter=',',skiprows=[0,2])
    # dat4 = pd.read_csv(fname4,delimiter=',',skiprows=[0,2])
    # dat5 = pd.read_csv(fname5,delimiter=',',skiprows=[0,2],nrows=255398)
    # # dat5 = pd.read_csv(fname5,delimiter=',',skiprows=[0,2])
    # dat6 = pd.read_csv(fname6,delimiter=',',skiprows=[0,2])
    comment = pd.read_csv(fname1,nrows=0,sep='\t')

    dat_concat = pd.concat([dat1,dat2],axis=0)
    # dat_concat = pd.concat([dat1,dat2,dat3],axis=0)
    # dat_concat = pd.concat([dat1,dat2,dat3,dat4,dat5],axis=0)
    # dat_concat = pd.concat([dat1,dat2,dat3,dat4,dat5,dat6],axis=0)

    if dat1.shape[0]+dat2.shape[0] != dat_concat.shape[0]:
    # if dat1.shape[0]+dat2.shape[0]+dat3.shape[0] != dat_concat.shape[0]:
    # if dat1.shape[0]+dat2.shape[0]+dat3.shape[0]+dat4.shape[0]+dat5.shape[0] != dat_concat.shape[0]:
    # if dat1.shape[0]+dat2.shape[0]+dat3.shape[0]+dat4.shape[0]+dat5.shape[0]+dat6.shape[0] != dat_concat.shape[0]:
        if write_on: flog.write('\nSomething went wrong - terminate program')
        else: print('Something went wrong - terminate program')
        break

    if write_on:
        fid = open(save_dir+csv_name,'a')
        fid.write(comment.columns[0]+'\n')
        dat_concat.to_csv(fid,index=False,float_format='%1.15e')
        fid.close()
    else:
        print('Write to %s'%(save_dir+csv_name))

if write_on: 
    flog.write('\n============ SUMMARY ============\n')
    flog.write('Run time: %2.4f s\n'%(time.time()-ti))
    flog.write('=================================\n')
    flog.close()
else:
    print('============ SUMMARY ============')
    print('Run time: %2.4f s'%(time.time()-ti))
    print('=================================')

os.system('touch finished_concate_fault.dat')