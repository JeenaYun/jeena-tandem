model_n=include_lam
branch_n=v6_Dc2_DZ
setup_dir=$tdhome/$model_n
output_dir=$SCRATCH/$model_n/$branch_n/outputs
export param_file=$setup_dir/p25v6Dc2DZ.toml
n_nodes=40
mkdir -p $output_dir

sbatch -J $branch_n -o $setup_dir/messages_%x.log -e $setup_dir/messages_%x.err --chdir=$output_dir --nodes=$n_nodes run_Tandem_supermuc.sh
