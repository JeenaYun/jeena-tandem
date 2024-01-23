model_n=depth_dep_sn
branch_n=reference
setup_dir=$WORK/$model_n
output_dir=$SCRATCH/$model_n/$branch_n/outputs
echo $output_dir
export param_file=$setup_dir/parameters_reference.toml
export ckp_f_step=50
export ckp_f_ptime=1000000000
export ckp_f_ctime=10
n_nodes=17
n_tasks_per_node=6
mkdir -p $output_dir

sbatch -J $branch_n -o $setup_dir/messages_%x.log -e $setup_dir/messages_%x.err --chdir=$output_dir --nodes=$n_nodes --ntasks-per-node=$n_tasks_per_node run_Tandem_supermuc_write.sh
