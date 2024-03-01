#!/bin/bash
model_n=BP1
branch_n=dir_check
setup_dir=$tdhome/$model_n
# rm -rf *profile_$branch_n
# mkdir -p /export/dump/jyun/$model_n
# cd /export/dump/jyun/$model_n
# echo "Remove existing directory: " /export/dump/jyun/$model_n/outputs_$branch_n
# rm -rf outputs_$branch_n
# echo "Create directory: " /export/dump/jyun/$model_n/outputs_$branch_n
# mkdir -p outputs_$branch_n
# cd outputs_$branch_n
echo "Tandem running in a directory: " $setup_dir

tandem_aging='/home/jyun/softwares/project-tandem/build-cp-test-complete/app/tandem'
tandem_latest_slip='/home/jyun/softwares/project-tandem/build-tsckp-slip/app/tandem'
tandem_latest_aging='/home/jyun/softwares/project-tandem/build-tsckp-aging/app/tandem'

# --- Without any checkpointing
# Write out trajectory outputs
# mpiexec -bind-to core -n 10 tandem $setup_dir/bp1_sym_QDGreen.toml --petsc -ts_max_steps 100 -ts_save_trajectory -ts_trajectory_keep_files -ts_trajectory_dirname trajectories/$branch_n -ts_checkpoint_storage_type none -options_file $tdhome/options/ridgecrest.cfg > messages_$branch_n.log &
mpiexec -bind-to core -n 10 $tandem_latest_aging bp1_sym_test.toml --petsc -ts_max_steps 100 -ts_checkpoint_storage_type none -options_file ../options/ridgecrest.cfg > messages_$branch_n.log &

# --- With checkpointing every certain time steps, physical time & cpu time
# mpiexec -bind-to core -n 10 tandem $setup_dir/bp1_sym_QDGreen.toml --petsc -ts_max_steps 50 -ts_checkpoint_path checkpoint -ts_checkpoint_freq_step 1 -ts_checkpoint_freq_physical_time 1000000000 -ts_checkpoint_freq_cputime 60 -options_file $tdhome/options/ridgecrest.cfg > messages_$branch_n.log &
# mpiexec -bind-to core -n 10 tandem $setup_dir/bp1_sym_QDGreen.toml --petsc -ts_max_steps 3000 -ts_checkpoint_storage_type unlimited -ts_checkpoint_path checkpoint -ts_checkpoint_freq_step 50 -ts_checkpoint_freq_physical_time 1000000000 -ts_checkpoint_freq_cputime 60 -options_file $tdhome/options/ridgecrest.cfg > messages_$branch_n.log &
# mpiexec -bind-to core -n 10 tandem $setup_dir/bp1_sym_QDGreen.toml --petsc -ts_checkpoint_load ../QDGreen_base/outputs/checkpoint/step1250 -ts_max_steps 1550 -ts_checkpoint_storage_type none -options_file $tdhome/options/ridgecrest.cfg > messages_$branch_n.log &
# Write out trajectory outputs
# mpiexec -bind-to core -n 10 tandem $setup_dir/bp1_sym_QDGreen.toml --petsc -ts_max_steps 50 -ts_checkpoint_storage_type unlimited -ts_checkpoint_path checkpoint -ts_checkpoint_freq_step 1 -ts_save_trajectory -ts_trajectory_keep_files -ts_trajectory_dirname trajectories/$branch_n -options_file $tdhome/options/ridgecrest.cfg > messages_$branch_n.log &

# --- Load checkpointing
# mpiexec -bind-to core -n 10 tandem $setup_dir/bp1_sym_QDGreen.toml --petsc -ts_checkpoint_load ../del_debug_pert/outputs/checkpoint/step50 -ts_max_steps 100 -ts_checkpoint_path checkpoint -ts_checkpoint_freq_step 1 -options_file $tdhome/options/ridgecrest.cfg > messages_$branch_n.log &
# mpiexec -bind-to core -n 5 tandem $setup_dir/bp1_sym_QDGreen.toml --petsc -ts_checkpoint_load ../QD_with_GF_base/outputs/checkpoint/step100 -ts_max_steps 600 -ts_checkpoint_freq_step 50 -ts_checkpoint_freq_physical_time 1000000000000 -ts_checkpoint_freq_cputime 60 -options_file $tdhome/options/ridgecrest.cfg > messages_$branch_n.log &
# mpiexec -bind-to core -n 5 tandem $setup_dir/bp1_sym_QD.toml --petsc -ts_checkpoint_load ../QD_no_GF_base/outputs/checkpoint/step12100 -ts_max_steps 12400 -ts_checkpoint_freq_step 100000 -ts_checkpoint_freq_physical_time 1000000000000 -ts_checkpoint_freq_cputime 60 -options_file $tdhome/options/ridgecrest.cfg > messages_$branch_n.log &
# Write out trajectory outputs
# mpiexec -bind-to core -n 10 tandem $setup_dir/bp1_sym_QDGreen.toml --petsc -ts_checkpoint_load ../outputcheck_mid1_QDG/outputs/checkpoint/step50 -ts_max_steps 50 -ts_checkpoint_storage_type unlimited -ts_checkpoint_path checkpoint -ts_checkpoint_freq_step 1 -ts_save_trajectory -ts_trajectory_keep_files -ts_trajectory_dirname trajectories/$branch_n -options_file $tdhome/options/ridgecrest.cfg > messages_$branch_n.log &