#!/bin/bash
model_n=perturb_stress
branch_n=lowres_spinup_aginglaw_reference_hf25
tdhome=/home/jyun/Tandem
setup_dir=$tdhome/$model_n
rm -rf $setup_dir/*profile_$branch_n
mkdir -p /export/dump/jyun/$model_n
cd /export/dump/jyun/$model_n

# ####################################
# # DON'T FORGET TO REMOVE THIS LINE #
# echo "Remove directory: " /export/dump/jyun/$model_n/$branch_n
# rm -rf $branch_n
# ####################################

echo "Create directory: " /export/dump/jyun/$model_n/outputs_$branch_n
mkdir -p outputs_$branch_n
cd outputs_$branch_n
# mkdir -p fault_output
# mkdir -p domain_output
echo "Tandem running in a directory: " $setup_dir

tandem_aging='/home/jyun/softwares/project-tandem/build-cp-test-complete/app/tandem'
tandem_latest_slip='/home/jyun/softwares/project-tandem/build-tsckp-slip/app/tandem'
tandem_latest_aging='/home/jyun/softwares/project-tandem/build-tsckp-aging/app/tandem'

# mpiexec -bind-to core -n 10 /home/jyun/softwares/project-tandem/build-tsckp-aging/app/tandem /home/jyun/Tandem/perturb_stress/parameters_tmp.toml --petsc -ts_checkpoint_storage_type none -options_file /home/jyun/Tandem/options/ridgecrest.cfg
# mpiexec -bind-to core -n 40 /home/jyun/softwares/project-tandem/build-tsckp-aging/app/tandem /home/jyun/Tandem/perturb_stress/parameters_tmp.toml --petsc -ts_checkpoint_storage_type none -options_file /home/jyun/Tandem/options/ridgecrest.cfg > /home/jyun/Tandem/perturb_stress/messages_domain_test_slowVpl.log &

# --- Build mesh
#mpiexec -bind-to core -n 80 $tandem_latest_slip $setup_dir/build_GF.toml --petsc -options_file $tdhome/options/ridgecrest.cfg > $setup_dir/messages_$branch_n.log &

# --- With checkpointing every certain time steps, physical time & cpu time
# mpiexec -bind-to core -n 10 $tandem_aging $setup_dir/parameters_reference_lowres.toml --petsc -ts_checkpoint_path checkpoint -ts_checkpoint_freq_step 50 -ts_checkpoint_freq_physical_time 3153600000 -ts_checkpoint_freq_cputime 60 -options_file $tdhome/options/ridgecrest.cfg > $setup_dir/messages_$branch_n.log &
mpiexec -bind-to core -n 40 $tandem_aging $setup_dir/parameters_reference_lowres.toml --petsc -ts_checkpoint_path checkpoint -ts_checkpoint_freq_step 50 -ts_checkpoint_freq_physical_time 3153600000 -ts_checkpoint_freq_cputime 60 -options_file $tdhome/options/ridgecrest.cfg > $setup_dir/messages_$branch_n.log &
# mpiexec -bind-to core -n 80 $tandem_latest_slip $setup_dir/parameters_sliplaw_reference_lowres.toml --petsc -ts_checkpoint_storage_type unlimited -ts_checkpoint_freq_step 50 -ts_checkpoint_freq_physical_time 3153600000 -ts_checkpoint_freq_cputime 60 -options_file $tdhome/options/ridgecrest.cfg > $setup_dir/messages_$branch_n.log &
# mpiexec -bind-to core -n 80 $tandem_latest_slip $setup_dir/parameters_sliplaw_reference.toml --petsc -ts_checkpoint_storage_type unlimited -ts_checkpoint_freq_step 50 -ts_checkpoint_freq_physical_time 1000000000 -ts_checkpoint_freq_cputime 60 -options_file $tdhome/options/ridgecrest.cfg > $setup_dir/messages_$branch_n.log &
# mpiexec -bind-to core -n 40 $tandem_aging $setup_dir/parameters_reference.toml --petsc -ts_checkpoint_path checkpoint -ts_checkpoint_freq_step 50 -ts_checkpoint_freq_physical_time 1000000000 -ts_checkpoint_freq_cputime 60 -options_file $tdhome/options/ridgecrest.cfg > $setup_dir/messages_$branch_n.log &
# mpiexec -bind-to core -n 40 $tandem_aging $setup_dir/parameters_reference_diffwavelength.toml --petsc -ts_checkpoint_path checkpoint -ts_checkpoint_freq_step 100 -ts_checkpoint_freq_physical_time 3153600000 -ts_checkpoint_freq_cputime 60 -options_file $tdhome/options/ridgecrest.cfg > $setup_dir/messages_$branch_n.log &
# mpiexec -bind-to core -n 40 $tandem_aging $setup_dir/parameters_reference_slowVpl.toml --petsc -ts_checkpoint_path checkpoint -ts_checkpoint_freq_step 100 -ts_checkpoint_freq_physical_time 3153600000 -ts_checkpoint_freq_cputime 60 -options_file $tdhome/options/ridgecrest.cfg > $setup_dir/messages_$branch_n.log &
# mpiexec -bind-to core -n 80 tandem $setup_dir/parameters_hf10_reference.toml --petsc -ts_checkpoint_freq_step 50 -ts_checkpoint_freq_physical_time 1000000000 -ts_checkpoint_freq_cputime 60 -ts_checkpoint_path checkpoint -options_file $tdhome/options/ridgecrest.cfg > $setup_dir/messages_$branch_n.log &
# mpiexec -bind-to core -n 60 tandem $setup_dir/p10Dc2.toml --petsc -ts_checkpoint_freq_step 50 -ts_checkpoint_freq_physical_time 1000000000 -ts_checkpoint_freq_cputime 60 -ts_checkpoint_path checkpoint -options_file $tdhome/options/ridgecrest.cfg > $setup_dir/messages_$branch_n.log &
# mpiexec -bind-to core -n 80 $tandem_aging $setup_dir/parameters_reference_bigDc.toml --petsc -options_file $tdhome/options/ridgecrest.cfg -ts_checkpoint_freq_step 100 -ts_checkpoint_freq_physical_time 1000000000 -ts_checkpoint_freq_cputime 60 -ts_checkpoint_path checkpoint > $setup_dir/messages_$branch_n.log &
# mpiexec -bind-to core -n 80 $tandem_latest_slip $setup_dir/parameters_sliplaw_reference.toml --petsc -ts_checkpoint_path checkpoint -ts_checkpoint_storage_type unlimited -ts_checkpoint_freq_step 50 -ts_checkpoint_freq_physical_time 1000000000 -ts_checkpoint_freq_cputime 60 -options_file $tdhome/options/ridgecrest_sliplaw.cfg > $setup_dir/messages_$branch_n.log &
# mpiexec -bind-to core -n 10 $tandem_latest_slip $setup_dir/parameters_tmp.toml --petsc -ts_checkpoint_storage_type none -options_file $tdhome/options/ridgecrest.cfg

# --- Load checkpointing
# mpiexec -bind-to core -n 10 $tandem_aging $setup_dir/parameters_reference_lowres.toml --petsc -ts_checkpoint_load ../lowres_spinup_aginglaw_reference/outputs/checkpoint/step84100 -ts_checkpoint_path checkpoint -ts_checkpoint_freq_step 50 -ts_checkpoint_freq_physical_time 3153600000 -ts_checkpoint_freq_cputime 60 -options_file $tdhome/options/ridgecrest.cfg > $setup_dir/messages_$branch_n.log &
# mpiexec -bind-to core -n 40 $tandem_aging $setup_dir/parameters_reference_diffwavelength.toml --petsc -ts_checkpoint_load ../diffwavelength_1/outputs/checkpoint/step708000 -ts_checkpoint_path checkpoint -ts_checkpoint_freq_step 100 -ts_checkpoint_freq_physical_time 3153600000 -ts_checkpoint_freq_cputime 60 -options_file $tdhome/options/ridgecrest.cfg > $setup_dir/messages_$branch_n.log &
# mpiexec -bind-to core -n 40 $tandem_aging $setup_dir/parameters_reference_slowVpl.toml --petsc -ts_checkpoint_load  ../correct_slowVpl_reference/outputs/checkpoint/step1199700 -ts_checkpoint_path checkpoint -ts_checkpoint_freq_step 100 -ts_checkpoint_freq_physical_time 3153600000 -ts_checkpoint_freq_cputime 60 -options_file $tdhome/options/ridgecrest.cfg > $setup_dir/messages_$branch_n.log &
# mpiexec -bind-to core -n 80 $tandem_latest_slip $setup_dir/parameters_sliplaw_reference.toml --petsc -ts_checkpoint_load ../spinup_sliplaw_reference_1/outputs/checkpoint/step19450 -ts_checkpoint_storage_type unlimited -ts_checkpoint_freq_step 50 -ts_checkpoint_freq_physical_time 3153600000 -ts_checkpoint_freq_cputime 60 -options_file $tdhome/options/ridgecrest.cfg > $setup_dir/messages_$branch_n.log &
# mpiexec -bind-to core -n 80 $tandem_aging $setup_dir/parameters_hf10_reference.toml --petsc -ts_checkpoint_load ../hf10_reference_5/outputs/checkpoint/step9720750 -ts_checkpoint_freq_step 100 -ts_checkpoint_freq_physical_time 3153600000 -ts_checkpoint_freq_cputime 60 -ts_checkpoint_path checkpoint -options_file $tdhome/options/ridgecrest.cfg > $setup_dir/messages_$branch_n.log &
# mpiexec -bind-to core -n 40 tandem $setup_dir/parameters_reference.toml --petsc -ts_checkpoint_load ../reference/outputs/checkpoint/step1555650 -ts_max_steps 1555660 -ts_checkpoint_freq_step 50 -ts_checkpoint_freq_physical_time 1000000000 -ts_checkpoint_freq_cputime 120 -options_file $tdhome/options/ridgecrest.cfg > $setup_dir/messages_$branch_n.log &
# With a fixed time step:
# mpiexec -bind-to core -n 40 tandem $setup_dir/parameters_reference.toml --petsc -ts_checkpoint_load ../reference/outputs/checkpoint/step1555650 -ts_adapt_type none -ts_dt 0.01 -ts_max_steps 1555660 -ts_checkpoint_freq_step 50 -ts_checkpoint_freq_physical_time 1000000000 -ts_checkpoint_freq_cputime 120 -options_file $tdhome/options/ridgecrest.cfg > $setup_dir/messages_$branch_n.log &

# mpiexec -bind-to core -n 40 tandem $setup_dir/parameters_nopert.toml --petsc -ts_checkpoint_load ../match31/outputs/checkpoint/step4915642 -ts_max_steps 4915672 -ts_checkpoint_freq_step 1000000 -ts_checkpoint_freq_cputime 10000000000 -ts_checkpoint_freq_physical_time 1000000000000 -options_file $tdhome/options/ridgecrest.cfg > $setup_dir/messages_$branch_n.log &
# mpiexec -bind-to core -n 40 tandem $setup_dir/parameters_reference.toml --petsc -ts_checkpoint_load ../diverge_test_ref1/outputs/checkpoint/step4650 -ts_max_steps 5000 -ts_checkpoint_freq_step 1000000 -ts_checkpoint_freq_cputime 10000000000 -ts_checkpoint_freq_physical_time 1000000000000 -options_file $tdhome/options/ridgecrest.cfg > $setup_dir/messages_$branch_n.log &

# --- Turn off checkpointing
# mpiexec -bind-to core -n 80 $tandem_latest_slip $setup_dir/parameters_sliplaw_debug.toml --petsc -ts_checkpoint_storage_type none -options_file $tdhome/options/ridgecrest_sliplaw.cfg > $setup_dir/messages_$branch_n.log &
# mpiexec -bind-to core -n 80 $tandem_latest_slip $setup_dir/build_GF.toml --petsc -ts_checkpoint_storage_type none -options_file $tdhome/options/ridgecrest.cfg > $setup_dir/messages_$branch_n.log &
# mpiexec -bind-to core -n 60 tandem $setup_dir/build_GF.toml --petsc -ts_checkpoint_storage_type none -options_file $tdhome/options/ridgecrest.cfg > $setup_dir/messages_$branch_n.log &

# --- Stale) Base command
# mpiexec -bind-to core -n 5 tandem $setup_dir/parameters_$branch_n.toml --petsc -options_file $tdhome/options/ridgecrest.cfg > $setup_dir/messages_$branch_n.log &
# --- Stale) MTMOD model
# mpiexec -bind-to core -n 40 tandem $setup_dir/parameters_reference.toml --petsc -options_file $tdhome/options/ridgecrest.cfg -ts_adapt_dt_max 5e5 > $setup_dir/messages_$branch_n.log &
