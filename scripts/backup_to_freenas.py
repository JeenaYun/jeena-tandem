import numpy as np
import os

testmode = False

if testmode:
    print('Test mode')
    status_fn = 'test_status.txt'
    macro_fn = 'test_move_macro.sh'
else:
    status_fn = 'status.txt'
    macro_fn = 'move_macro.sh'

freenas_dir = '/import/freenas-m-05-seissol/jyun/perturb_stress'
output_dir = '/export/dump/jyun/perturb_stress'
freenas_fn = [name for name in os.listdir(freenas_dir) if os.path.isdir(os.path.join(freenas_dir, name))]
raw_fn = [name for name in os.listdir(output_dir) if os.path.isdir(os.path.join(output_dir, name))]

fid = open(os.path.join(output_dir, macro_fn),'w')
fid.write('rm -f %s\n'%(status_fn))
fid.write('touch %s\n'%(status_fn))

for fn in np.sort(raw_fn):
    if fn in freenas_fn:
        print(fn,': already backed up >> skip')
    else:
        print(fn) 
        fid.write('cp -r %s %s; echo "%s done" >> %s\n'%(os.path.join(output_dir,fn),freenas_dir,fn,status_fn))

fid.write('echo "\n-----------------------------------------" >> %s\n'%(status_fn))
fid.write('echo "Backup Successful - Bye!" >> %s\n'%(status_fn))
fid.close()