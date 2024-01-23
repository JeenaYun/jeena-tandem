model_n=depth_dep_sn
branch_n=scale_test_90_2
setup_dir=$WORK/$model_n
output_dir=$SCRATCH/$model_n/$branch_n/outputs
export param_file=$setup_dir/scale_test.toml
n_nodes=15
n_tasks_per_node=6
mkdir -p $output_dir

sbatch -J $branch_n -o $setup_dir/messages_%x.log -e $setup_dir/messages_%x.err --chdir=$output_dir --nodes=$n_nodes --ntasks-per-node=$n_tasks_per_node run_Tandem_supermuc_ckpoff.sh
