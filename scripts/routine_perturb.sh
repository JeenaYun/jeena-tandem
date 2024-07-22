#!/bin/bash
# Define some useful functions
process_output_full() { echo "/export/dump/jyun/$1/$2"; mkdir -p "/export/dump/jyun/$1/$2"; mv "/export/dump/jyun/$1/outputs_$2" "/export/dump/jyun/$1/$2"; mv "/export/dump/jyun/$1/$2/outputs_$2" "/export/dump/jyun/$1/$2/outputs"; python /home/jyun/Tandem/get_plots.py /export/dump/jyun/$1/$2 -c; }
read_time_full() { /home/jyun/Tandem/read_time_recursive "/export/dump/jyun/$1/$2"; }
existckp_full() { ls "/export/dump/jyun/$1/$2"; }
tandem_aging='/home/jyun/softwares/project-tandem/build-cp-test-complete/app/tandem'
tandem_latest_slip='/home/jyun/softwares/project-tandem/build-tsckp-slip/app/tandem'

model_n=perturb_stress
tdhome=/home/jyun/Tandem
setup_dir=$tdhome/$model_n

# Run the after perturbation period
branch_n=continue_after_pert8_vs340_262800h
cd /export/dump/jyun/$model_n
mkdir -p outputs_$branch_n
cd outputs_$branch_n
echo "Tandem running in a directory: " $setup_dir

# Safety check
existckp_full $model_n first_after_pert8_vs340_262800h/outputs/checkpoint/step1516300

# If safe, proceed
mpiexec -bind-to core -n 40 $tandem_aging $setup_dir/parameters_perturb_scenario.toml --final_time 2.869780394139096e+10 --petsc -ts_checkpoint_load ../first_after_pert8_vs340_262800h/outputs/checkpoint/step1516300 -ts_adapt_type basic -ts_checkpoint_path checkpoint -ts_checkpoint_freq_step 100 -ts_checkpoint_freq_physical_time 10000000000 -ts_checkpoint_freq_cputime 60 -options_file $tdhome/options/ridgecrest.cfg > $setup_dir/messages_$branch_n.log &

# Finally, Process the after perturbation period output, change the directory name, and generate checkpoint time info
# process_output_full $model_n $branch_n
# read_time_full $model_n $branch_n

