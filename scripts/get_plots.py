#!/usr/bin/env python3
'''
An executable plotting script for Tandem to save figures directly from a remote server
By Jeena Yun
Update note: added color bar off feature
Last modification: 2024.04.02.
'''
import argparse
import setup_shortcut

sc = setup_shortcut.setups()

yr2sec = 365*24*60*60
wk2sec = 7*24*60*60

# Set input parameters -------------------------------------------------------------------------------------------------------------------
parser = argparse.ArgumentParser()
parser.add_argument("save_dir", help=": directory to output files and to save plots")
parser.add_argument("-c","--compute", action="store_true", help=": Activate only when you want to compute")
parser.add_argument("-ot","--output_type", type=str.lower, choices=['fault_probe','fault'], help=": Type of on-fault output to process ['fault_probe','fault']",default='fault_probe')

# Fault output vs. time at certain depth
parser.add_argument("-sr","--sliprate", type=float, help=": If used, depth of slip rate vs. time plot [km]", default=0)
parser.add_argument("-sl","--slip", type=float, help=": If used, depth of slip vs. time plot [km]", default=0)
parser.add_argument("-st","--stress", type=float, help=": If used, depth of stress vs. time plot [km]", default=0)
parser.add_argument("-sv","--state_var", type=float, help=": If used, depth of state variable vs. time plot [km]", default=0)
parser.add_argument("-sec","--plot_in_sec", action="store_true", help=": Time axis in seconds",default=False)

# Input variable profile
parser.add_argument("-ist","--stressprof", action="store_true", help=": ON/OFF in & out stress profile")
parser.add_argument("-ab","--abprof", action="store_true", help=": ON/OFF in & out a-b profile")
parser.add_argument("-dc","--dcprof", action="store_true", help=": ON/OFF in & out Dc profile")

# Fault output image
parser.add_argument("-im","--image", type=str, choices=['sliprate','shearT','delshearT','normalT','delnormalT','state_var'], help=": Type of image plot ['sliprate','shearT','normalT','state_var']")
parser.add_argument("-ts","--plot_in_timestep", action="store_true", help=": Time axis in timesteps",default=False)
parser.add_argument("-zf","--zoom_frame", nargs='+', type=int, help=": When used, event indexes or timestep ranges you want to zoom in",default=[])
parser.add_argument("-vmin","--vmin", type=float, help=": vmin for the plot")
parser.add_argument("-vmax","--vmax", type=float, help=": vmax for the plot")
parser.add_argument("-cboff","--colorbar_off", action="store_true", help=": Turn OFF colorbar from the figure",default=False)

# Cumulative slip profile related paramters
parser.add_argument("-csl","--cumslip", action="store_true", help=": ON/OFF cumulative slip profile")
parser.add_argument("-dtcr","--dt_creep", type=float, help=": Contour interval for CREEPING section [yr]")
parser.add_argument("-dtco","--dt_coseismic", type=float, help=": Contour interval for COSEISMIC section [s]")
parser.add_argument("-dtint","--dt_interm", type=float, help=": Contour interval for INTERMEDIATE section [wk]")
parser.add_argument("-Vths","--Vths", type=float, help=": Slip-rate threshold to define coseismic section [m/s]")
parser.add_argument("-Vlb","--Vlb", type=float, help=": When used with --Vths becomes lower bound of slip rate of intermediate section [m/s]")
parser.add_argument("-srvar","--SRvar", type=float, help=": Criterion for SR variation within a detected event")
parser.add_argument("-dd","--depth_dist", action="store_true", help=": Plot cumslip plot with hypocenter depth distribution",default=False)
parser.add_argument("-abio","--ab_inout", action="store_true", help=": Plot cumslip plot with a-b profile",default=False)
parser.add_argument("-stio","--stress_inout", action="store_true", help=": Plot cumslip plot with stress profile",default=False)
parser.add_argument("-dcio","--dc_inout", action="store_true", help=": Plot cumslip plot with Dc profile",default=False)
# parser.add_argument("-spup","--spin_up", type=float, help=": Plot with spin-up after given slip amount",default=0)
parser.add_argument("-spup","--spin_up", nargs=2, type=str, help=": Plot with spin-up after given amount of quantity",default=[])
parser.add_argument("-rths","--rths", type=float, help=": Rupture length threshold to define system wide event [m]")
parser.add_argument("-ct","--cuttime", type=float, help=": Show result up until to the given time to save computation time [yr]", default=0)
parser.add_argument("-mg","--mingap", type=float, help=": Minimum seperation time between two different events [s]", default=60)

# Miscellaneous plots
parser.add_argument("-evan","--ev_anal", action="store_true", help=": ON/OFF event analyzation plot")
parser.add_argument("-stf","--STF", action="store_true", help=": ON/OFF STF plot")
parser.add_argument("-M0","--M0", type=str.lower, choices=['1d','approx2d'], help=": Produce M0 plot of your choice ['1d','approx2d']")
parser.add_argument("-Mw","--Mw", action="store_true", help="When used with --M0, plots output in Mw scale")
parser.add_argument("-gr","--GR", nargs='+', type=float, help="Returns Gutenberg-Richter relation. Cutoff magnitude and number of points are required")
parser.add_argument("-u","--displacement", type=str.lower, choices=['x','t'], help=": Plots displacement as a function of distance (x) or time (t)")

# Whether this figure is for publishing
parser.add_argument("-pub","--publish", action="store_true", help="Generate figure for publishing purpose (without version names)",default=False)

# Whether this figure is for publishing
parser.add_argument("-hsize","--horz_size", type=float, help="Horizontal size of the figure frame",default=None)
parser.add_argument("-vsize","--vert_size", type=float, help="Vertical size of the figure frame",default=None)

args = parser.parse_args()

def get_cumslip_outputs(save_dir,outputs,dep,cuttime,Vlb,Vths,dt_creep,dt_coseismic,dt_interm,SRvar,rths):
    import os
    branch_name = save_dir.split('/')[-1]
    raw_dir = save_dir.replace(branch_name,'')
    model_tag = sc.tandem_modeltag(branch_name)[0]
    if model_tag != 'reference':
        cumslip_dir = raw_dir+model_tag
    else:
        cumslip_dir = raw_dir+'reference'
    exist_cumslip = os.path.exists('%s/cumslip_outputs_Vths_%1.0e_srvar_%03d_rths_%d_tcreep_%d_tseis_%02d.npy'%(cumslip_dir,Vths,SRvar*100,rths,dt_creep/yr2sec,dt_coseismic*10))
    if not exist_cumslip or 'pert' in branch_name:
        from cumslip_compute import compute_cumslip,compute_spinup
        print('No existing file - compute cumslip outputs')
        cumslip_outputs = compute_cumslip(outputs,dep,cuttime,Vlb,Vths,dt_creep,dt_coseismic,dt_interm,SRvar)
        if outputs[0,-1,0]-outputs[0,0,0] > 200*yr2sec:
            print('Compute spin-up index')
            spin_up_idx = compute_spinup(outputs,dep,cuttime,cumslip_outputs,['yrs',200],rths)[-1]
        else:
            print('Too short to spin-up - skip')
            spin_up_idx = 0
        if not 'pert' in branch_name:
            np.save('%s/cumslip_outputs_Vths_%1.0e_srvar_%03d_rths_%d_tcreep_%d_tseis_%02d.npy'%(cumslip_dir,Vths,SRvar*100,rths,dt_creep/yr2sec,dt_coseismic*10),cumslip_outputs)
            np.save('%s/spin_up_idx_Vths_%1.0e_srvar_%03d_rths_%d_tcreep_%d_tseis_%02d.npy'%(cumslip_dir,Vths,SRvar*100,rths,dt_creep/ch.yr2sec,dt_coseismic*10),spin_up_idx)
    else:
        from read_outputs import load_cumslip_outputs
        cumslip_outputs,_ = load_cumslip_outputs(cumslip_dir,Vths=Vths,SRvar=SRvar,rths=rths,dt_creep=dt_creep,dt_coseismic=dt_coseismic)
    return cumslip_outputs

# --- Check dependencies
if args.cumslip or args.ev_anal or args.STF or args.image or args.M0 or args.GR:        # When args.cumslip are true
    default_vmin,default_vmax,default_Vths,default_SRvar,_,_,_,default_rths,default_dt_creep,default_dt_coseismic = sc.base_event_criteria(args.save_dir)
    if not args.dt_creep:
        parser.error('Required field \'dt_creep\' is not defined - check again')
    if not args.dt_coseismic:
        parser.error('Required field \'dt_coseismic\' is not defined - check again')
    if not args.Vths:
        print('Required field \'Vths\' not defined - using default value %g m/s'%(default_Vths))
        args.Vths = default_Vths
    if args.SRvar is None:
        print('Field \'SRvar\' not defined - using default value %g'%(default_SRvar))
        args.SRvar = default_SRvar
    if args.rths is None:
        print('Field \'rths\' not defined - using default value %d'%(default_rths))
        args.rths = default_rths
    dt_creep = args.dt_creep*yr2sec
    dt_coseismic = args.dt_coseismic
    if args.dt_interm:
        dt_interm = args.dt_interm*wk2sec
        if not args.Vlb:
            print('Required field \'Vlb\' not defined - using default value 1e-8 m/s')
            args.Vlb = 1e-8
    else:
        dt_interm = 0
        args.Vlb = 0

save_dir = args.save_dir
if 'models' in save_dir: # local
    prefix = save_dir.split('models/')[-1]
elif 'di75weg' in save_dir: # supermuc
    prefix = save_dir.split('di75weg/')[-1]
elif 'jyun' in save_dir: # LMU server
    prefix = save_dir.split('jyun/')[-1]

cuttime = args.cuttime*yr2sec

if args.publish:
    print('Figure version: publish')

# Extract data ---------------------------------------------------------------------------------------------------------------------------
from read_outputs import *
if args.compute:
    print('Compute on - extract outputs')
    if args.output_type == 'fault_probe':
        outputs,dep,params = read_fault_probe_outputs(save_dir)
    elif args.output_type == 'fault':
        outputs,dep,params = read_fault_outputs(save_dir)
else:
    if args.output_type == 'fault_probe':
        outputs,dep,params = load_fault_probe_outputs(save_dir)
    elif args.output_type == 'fault':
        outputs,dep,params = load_fault_outputs(save_dir)

# Cumslip vs. Depth ----------------------------------------------------------------------------------------------------------------------
if args.cumslip:
    from cumslip_plot import *
    cumslip_outputs = get_cumslip_outputs(save_dir,outputs,dep,cuttime,args.Vlb,args.Vths,dt_creep,dt_coseismic,dt_interm,args.SRvar,args.rths)

    # --- Plot the result
    if len(args.spin_up) > 0:
        from cumslip_compute import compute_spinup
        spup_cumslip_outputs = compute_spinup(outputs,dep,cuttime,cumslip_outputs,args.spin_up,args.rths)
        spup_where(save_dir,prefix,cumslip_outputs,spup_cumslip_outputs,args.Vths,dt_coseismic,args.rths,args.publish)
    else:
        spup_cumslip_outputs = None

    if sum([args.ab_inout,args.stress_inout,args.dc_inout,args.depth_dist]) == 0:
        only_cumslip(save_dir,prefix,cumslip_outputs,args.Vths,dt_coseismic,args.rths,spup_cumslip_outputs,args.publish)
    elif sum([args.ab_inout,args.stress_inout,args.dc_inout,args.depth_dist]) == 1:
        two_set(save_dir,prefix,outputs,dep,cumslip_outputs,args.Vths,dt_coseismic,args.depth_dist,args.ab_inout,args.stress_inout,args.dc_inout,args.rths,spup_cumslip_outputs,args.publish)
    elif sum([args.ab_inout,args.stress_inout,args.dc_inout,args.depth_dist]) == 2:
        three_set(save_dir,prefix,outputs,dep,cumslip_outputs,args.Vths,dt_coseismic,args.depth_dist,args.ab_inout,args.stress_inout,args.dc_inout,args.rths,spup_cumslip_outputs,args.publish)

# Fault output image ---------------------------------------------------------------------------------------------------------------------
if args.image:
    from faultoutputs_image import fout_image
    if not args.vmin:                       # No vmin defined
        if args.image == 'sliprate':
            try:
                vmin = params.item().get('Vp')*1e-3
            except:
                vmin = default_vmin
            print('vmin not defined - using default value %g [m/s]'%(vmin))
        elif args.image == 'delshearT':
            print('vmin not defined - using default value -5 [MPa]')
            vmin = -5
        elif args.image == 'delnormalT':
            print('vmin not defined - using default value -1 [MPa]')
            vmin = -1
        else:
            vmin = None
    else:
        vmin = args.vmin
    if not args.vmax:                       # No vmax defined
        if args.image == 'sliprate':
            print('vmax not defined - using default value %g [m/s]'%(default_vmax))
            vmax = default_vmax
        elif args.image == 'delshearT':
            print('vmax not defined - using default value 5 [MPa]')
            vmax = 5
        elif args.image == 'delnormalT':
            print('vmax not defined - using default value 1 [MPa]')
            vmax = 1
        else:
            vmax = None
    else:
        vmax = args.vmax
    if not args.horz_size: args.horz_size = 20.6
    if not args.vert_size: args.vert_size = 11
    if not 'cumslip_outputs' in locals():   # No event outputs computed
        # cumslip_outputs = get_cumslip_outputs(save_dir,None,None,cuttime,args.Vlb,args.Vths,dt_creep,dt_coseismic,dt_interm,args.SRvar,args.rths)
        cumslip_outputs = get_cumslip_outputs(save_dir,outputs,dep,cuttime,args.Vlb,args.Vths,dt_creep,dt_coseismic,dt_interm,args.SRvar,args.rths)
    fout_image(args.image,outputs,dep,params,cumslip_outputs,save_dir,prefix,args.rths,vmin,vmax,args.Vths,args.zoom_frame,args.horz_size,args.vert_size,args.plot_in_timestep,args.plot_in_sec,args.colorbar_off,args.publish)

# Miscellaneous --------------------------------------------------------------------------------------------------------------------------
if args.ev_anal:
    from misc_plots import plot_event_analyze
    if not 'cumslip_outputs' in locals():
        cumslip_outputs = get_cumslip_outputs(save_dir,outputs,dep,cuttime,args.Vlb,args.Vths,dt_creep,dt_coseismic,dt_interm,args.SRvar,args.rths)
    plot_event_analyze(save_dir,prefix,cumslip_outputs,args.rths,args.publish)

if args.STF:
    from misc_plots import plot_STF
    if not 'cumslip_outputs' in locals():
        cumslip_outputs = get_cumslip_outputs(save_dir,outputs,dep,cuttime,args.Vlb,args.Vths,dt_creep,dt_coseismic,dt_interm,args.SRvar,args.rths)

    if len(args.spin_up) > 0:
        if not 'spin_up_idx' in locals():
            from cumslip_compute import compute_spinup
            spin_up_idx = compute_spinup(outputs,dep,cuttime,cumslip_outputs,args.spin_up,args.rths)[-1]
    else:
        spin_up_idx = 0
    plot_STF(save_dir,outputs,dep,cumslip_outputs,spin_up_idx,args.rths)

if args.M0:
    from misc_plots import plot_M0
    if not 'cumslip_outputs' in locals():
        cumslip_outputs = get_cumslip_outputs(save_dir,outputs,dep,cuttime,args.Vlb,args.Vths,dt_creep,dt_coseismic,dt_interm,args.SRvar,args.rths)

    if len(args.spin_up) > 0:
        if not 'spin_up_idx' in locals():
            from cumslip_compute import compute_spinup
            spin_up_idx = compute_spinup(outputs,dep,cuttime,cumslip_outputs,args.spin_up,args.rths)[-1]
    else:
        spin_up_idx = 0
    plot_M0(save_dir,cumslip_outputs,spin_up_idx,args.rths,args.M0,args.Mw)

if args.GR:
    cutoff_Mw = args.GR[0]
    if len(args.GR) == 1:
        print('Field npts not defined - using default value 50')
        npts = 50
    else:
        npts = args.GR[1]
    from misc_plots import plot_GR
    if not 'cumslip_outputs' in locals():
        cumslip_outputs = get_cumslip_outputs(save_dir,outputs,dep,cuttime,args.Vlb,args.Vths,dt_creep,dt_coseismic,dt_interm,args.SRvar,args.rths)

    if len(args.spin_up) > 0:
        if not 'spin_up_idx' in locals():
            from cumslip_compute import compute_spinup
            spin_up_idx = compute_spinup(outputs,dep,cuttime,args.rths,cumslip_outputs,args.spin_up,args.rths)[-1]
    else:
        spin_up_idx = 0
    plot_GR(save_dir,prefix,cumslip_outputs,spin_up_idx,args.rths,cutoff_Mw,npts,args.publish)

if args.displacement:
    import os
    if os.path.exists('%s/domain_probe_outputs.npy'%(save_dir)):
        dp_outputs,xyloc = load_domain_probe_outputs(save_dir)
    else:
        print('%s/domain_probe_outputs.npy not found - compute domain probe outputs'%(save_dir))
        dp_outputs,xyloc = read_domain_probe_outputs(save_dir)
    from misc_plots import plot_displacements
    plot_displacements(save_dir,dp_outputs,xyloc,args.displacement)

# Input variable profile -----------------------------------------------------------------------------------------------------------------
if args.stressprof:
    from stress_profile import plot_stress_vs_depth
    plot_stress_vs_depth(save_dir,prefix,outputs,dep)

if args.abprof:
    from ab_profile import plot_ab_vs_depth
    plot_ab_vs_depth(save_dir,prefix)

if args.dcprof:
    from Dc_profile import plot_Dc_vs_depth
    plot_Dc_vs_depth(save_dir,prefix)

# Fault output vs. time at certain depth -------------------------------------------------------------------------------------------------
if abs(args.sliprate)>0:
    from faultoutputs_vs_time import fout_time
    # from faultoutputs_vs_time import sliprate_time
    # sliprate_time(save_dir,outputs,dep,args.sliprate,args.plot_in_sec)
    fout_time(save_dir,outputs,dep,target_depth=args.sliprate,target_var='sliprate',plot_in_sec=args.plot_in_sec)
    
if abs(args.slip)>0:
    from faultoutputs_vs_time import fout_time
    # from faultoutputs_vs_time import slip_time
    # slip_time(save_dir,outputs,dep,args.slip,args.plot_in_sec)
    fout_time(save_dir,outputs,dep,target_depth=args.slip,target_var='slip',plot_in_sec=args.plot_in_sec)
    
if abs(args.stress)>0:
    from faultoutputs_vs_time import fout_time
    # from faultoutputs_vs_time import stress_time
    # stress_time(save_dir,outputs,dep,args.stress,args.plot_in_sec)
    fout_time(save_dir,outputs,dep,target_depth=args.stress,target_var='shearT',plot_in_sec=args.plot_in_sec)
    fout_time(save_dir,outputs,dep,target_depth=args.stress,target_var='normalT',plot_in_sec=args.plot_in_sec)

if abs(args.state_var)>0:
    from faultoutputs_vs_time import fout_time
    # from faultoutputs_vs_time import state_time
    # state_time(save_dir,outputs,dep,args.state_var,args.plot_in_sec)
    fout_time(save_dir,outputs,dep,target_depth=args.state_var,target_var='state',plot_in_sec=args.plot_in_sec)
