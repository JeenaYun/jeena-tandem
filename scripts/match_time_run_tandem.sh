#!/bin/bash
# Define some useful functions
process_output_full() { echo "/export/dump/jyun/$1/$2"; mkdir -p "/export/dump/jyun/$1/$2"; mv "/export/dump/jyun/$1/outputs_$2" "/export/dump/jyun/$1/$2"; mv "/export/dump/jyun/$1/$2/outputs_$2" "/export/dump/jyun/$1/$2/outputs"; python /home/jyun/Tandem/get_plots.py /export/dump/jyun/$1/$2 -c; }
read_time_full() { /home/jyun/Tandem/read_time_recursive "/export/dump/jyun/$1/$2"; }
existckp_full() { ls "/export/dump/jyun/$1/$2"; }
tandem_aging='/home/jyun/softwares/project-tandem/build-cp-test-complete/app/tandem'
tandem_latest_slip='/home/jyun/softwares/project-tandem/build-tsckp-slip/app/tandem'

model_n=perturb_stress
branch_n=match8_lowres_spinup_sliplaw_reference
tdhome=/home/jyun/Tandem
setup_dir=$tdhome/$model_n
mkdir -p /export/dump/jyun/$model_n
cd /export/dump/jyun/$model_n
mkdir -p outputs_$branch_n
cd outputs_$branch_n
echo "Tandem running in a directory: " $setup_dir

# Safety check
existckp_full $model_n lowres_spinup_sliplaw_reference/outputs/checkpoint/step603800

mpiexec -bind-to core -n 80 $tandem_latest_slip $setup_dir/parameters_match_time.toml --petsc -ts_checkpoint_load ../lowres_spinup_sliplaw_reference/outputs/checkpoint/step603800 -ts_checkpoint_path checkpoint -ts_checkpoint_storage_type unlimited -ts_checkpoint_freq_step 1 -ts_checkpoint_freq_physical_time 1000000000 -ts_checkpoint_freq_cputime 60 -options_file $tdhome/options/ridgecrest.cfg > $setup_dir/messages_$branch_n.log 

# Process the output, change the directory name, and generate checkpoint time info
save_dir=/export/dump/jyun/$model_n/$branch_n
mkdir -p $save_dir
mv /export/dump/jyun/$model_n/outputs_$branch_n $save_dir
mv $save_dir/outputs_$branch_n $save_dir/outputs
read_time_full $model_n $branch_n

