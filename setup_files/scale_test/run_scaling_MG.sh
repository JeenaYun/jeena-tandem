tandem_latest_aging='/home/jyun/softwares/project-tandem/build-tsckp-aging/app/tandem'

# --------------- Single rank
# h-refinements (0 to 5 times refined)
tandem_latest_aging bp1_mg.toml --mesh_file bp1_refine2.msh --petsc -ts_max_steps 20 -ts_checkpoint_storage_type none -options_file scale_test_MG.cfg > MG/p6/messages_h2.log &
# tandem_latest_aging bp1_mg.toml --mesh_file bp1_refine5.msh --petsc -ts_max_steps 10 -ts_checkpoint_storage_type none -options_file mg_chev.cfg > MG/p6/messages_h5.log &
# p-refinements (p = 1 to 8)
# tandem_latest_aging_p8 bp1_mg.toml --mesh_file bp1_refine4.msh --petsc -ts_max_steps 20 -ts_checkpoint_storage_type none -options_file mg_chev.cfg > MG/messages_p8.log &

# --------------- Strong scale
# --- 4 times refined mesh
# mpiexec -bind-to core -n 2 $tandem_latest_aging bp1_mg.toml --mesh_file bp1_refine4.msh --petsc -ts_max_steps 20 -ts_checkpoint_storage_type none -options_file mg_chev.cfg > MG/refine4/messages_s002.log &
# mpiexec -bind-to core -n 4 $tandem_latest_aging bp1_mg.toml --mesh_file bp1_refine4.msh --petsc -ts_max_steps 20 -ts_checkpoint_storage_type none -options_file mg_chev.cfg > MG/refine4/messages_s004.log &
# mpiexec -bind-to core -n 8 $tandem_latest_aging bp1_mg.toml --mesh_file bp1_refine4.msh --petsc -ts_max_steps 20 -ts_checkpoint_storage_type none -options_file mg_chev.cfg > MG/refine4/messages_s008.log &
# mpiexec -bind-to core -n 16 $tandem_latest_aging bp1_mg.toml --mesh_file bp1_refine4.msh --petsc -ts_max_steps 20 -ts_checkpoint_storage_type none -options_file mg_chev.cfg > MG/refine4/messages_s016.log &
# mpiexec -bind-to core -n 32 $tandem_latest_aging bp1_mg.toml --mesh_file bp1_refine4.msh --petsc -ts_max_steps 20 -ts_checkpoint_storage_type none -options_file mg_chev.cfg > MG/refine4/messages_s032.log &
# mpiexec -bind-to core -n 64 $tandem_latest_aging bp1_mg.toml --mesh_file bp1_refine4.msh --petsc -ts_max_steps 20 -ts_checkpoint_storage_type none -options_file mg_chev.cfg > MG/refine4/messages_s064.log &
# mpiexec -bind-to core -n 120 $tandem_latest_aging bp1_mg.toml --mesh_file bp1_refine4.msh --petsc -ts_max_steps 20 -ts_checkpoint_storage_type none -options_file mg_chev.cfg > MG/refine4/messages_s120.log &

# --- 3 times refined mesh
# mpiexec -bind-to core -n 2 $tandem_latest_aging bp1_mg.toml --mesh_file bp1_refine3.msh --petsc -ts_max_steps 20 -ts_checkpoint_storage_type none -options_file mg_chev.cfg > MG/refine3/messages_s002.log &
# mpiexec -bind-to core -n 4 $tandem_latest_aging bp1_mg.toml --mesh_file bp1_refine3.msh --petsc -ts_max_steps 20 -ts_checkpoint_storage_type none -options_file mg_chev.cfg > MG/refine3/messages_s004.log &
# mpiexec -bind-to core -n 8 $tandem_latest_aging bp1_mg.toml --mesh_file bp1_refine3.msh --petsc -ts_max_steps 20 -ts_checkpoint_storage_type none -options_file mg_chev.cfg > MG/refine3/messages_s008.log &
# mpiexec -bind-to core -n 16 $tandem_latest_aging bp1_mg.toml --mesh_file bp1_refine3.msh --petsc -ts_max_steps 20 -ts_checkpoint_storage_type none -options_file mg_chev.cfg > MG/refine3/messages_s016.log &
# mpiexec -bind-to core -n 32 $tandem_latest_aging bp1_mg.toml --mesh_file bp1_refine3.msh --petsc -ts_max_steps 20 -ts_checkpoint_storage_type none -options_file mg_chev.cfg > MG/refine3/messages_s032.log &
# mpiexec -bind-to core -n 64 $tandem_latest_aging bp1_mg.toml --mesh_file bp1_refine3.msh --petsc -ts_max_steps 20 -ts_checkpoint_storage_type none -options_file mg_chev.cfg > MG/refine3/messages_s064.log &
# mpiexec -bind-to core -n 120 $tandem_latest_aging bp1_mg.toml --mesh_file bp1_refine3.msh --petsc -ts_max_steps 20 -ts_checkpoint_storage_type none -options_file mg_chev.cfg > MG/refine3/messages_s120.log &

# --- 2 times refined mesh
# mpiexec -bind-to core -n 2 $tandem_latest_aging bp1_mg.toml --mesh_file bp1_refine2.msh --petsc -ts_max_steps 20 -ts_checkpoint_storage_type none -options_file mg_chev.cfg > MG/refine2/messages_s002.log &
# mpiexec -bind-to core -n 4 $tandem_latest_aging bp1_mg.toml --mesh_file bp1_refine2.msh --petsc -ts_max_steps 20 -ts_checkpoint_storage_type none -options_file mg_chev.cfg > MG/refine2/messages_S004.log &
# mpiexec -bind-to core -n 8 $tandem_latest_aging bp1_mg.toml --mesh_file bp1_refine2.msh --petsc -ts_max_steps 20 -ts_checkpoint_storage_type none -options_file mg_chev.cfg > MG/refine2/messages_s008.log &
# mpiexec -bind-to core -n 16 $tandem_latest_aging bp1_mg.toml --mesh_file bp1_refine2.msh --petsc -ts_max_steps 20 -ts_checkpoint_storage_type none -options_file mg_chev.cfg > MG/refine2/messages_s016.log &
# mpiexec -bind-to core -n 32 $tandem_latest_aging bp1_mg.toml --mesh_file bp1_refine2.msh --petsc -ts_max_steps 20 -ts_checkpoint_storage_type none -options_file mg_chev.cfg > MG/refine2/messages_s032.log &
# mpiexec -bind-to core -n 64 $tandem_latest_aging bp1_mg.toml --mesh_file bp1_refine2.msh --petsc -ts_max_steps 20 -ts_checkpoint_storage_type none -options_file mg_chev.cfg > MG/refine2/messages_s064.log &
# mpiexec -bind-to core -n 120 $tandem_latest_aging bp1_mg.toml --mesh_file bp1_refine2.msh --petsc -ts_max_steps 20 -ts_checkpoint_storage_type none -options_file mg_chev.cfg > MG/refine2/messages_s120.log &

# --------------- Weak scale
# --- ~1000 elements / rank
# mpiexec -bind-to core -n 2 $tandem_latest_aging bp1_mg.toml --mesh_file bp1_refine1.msh --petsc -ts_max_steps 20 -ts_checkpoint_storage_type none -options_file mg_chev.cfg > MG/elem_per_rank_1000/messages_w002.log &
# mpiexec -bind-to core -n 7 $tandem_latest_aging bp1_mg.toml --mesh_file bp1_refine2.msh --petsc -ts_max_steps 20 -ts_checkpoint_storage_type none -options_file mg_chev.cfg > MG/elem_per_rank_1000/messages_w007.log &
# mpiexec -bind-to core -n 27 $tandem_latest_aging bp1_mg.toml --mesh_file bp1_refine3.msh --petsc -ts_max_steps 20 -ts_checkpoint_storage_type none -options_file mg_chev.cfg > MG/elem_per_rank_1000/messages_w027.log &
# mpiexec -bind-to core -n 107 $tandem_latest_aging bp1_mg.toml --mesh_file bp1_refine4.msh --petsc -ts_max_steps 20 -ts_checkpoint_storage_type none -options_file mg_chev.cfg > MG/elem_per_rank_1000/messages_w107.log &
