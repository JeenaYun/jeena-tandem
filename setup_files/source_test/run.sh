#!/bin/bash
model_n=source_test
branch_n=custom_source
tdhome=/raid/class239/jeena/Tandem
setup_dir=$tdhome/$model_n
rm -rf $setup_dir/*profile_$branch_n
mkdir -p /raid/class239/jeena/Tandem/$model_n
cd /raid/class239/jeena/Tandem/$model_n

####################################
# DON'T FORGET TO REMOVE THIS LINE #
echo "Remove directory: " /raid/class239/jeena/Tandem/$model_n/outputs_$branch_n
echo "Remove directory: " /raid/class239/jeena/Tandem/$model_n/$branch_n
rm -rf /raid/class239/jeena/Tandem/$model_n/outputs_$branch_n
rm -rf /raid/class239/jeena/Tandem/$model_n/$branch_n
# ####################################

echo "Create directory: " /raid/class239/jeena/Tandem/$model_n/outputs_$branch_n
mkdir -p outputs_$branch_n
cd outputs_$branch_n
echo "Tandem running in a directory: " $setup_dir

# mpiexec -bind-to core -n 5 /raid/class239/jeena/software/project-tandem/official_ckpnt/app/tandem $setup_dir/base.toml --petsc -ts_checkpoint_path checkpoint -ts_checkpoint_storage_type unlimited -ts_checkpoint_freq_step 50 -ts_checkpoint_freq_physical_time 10000000000 -ts_checkpoint_freq_cputime 10 -options_file $tdhome/options/lu_mumps.cfg -options_file $tdhome/options/rk45.cfg -ts_monitor > $setup_dir/messages_$branch_n.log &
# mpiexec -bind-to core -n 5 /raid/class239/jeena/software/project-tandem/official_ckpnt/app/tandem $setup_dir/base_pert.toml --petsc -ts_checkpoint_load $setup_dir/base/outputs/checkpoint/step64150 -ts_max_steps 65651 -ts_adapt_type none -ts_dt 0.01 -options_file $tdhome/options/lu_mumps.cfg -options_file $tdhome/options/rk45.cfg -ts_monitor > $setup_dir/messages_$branch_n.log &
# mpiexec -bind-to core -n 5 /raid/class239/jeena/software/project-tandem/original_source/app/tandem $setup_dir/original.toml --petsc -ts_checkpoint_load $setup_dir/base/outputs/checkpoint/step64150 -ts_max_steps 65651 -ts_adapt_type none -ts_dt 0.01 -options_file $tdhome/options/lu_mumps.cfg -options_file $tdhome/options/rk45.cfg -ts_monitor > $setup_dir/messages_$branch_n.log &
mpiexec -bind-to core -n 5 /raid/class239/jeena/software/project-tandem/custom_source/app/tandem $setup_dir/custom.toml --petsc -ts_checkpoint_load $setup_dir/base/outputs/checkpoint/step64150 -ts_max_steps 65651 -ts_adapt_type none -ts_dt 0.01 -options_file $tdhome/options/lu_mumps.cfg -options_file $tdhome/options/rk45.cfg -ts_monitor > $setup_dir/messages_$branch_n.log &
