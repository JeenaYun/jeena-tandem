model_n=perturb_stress
# branch_n=pert6_vs340_lowres_spinup_sliplaw_reference
branch_n=after_pert18_vs340_lowres_spinup_aginglaw_reference
save_dir=/export/dump/jyun/$model_n/$branch_n
echo $save_dir
mkdir -p $save_dir
mv /export/dump/jyun/$model_n/outputs_$branch_n $save_dir
mv $save_dir/outputs_$branch_n $save_dir/outputs

# python get_plots.py $save_dir -c #> messages/compute_$branch_n.log &
# python get_plots.py $save_dir -dtcr 2 -dtco 0.5 -Vths 0.2 -im delnormalT -sec
# python get_plots.py $save_dir -dtcr 2 -dtco 0.5 -Vths 0.2 -ist -ab -dc -gr 0 -u t > $model_n/getplot_$branch_n.log &
# python get_plots.py $save_dir -dc
# python get_plots.py $save_dir -dtcr 2 -dtco 0.5 -Vths 0.2 -im sliprate -sec -hsize 40 -pub
# python get_plots.py $save_dir -dtcr 2 -dtco 0.5 -Vths 0.2 -im sliprate -ts -hsize 40 -pub
# python get_plots.py $save_dir -dtcr 2 -dtco 0.5 -Vths 0.2 -im sliprate -ts -zf 0 45000 -pub
# python get_plots.py $save_dir -dtcr 2 -dtco 0.5 -Vths 0.2 -im sliprate -ts -zf 0 1700 -pub
# python get_plots.py $save_dir -dtcr 2 -dtco 0.5 -Vths 0.2 -im sliprate -zf 117 120 1000 1000 -pub
# python get_plots.py $save_dir -dtcr 2 -dtco 0.5 -Vths 0.2 -csl -pub
# python get_plots.py $save_dir -dtcr 2 -dtco 0.5 -Vths 0.2 -im sliprate -ts -pub -vmin 3.2e-14
python get_plots.py $save_dir -dtcr 2 -dtco 0.5 -Vths 0.2 -im sliprate -ts -pub
# python get_plots.py $save_dir -dtcr 2 -dtco 0.5 -Vths 0.2 -im delnormalT -ts -pub -vmin -1 -vmax 1
# python get_plots.py $save_dir -dtcr 2 -dtco 0.5 -Vths 0.2 -im delshearT -ts -pub -vmin -1 -vmax 1