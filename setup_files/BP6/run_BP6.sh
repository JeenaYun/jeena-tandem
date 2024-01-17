#!/bin/bash
model_n=BP6
branch_n=S_hf100m
tdhome=/home/jyun/Tandem
setup_dir=$tdhome/$model_n
rm -rf $setup_dir/*profile_$branch_n
mkdir -p /export/dump/jyun/$model_n
cd /export/dump/jyun/$model_n

####################################
# DON'T FORGET TO REMOVE THIS LINE #
echo "Remove directory: " /export/dump/jyun/$model_n/outputs_$branch_n
echo "Remove directory: " /export/dump/jyun/$model_n/$branch_n
rm -rf /export/dump/jyun/$model_n/outputs_$branch_n
rm -rf /export/dump/jyun/$model_n/$branch_n
# ####################################

echo "Create directory: " /export/dump/jyun/$model_n/outputs_$branch_n
mkdir -p outputs_$branch_n
cd outputs_$branch_n
echo "Tandem running in a directory: " $setup_dir

# mpiexec -bind-to core -n 10 tandem $setup_dir/bp6_demo.toml --petsc -ts_checkpoint_path checkpoint -ts_checkpoint_storage_type unlimited -ts_checkpoint_freq_step 50 -ts_checkpoint_freq_physical_time 1000000000 -ts_checkpoint_freq_cputime 10 -options_file $tdhome/options/lu_mumps.cfg -options_file $tdhome/options/rk45.cfg -ts_monitor > $setup_dir/messages_$branch_n.log &
mpiexec -bind-to core -n 10 tandem $setup_dir/bp6_S.toml --petsc -ts_checkpoint_path checkpoint -ts_checkpoint_storage_type unlimited -ts_checkpoint_freq_step 50 -ts_checkpoint_freq_physical_time 1000000000 -ts_checkpoint_freq_cputime 10 -options_file $tdhome/options/lu_mumps.cfg -options_file $tdhome/options/rk45.cfg -ts_monitor > $setup_dir/messages_$branch_n.log &
# mpiexec -bind-to core -n 10 tandem $setup_dir/bp6_A.toml --petsc -ts_checkpoint_path checkpoint -ts_checkpoint_storage_type unlimited -ts_checkpoint_freq_step 50 -ts_checkpoint_freq_physical_time 1000000000 -ts_checkpoint_freq_cputime 10 -options_file $tdhome/options/lu_mumps.cfg -options_file $tdhome/options/rk45.cfg -ts_monitor > $setup_dir/messages_$branch_n.log &
