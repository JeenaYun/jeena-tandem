model_n=BP1
branch_n=load350
setup_dir=$WORK/$model_n
output_dir=$SCRATCH/$model_n/$branch_n/outputs
export load_from=$SCRATCH/$model_n/reference/outputs/checkpoint/step350
export param_file=$setup_dir/bp1_sym.toml
export ckp_f_step=50
export ckp_f_ptime=1000000000
export ckp_f_ctime=10
n_nodes=10
mkdir -p $output_dir

sbatch -J $branch_n -o $setup_dir/messages_%x.log -e $setup_dir/messages_%x.err --chdir=$output_dir --nodes=$n_nodes run_Tandem_supermuc_load.sh
