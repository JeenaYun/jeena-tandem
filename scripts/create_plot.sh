model_n=perturb_stress
branch_n=after_pert8_vs340_262800h
save_dir=/export/dump/jyun/$model_n/$branch_n
echo $save_dir
mkdir -p $save_dir
mv /export/dump/jyun/$model_n/outputs_$branch_n $save_dir
mv $save_dir/outputs_$branch_n $save_dir/outputs

# python get_plots.py $save_dir -c #> messages/compute_$branch_n.log &
# python get_plots.py $save_dir -dtcr 2 -dtco 0.5 -Vths 0.2 -im delnormalT -sec -pub -vmin -1 -vmax 1
# python get_plots.py $save_dir -dtcr 2 -dtco 0.5 -Vths 0.2 -im delshearT -sec -pub -vmin -1 -vmax 1
# python get_plots.py $save_dir -dtcr 2 -dtco 0.5 -Vths 0.2 -im delshearT -ts -pub -vmin -20 -vmax 20
# python get_plots.py $save_dir -dtcr 2 -dtco 0.5 -Vths 0.2 -im state_var -sec -pub
# python get_plots.py $save_dir -dtcr 2 -dtco 0.5 -Vths 0.2 -ist -ab -dc -gr 0 -u t > $model_n/getplot_$branch_n.log &
# python get_plots.py $save_dir -dc
# python get_plots.py $save_dir -dtcr 2 -dtco 0.5 -Vths 0.2 -im sliprate -sec -hsize 40 -pub
# python get_plots.py $save_dir -dtcr 2 -dtco 0.5 -Vths 0.2 -im sliprate -ts -hsize 40 -pub
# python get_plots.py $save_dir -dtcr 2 -dtco 0.5 -Vths 0.2 -im sliprate -ts -zf 850000 930000 -pub
# python get_plots.py $save_dir -dtcr 2 -dtco 0.5 -Vths 0.2 -im sliprate -ts -zf 275000 310000 -pub
# python get_plots.py $save_dir -dtcr 2 -dtco 0.5 -Vths 0.2 -im sliprate -sec -zf 280 282 50000 100 -pub
# python get_plots.py $save_dir -dtcr 2 -dtco 0.5 -Vths 0.2 -csl -pub
# python get_plots.py $save_dir -dtcr 2 -dtco 0.5 -Vths 0.2 -im sliprate -ts -pub -vmin 3.2e-14
python get_plots.py $save_dir -c -dtcr 2 -dtco 0.5 -Vths 0.2 -im sliprate -ts -pub
# python get_plots.py $save_dir -dtcr 2 -dtco 0.5 -Vths 0.2 -im sliprate -ts -pub
# python get_plots.py $save_dir -dtcr 2 -dtco 0.5 -Vths 0.2 -im delnormalT -ts -pub -vmin -1 -vmax 1
# python get_plots.py $save_dir -dtcr 2 -dtco 0.5 -Vths 0.2 -im delshearT -ts -pub -vmin -1 -vmax 1