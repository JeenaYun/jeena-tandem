#!/usr/bin/env python3
'''
Concatenate truncated outputs due to the checkpointing feature
By Jeena Yun
Last modification: 2024.03.28.
'''

import numpy as np
import pandas as pd
import time
from glob import glob
import os

write_on = 1
dir1 = '/export/dump/jyun/perturb_stress/first_after_pert18_vs340_lowres_spinup_aginglaw_reference/outputs'
dir2 = '/export/dump/jyun/perturb_stress/continue_after_pert18_vs340_lowres_spinup_aginglaw_reference/outputs'
# dir1 = '/export/dump/jyun/perturb_stress/correct_slowVpl_reference_1/outputs'
# dir2 = '/export/dump/jyun/perturb_stress/outputs_correct_slowVpl_reference_2'
# dir3 = '/export/dump/jyun/perturb_stress/outputs_correct_slowVpl_reference_3'
save_dir = '/export/dump/jyun/perturb_stress/outputs_after_pert18_vs340_lowres_spinup_aginglaw_reference'

fnames = glob('%s/faultp_*.csv'%(dir1))

if not os.path.exists(save_dir): 
    print('Warning: save_dir does not exist -> create directory %s'%(save_dir))
    os.mkdir(save_dir)

if write_on: flog = open('messages_faultp_concat.log','w')
ti = time.time()
for fn_template in np.sort(fnames):
    csv_name = fn_template.split('/outputs')[-1]
    if write_on: 
        flog.write('Processing file %s\n'%(csv_name[1:]))
    else:
        print('Processing file %s'%(csv_name[1:]))
    fname1 = dir1+csv_name
    fname2 = dir2+csv_name
    # fname3 = dir3+csv_name
    # fname4 = dir4+csv_name
    # fname5 = dir5+csv_name

    dat1 = pd.read_csv(fname1,delimiter=',',skiprows=1)
    dat2 = pd.read_csv(fname2,delimiter=',',skiprows=1)
    # dat3 = pd.read_csv(fname3,delimiter=',',skiprows=1)
    # dat4 = pd.read_csv(fname4,delimiter=',',skiprows=1)
    # dat5 = pd.read_csv(fname5,delimiter=',',skiprows=1,nrows=255398)
    comment = pd.read_csv(fname1,nrows=0,sep='\t')

    dat_concat = pd.concat([dat1,dat2],axis=0)
    # dat_concat = pd.concat([dat1,dat2,dat3],axis=0)
    # dat_concat = pd.concat([dat1,dat2,dat3,dat4,dat5],axis=0)
    if dat1.shape[0]+dat2.shape[0] != dat_concat.shape[0]:
    # if dat1.shape[0]+dat2.shape[0]+dat3.shape[0] != dat_concat.shape[0]:
    # if dat1.shape[0]+dat2.shape[0]+dat3.shape[0]+dat4.shape[0]+dat5.shape[0] != dat_concat.shape[0]:
        print('Something wrong!!')
        break

    if write_on:
        fid = open(save_dir+csv_name,'a')
        fid.write(comment.columns[0]+'\n')
        dat_concat.to_csv(fid,index=False,float_format='%1.15e')
        fid.close()
    else:
        print('Write to %s'%(save_dir+csv_name))

if write_on: 
    flog.write('============ SUMMARY ============\n')
    flog.write('Run time: %2.4f s\n'%(time.time()-ti))
    flog.write('=================================')
    flog.close()
else:
    print('============ SUMMARY ============')
    print('Run time: %2.4f s'%(time.time()-ti))
    print('=================================')