#!/bin/bash
# Job Name and Files (also --job-name)

#Notification and type
#SBATCH --mail-type=END
#SBATCH --mail-user=j4yun@ucsd.edu

# Wall clock limit:
#SBATCH --time=24:00:00
#SBATCH --no-requeue

#Setup of execution environment
#SBATCH --export=ALL
#SBATCH --account=pn49ha
#constraints are optional
#--constraint="scratch&work"
#SBATCH --partition=general

#SBATCH --ear=off

#Number of nodes and MPI tasks per node:
#SBATCH --ntasks-per-node=1

#Run the program:
export OMP_NUM_THREADS=1

source /etc/profile.d/modules.sh
echo 'num_nodes:' $SLURM_JOB_NUM_NODES 'ntasks:' $SLURM_NTASKS 'cpus_per_task:' $SLURM_CPUS_PER_TASK
ulimit -Ss 2097152

mpiexec -n $SLURM_NTASKS tandem $param_file --petsc -options_file $tdhome/../options/lu_mumps.cfg -options_file $tdhome/../options/rk45.cfg -ts_monitor
