'''
Reads in petsc binary files
By Jeena Yun, modified from Dave May
Last modification: 2023.11.25.
'''
import numpy as np
import PetscBinaryIO as pio

def PetscVecLoadFromFile(fname, **kwags):
  io = pio.PetscBinaryIO(**kwags) # Instantiate a petsc binary loader
  with open(fname) as fp:
    objecttype = io.readObjectType(fp)
    v = io.readVec(fp)
  return v

def PetscMatLoadFromFile(fname, **kwags):
  io = pio.PetscBinaryIO(**kwags) # Instantiate a petsc binary loader
  with open(fname) as fp:
    commsize = np.fromfile(fp, dtype=io._inttype, count=1)[0]
    ngf = np.fromfile(fp, dtype=io._inttype, count=1)[0]
    print(commsize, ngf)
    objecttype = io.readObjectType(fp)
    v = io.readMatDense(fp)
  return v

fname1 = 'gf/gf_mat.bin'
G_checkpointed = PetscMatLoadFromFile(fname1)
print(G_checkpointed.shape, np.min(G_checkpointed), np.max(G_checkpointed))

fname2 = 'gf1.mat'
G_bin = PetscMatLoadFromFile(fname2)
print(G_bin.shape, np.min(G_bin), np.max(G_bin))


print('Max. abs. diff: %1.15e'%(np.max(abs(G_checkpointed - G_bin))))
print('Mean. abs. diff: %1.15e'%(np.mean(abs(G_checkpointed - G_bin))))
print('Min. abs. diff: %1.15e'%(np.min(abs(G_checkpointed - G_bin))))

# for i in range(101):
#   x1 = PetscVecLoadFromFile('%s/%s/TS-%06d.bin'%(base_dir,dir1,i))
#   if i < 50:
#     x2 = PetscVecLoadFromFile('%s/%s/TS-%06d.bin'%(base_dir,dir2,i))
#     crit = [np.all(x1==x2)]
#   elif i > 50:
#     x3 = PetscVecLoadFromFile('%s/%s/TS-%06d.bin'%(base_dir,dir3,i))
#     crit = [np.all(x1==x3)]
#   elif i == 50:
#     x2 = PetscVecLoadFromFile('%s/%s/TS-%06d.bin'%(base_dir,dir2,i))
#     x3 = PetscVecLoadFromFile('%s/%s/TS-%06d.bin'%(base_dir,dir3,i))
#     crit = [np.all(x1==x2),np.all(x1==x3)]
#   if len(crit) == 1:
#     print('(i = %d) All components the same? -->'%(i),crit[0])
#     if crit[0]: correct += 1
#   else:
#     print('(i = %d) All components the same? -->'%(i),crit[0],'(for mid1);',crit[1],'(for mid1)')
#     if crit[0] and crit[1]: correct += 1
#   total += 1 
# print('=================================')
# print('In summary, %d out of %d checkpoints are completely agreeing'%(correct,total))

# # x1 = PetscVecLoadFromFile('%s/%s/TS-%06d.bin'%(base_dir,dir1,35))
# # x2 = PetscVecLoadFromFile('%s/%s/TS-%06d.bin'%(base_dir,dir2,34))
# # crit = np.all(x1==x2)
# # print(crit)
