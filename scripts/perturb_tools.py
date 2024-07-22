#!/usr/bin/env python3
"""
Tools for comparing perturbed cycle models
Last modification: 2024.04.13.
by Jeena Yun
"""

import numpy as np
import setup_shortcut
import os
sc = setup_shortcut.setups()

class PERTURB:
    def __init__(self,branch_name):
        self.raw_dir = '/export/dump/jyun/perturb_stress/'
        self.stress_models_dir = '/home/jyun/Tandem/perturb_stress/seissol_outputs'
        self.model_tag,self.target_eventid,self.seissol_model_n,self.receivef_strike,self.multiply,self.time_diff_in_h,self.mu = sc.tandem_modeltag(branch_name)
        self.branch_name = branch_name
        self.save_dir = self.raw_dir+self.branch_name

        if self.model_tag != 'reference':
            self.cumslip_dir = self.raw_dir+self.model_tag
        else:
            self.cumslip_dir = self.raw_dir+'reference'
        
        # Parameters related to the event analyzing
        from cumslip_compute import analyze_events,compute_cumslip
        _,_,self.Vths,self.SRvar,self.Vlb,self.dt_interm,self.cuttime,self.rths,self.dt_creep,self.dt_coseismic = sc.base_event_criteria(self.cumslip_dir)

    def load_output(self,pert=None,after_pert=None,ckp_on=False,load_var=True,print_on=True,short_idx=None):
        from read_outputs import load_fault_probe_outputs,load_checkpoint_info,load_short_fault_probe_outputs
        if self.model_tag == 'reference' and 'pert' not in self.branch_name:
            start_time = np.load('%s/short_outputs_start_time.npy'%(self.save_dir))
            if after_pert is not None:
                if len(np.where(start_time<=np.min([pert.outputs[0,0,0],after_pert.outputs[0,0,0]]))[0]) > 0:
                    short_idx = np.where(start_time<=np.min([pert.outputs[0,0,0],after_pert.outputs[0,0,0]]))[0][-1]
                    # if short_idx < len(start_time)-1 and after_pert.outputs[0,-1,0] >= start_time[short_idx+1]:
                    #     print('WARNING: Output 2 and 3 are in the middle of short outputs %d and %d - loading both'%(short_idx,short_idx+1))
                    #     outputs1_1,dep1_1,params1_1 = load_short_fault_probe_outputs(self.save_dir,short_idx)
                    #     outputs1_2,dep1_2,params1_2 = load_short_fault_probe_outputs(self.save_dir,short_idx+1)
                else: 
                    short_idx = 0
            elif pert is not None:
                if len(np.where(start_time<=np.min(pert.outputs[0,0,0]))[0]) > 0:
                    short_idx = np.where(start_time<=np.min(pert.outputs[0,0,0]))[0][-1]
                else:
                    short_idx = 0
        if short_idx is None:
            self.outputs,self.dep,self.params = load_fault_probe_outputs(self.save_dir,print_on=print_on)
        else:
            self.outputs,self.dep,self.params = load_short_fault_probe_outputs(self.save_dir,short_idx,print_on=print_on)
        if ckp_on and os.path.exists(self.save_dir+'/checkpoint_info.csv'):
            if print_on: print('Load checkpoint info from ',self.save_dir+'/checkpoint_info.csv')
            self.ckp_dat = load_checkpoint_info(self.save_dir)
        if load_var:
            variables = {}
            from read_outputs import OUTPUTS
            for target_var in ['time','state','slip','shearT','sliprate','normalT']:
                var = OUTPUTS(self.outputs,self.dep,target_var)
                if self.branch_name == 'pert45_vs340':
                    if target_var == 'time':
                        var.data = var.data[143:]
                    else:
                        var.data = var.data[:,143:]
                variables[target_var] = var
            self.variables = variables

    def load_events(self,compute_on=False,save_on=True,print_on=True):
        from read_outputs import load_cumslip_outputs
        from cumslip_compute import analyze_events
        if compute_on:
            if print_on: print('Compute event details')
            from cumslip_compute import compute_cumslip,compute_spinup
            if not 'outputs' in dir(self): self.load_output()
            self.cumslip_outputs = compute_cumslip(self.outputs,self.dep,self.cuttime,self.Vlb,self.Vths,self.dt_creep,self.dt_coseismic,self.dt_interm,self.SRvar,print_on=print_on)
            if self.outputs[0,-1,0]-self.outputs[0,0,0] > 200*sc.yr2sec:
                if print_on: print('Compute spin-up index')
                self.spin_up_idx = compute_spinup(self.outputs,self.dep,self.cuttime,self.cumslip_outputs,['yrs',200],self.rths,print_on=print_on)[-1]
            else:
                if print_on: print('Too short to spin-up - skip')
                self.spin_up_idx = 0
            if save_on:
                np.save('%s/cumslip_outputs_Vths_%1.0e_srvar_%03d_rths_%d_tcreep_%d_tseis_%02d.npy'%(self.cumslip_dir,self.Vths,self.SRvar*100,self.rths,self.dt_creep/sc.yr2sec,self.dt_coseismic*10),self.cumslip_outputs)
                np.save('%s/spin_up_idx_Vths_%1.0e_srvar_%03d_rths_%d_tcreep_%d_tseis_%02d.npy'%(self.cumslip_dir,self.Vths,self.SRvar*100,self.rths,self.dt_creep/sc.yr2sec,self.dt_coseismic*10),self.spin_up_idx)
        else:
            try:
                self.cumslip_outputs,self.spin_up_idx = load_cumslip_outputs(self.cumslip_dir)
            except:
                print('No pre-saved cumslip outputs')
        self.tstart,self.tend,self.evdep = self.cumslip_outputs[0][0],self.cumslip_outputs[0][1],self.cumslip_outputs[1][1]
        self.rupture_length,self.av_slip,self.system_wide,self.partial_rupture,self.event_cluster,self.lead_fs,self.major_pr,self.minor_pr = analyze_events(self.cumslip_outputs,self.rths)

    def get_idx(self,target_eventid):
        if self.model_tag == 'reference':
            self.idx = self.system_wide[self.system_wide>=self.spin_up_idx][target_eventid]
        else:
            self.idx = target_eventid

    def print_event_details(self,target_eventid=None):
        if target_eventid is None: # perturbed events
            try:
                print('======== Event details with perturbation ========')
                print('Evdep:',self.evdep)
                print('System_wide:',self.system_wide)
                print('Event depth with perturbation:',self.evdep[self.system_wide])
            except TypeError:
                if len(self.tstart) == 0: print('No events')
        else: # reference events
            print('======== Event details without perturbation ========')
            self.get_idx(target_eventid)
            print('Event %d'%(self.idx))
            print('Event depth without perturbation: %1.2f'%(self.evdep[self.idx]))

    def load_related_ref(self):
        self.load_events(compute_on=False)
        if self.model_tag == 'reference':
            self.idx = self.system_wide[self.system_wide>=self.spin_up_idx][self.target_eventid]
        else:
            self.idx = self.target_eventid

    def load_stress_info(self,target_depth=None,print_on=True):
        from stress_model_tools import fixed_model
        if 'evdep' in dir(self) and 'idx' in dir(self): target_depth = self.evdep[self.idx]
        if target_depth is not None:
            self.peak_dynamic,self.static = fixed_model(self.save_dir,self.seissol_model_n,self.receivef_strike,target_depth,self.multiply,self.mu,print_off=not print_on)

    def get_input_dCFS(self,target_depth,dt=0.01):
        # dCFS from seissol model
        from scipy import interpolate
        # target_depth = self.evdep[self.idx]
        delPn = np.loadtxt('%s/ssaf_%s_Pn_pert_mu%02d_%d.dat'%(self.stress_models_dir,self.seissol_model_n,int(self.mu*10),self.receivef_strike))
        delTs = np.loadtxt('%s/ssaf_%s_Ts_pert_mu%02d_%d.dat'%(self.stress_models_dir,self.seissol_model_n,int(self.mu*10),self.receivef_strike))
        depth_range = np.loadtxt('%s/ssaf_%s_dep_stress_pert_mu%02d_%d.dat'%(self.stress_models_dir,self.seissol_model_n,int(self.mu*10),self.receivef_strike))
        dCFSt_in = delTs + self.mu*delPn
        if target_depth is not None:
            dCFSt_seissol = [interpolate.interp1d(depth_range,dCFSt_in[ti])(-target_depth) for ti in range(dCFSt_in.shape[0])]
            time_seissol = np.linspace(0,len(dCFSt_seissol)*dt,len(dCFSt_seissol))
        else:
            dCFSt_seissol,time_seissol = None,None
        return dCFSt_seissol,time_seissol,delPn,delTs,depth_range

    def get_output_dCFS(self,target_depth,print_on=True):
        # dCFS from Tandem model
        indx = np.argmin(abs(abs(self.dep) - abs(target_depth)))
        if print_on: print('Depth = %1.2f [km]'%abs(self.dep[indx]))
        pn = self.variables['normalT'].data[indx,1:] - self.variables['normalT'].data[indx,1]
        ts = self.variables['shearT'].data[indx,:] - self.variables['shearT'].data[indx,0]
        # pn = self.outputs[indx,1:,5] - self.outputs[indx,1,5]
        # ts = self.outputs[indx,1:,3] - self.outputs[indx,1,3]
        dCFSt_tandem = -ts - self.mu * pn
        time_tandem = self.outputs[indx,1:,0] - self.outputs[indx,1,0]
        return dCFSt_tandem,time_tandem,pn,ts

###########################################################################

class ROUTINE_PERTURB:
    def __init__(self,pert_name,base_model_tag=None):
        # ----------------- Create classes
        if base_model_tag is None:
            ref = PERTURB('reference')
            pert = PERTURB('%s'%(pert_name))
            after_pert = PERTURB('after_%s'%(pert_name))
        else:
            if 'stress_dep' in base_model_tag:
                if base_model_tag == 'stress_dep':
                    ref = PERTURB('reference')
                else:
                    ref = PERTURB(base_model_tag.split('_stress_dep')[0])
            else:
                ref = PERTURB(base_model_tag)
            pert = PERTURB('%s_%s'%(pert_name,base_model_tag))
            after_pert = PERTURB('after_%s_%s'%(pert_name,base_model_tag))
            # after_pert = PERTURB('first_after_%s_%s'%(pert_name,base_model_tag))
        target_eventid = int(pert_name.split('pert')[-1].split('_')[0])

        print('----------------- Load outputs -----------------')
        pert.load_output()
        after_pert.load_output()
        ref.load_output(pert=pert,after_pert=after_pert)

        print('----------------- Load events -----------------')
        ref.load_events(compute_on=False)
        ref.print_event_details(target_eventid=target_eventid)
        after_pert.load_events(compute_on=True,save_on=False)
        after_pert.print_event_details()

        # ----------------- 
        self.ref,self.pert,self.after_pert = ref,pert,after_pert
    
    def estimate_triggering_response(self,ref,after_pert):
        noline = False
        if len(after_pert.system_wide) == 0 or len(after_pert.tstart) == 0:
            import warnings
            warnings.warn('No system_size event detected - check back the sequence')
            after_tstart = 0
            noline = True
        elif len(after_pert.system_wide) > 1:
            after_tstart = after_pert.tstart[after_pert.system_wide[-1]]
        else:
            after_tstart = after_pert.tstart[after_pert.system_wide]
        lag = ref.tstart[ref.idx] - after_tstart
        return lag,noline,after_tstart

    def plot_triggering_response(self,ax):
        from perturb_plots import triggering_response
        lag,noline,_ = self.estimate_triggering_response(self.ref,self.after_pert)
        ax = triggering_response(ax,self.ref,self.pert,self.after_pert,lag,noline)
        return ax,lag

    def pub_plot_triggering_response(self,ax):
        from perturb_plots import pub_triggering_response
        lag,noline,after_tstart = self.estimate_triggering_response(self.ref,self.after_pert)
        ax = pub_triggering_response(ax,self.ref,self.pert,self.after_pert,lag,noline,after_tstart)
        return ax,lag

    def plot_compare_with_input_dCFS(self,ax,dt=0.01):
        target_depth = self.ref.evdep[self.ref.idx]
        from perturb_plots import compare_dCFS_at_depth
        dCFSt_seissol,time_seissol = self.pert.get_input_dCFS(target_depth,dt)[:2]
        dCFSt_tandem,time_tandem = self.pert.get_output_dCFS(target_depth)[:2]
        ax = compare_dCFS_at_depth(ax,dCFSt_seissol,time_seissol,dCFSt_tandem,time_tandem)
        ax.legend(fontsize=15,loc='lower right')
        return ax

    def return_vars(self):
        return self.ref,self.pert,self.after_pert