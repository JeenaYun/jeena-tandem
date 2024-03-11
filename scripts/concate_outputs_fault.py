#!/usr/bin/env python3
'''
Concatenate truncated outputs due to the checkpointing feature
By Jeena Yun
Last modification: 2024.01.17.
'''

import numpy as np
import pandas as pd
import time
from glob import glob

write_on = 1
dir1 = '/export/dump/jyun/perturb_stress/first_after_pert8_vsX10_340_stress_dep/outputs'
dir2 = '/export/dump/jyun/perturb_stress/continue_after_pert8_vsX10_340_stress_dep/outputs'
# dir3 = '/export/dump/jyun/perturb_stress/outputs_reference_3'
save_dir = '/export/dump/jyun/perturb_stress/after_pert8_vsX10_340_stress_dep/outputs'

fnames = glob('%s/faultp_*.csv'%(dir1))

if write_on: flog = open('messages_faultp_concat.log','w')
ti = time.time()
for fname3 in np.sort(fnames):
    csv_name = fname3.split('/outputs')[-1]
    # csv_name = fname3.split('outputs_reference_3')[-1]
    if write_on: 
        flog.write('Processing file %s\n'%(csv_name[1:]))
    else:
        print('Processing file %s'%(csv_name[1:]))
    fname1 = dir1+csv_name
    fname2 = dir2+csv_name

    dat1 = pd.read_csv(fname1,delimiter=',',skiprows=1)
    dat2 = pd.read_csv(fname2,delimiter=',',skiprows=1)
    # dat3 = pd.read_csv(fname3,delimiter=',',skiprows=1)
    comment = pd.read_csv(fname1,nrows=0,sep='\t')

    dat12 = pd.concat([dat1,dat2],axis=0)
    # dat123 = pd.concat([dat1,dat2,dat3],axis=0)
    if dat1.shape[0]+dat2.shape[0] != dat12.shape[0]:
    # if dat1.shape[0]+dat2.shape[0]+dat3.shape[0] != dat123.shape[0]:
        print('Something wrong!!')
        break

    if write_on:
        fid = open(save_dir+csv_name,'a')
        fid.write(comment.columns[0]+'\n')
        dat12.to_csv(fid,index=False,float_format='%1.15e')
        # dat123.to_csv(fid,index=False,float_format='%1.15e')
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