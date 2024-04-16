#!/usr/bin/env python3
'''
Concatenate truncated outputs due to the checkpointing feature
By Jeena Yun
Last modification: 2023.11.03.
'''

import numpy as np
import pandas as pd
import time
from glob import glob
import os

dir1 = '/export/dump/jyun/perturb_stress/first_after_pert18_vs340_lowres_spinup_aginglaw_reference/outputs'
dir2 = '/export/dump/jyun/perturb_stress/continue_after_pert18_vs340_lowres_spinup_aginglaw_reference/outputs'
# dir1 = '/export/dump/jyun/perturb_stress/hf10_reference_1/outputs'
# dir2 = '/export/dump/jyun/perturb_stress/hf10_reference_2/outputs'
# dir3 = '/export/dump/jyun/perturb_stress/hf10_reference_3/outputs'
# dir4 = '/export/dump/jyun/perturb_stress/hf10_reference_4/outputs'
# dir5 = '/export/dump/jyun/perturb_stress/hf10_reference_5/outputs'
# dir6 = '/export/dump/jyun/perturb_stress/outputs_hf10_reference_6'
save_dir = '/export/dump/jyun/perturb_stress/outputs_after_pert18_vs340_lowres_spinup_aginglaw_reference'


fnames = glob('%s/domainp_*.csv'%(dir1))

if not os.path.exists(save_dir): 
    print('Warning: save_dir does not exist -> create directory %s'%(save_dir))
    os.mkdir(save_dir)

flog = open('messages_domainp_concat.log','w')
ti = time.time()
for fname1 in np.sort(fnames):
    csv_name = fname1.split('/outputs')[-1]
    flog.write('Processing file %s\n'%(csv_name[1:]))
    fname1 = dir1+csv_name
    fname2 = dir2+csv_name
    # fname3 = dir3+csv_name
    # fname4 = dir4+csv_name
    # fname5 = dir5+csv_name
    # fname6 = dir6+csv_name

    dat1 = pd.read_csv(fname1,delimiter=',',skiprows=1)
    dat2 = pd.read_csv(fname2,delimiter=',',skiprows=1)
    # dat3 = pd.read_csv(fname3,delimiter=',',skiprows=1)
    # dat4 = pd.read_csv(fname4,delimiter=',',skiprows=1)
    # dat5 = pd.read_csv(fname5,delimiter=',',skiprows=1)
    # dat6 = pd.read_csv(fname6,delimiter=',',skiprows=1)
    comment = pd.read_csv(fname1,nrows=0,sep='\t')

    dat_concat = pd.concat([dat1,dat2],axis=0)
    # dat_concat = pd.concat([dat1,dat2,dat3],axis=0)
    # dat_concat = pd.concat([dat1,dat2,dat3,dat4,dat5],axis=0)
    # dat_concat = pd.concat([dat1,dat2,dat3,dat4,dat5,dat6],axis=0)
    # if fname3 == fnames[0]:
    #     print('dat1.shape:',dat1.shape)
    #     print('dat2.shape:',dat2.shape)
    #     print('dat3.shape:',dat3.shape)
    #     print('dat_concat.shape:',dat_concat.shape)
    if dat1.shape[0]+dat2.shape[0] != dat_concat.shape[0]:
    # if dat1.shape[0]+dat2.shape[0]+dat3.shape[0] != dat_concat.shape[0]:
    # if dat1.shape[0]+dat2.shape[0]+dat3.shape[0]+dat4.shape[0]+dat5.shape[0] != dat_concat.shape[0]:
    # if dat1.shape[0]+dat2.shape[0]+dat3.shape[0]+dat4.shape[0]+dat5.shape[0]+dat6.shape[0] != dat_concat.shape[0]:
        print('Something wrong!!')
        break

    fid = open(save_dir+csv_name,'a')
    fid.write(comment.columns[0]+'\n')
    dat_concat.to_csv(fid,index=False,float_format='%1.15e')
    fid.close()

flog.close()
print('============ SUMMARY ============')
print('Run time: %2.4f s'%(time.time()-ti))
print('=================================')