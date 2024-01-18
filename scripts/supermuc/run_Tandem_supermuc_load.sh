#!/bin/bash
# Job Name and Files (also --job-name)

#Notification and type
#SBATCH --mail-type=END
#SBATCH --mail-user=j4yun@ucsd.edu

# Wall clock limit:
#SBATCH --time=00:30:00
#SBATCH --no-requeue

#Setup of execution environment
#SBATCH --export=ALL
#SBATCH --account=pn49ha
#constraints are optional
#--constraint="scratch&work"
#SBATCH --partition=test

#SBATCH --ear=off

#Number of nodes and MPI tasks per node:
#SBATCH --ntasks-per-node=1

#Run the program:
export OMP_NUM_THREADS=1

source /etc/profile.d/modules.sh
echo 'num_nodes:' $SLURM_JOB_NUM_NODES 'ntasks:' $SLURM_NTASKS 'cpus_per_task:' $SLURM_CPUS_PER_TASK
ulimit -Ss 2097152

# -- Checkpoint load
mpiexec -n $SLURM_NTASKS tandem $param_file --petsc -ts_checkpoint_load $load_from -ts_checkpoint_path checkpoint -ts_checkpoint_storage_type unlimited -ts_checkpoint_freq_step $ckp_f_step -ts_checkpoint_freq_physical_time $ckp_f_ptime -ts_checkpoint_freq_cputime $ckp_f_ctime  -options_file $tdhome/../options/lu_mumps.cfg -options_file $tdhome/../options/rk45.cfg -ts_monitor -ts_max_steps 500
