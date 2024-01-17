#!/usr/bin/env python3
"""
Tools for comparing perturbed cycle models
Last modification: 2024.01.09.
by Jeena Yun
"""

import numpy as np
import setup_shortcut
import os
sc = setup_shortcut.setups()

class PERTURB:
    def __init__(self,target_eventid,model_n,receivef_strike,after_pert=True,time_diff_in_h=16.2,mu=0.4,do_not_load_output=False,print_on=False):
        self.target_eventid = target_eventid
        self.model_n = model_n
        if len(self.model_n.split('_X')) > 1:
            self.multiply = int(self.model_n.split('_X')[-1])
        else:
            self.multiply = int(1)
        self.mu = mu
        self.receivef_strike = receivef_strike
        if after_pert:
            self.period = 'after_pert'
        else:
            self.period = 'pert'
        self.time_diff_in_h = time_diff_in_h
        self.raw_dir = '/export/dump/jyun/perturb_stress/'
        self.stress_models_dir = '/home/jyun/Tandem/perturb_stress/seissol_outputs'
        if self.time_diff_in_h == 16.2:
            self.full_pert_model_name = '%s%d'%(sc.model_code(self.model_n),self.receivef_strike)
        else:
            self.full_pert_model_name = '%s%d_%dh'%(sc.model_code(self.model_n),self.receivef_strike,self.time_diff_in_h)
        self.save_dir = self.raw_dir+'%s%d_%s'%(self.period,self.target_eventid,self.full_pert_model_name)
        if not do_not_load_output: self.load_output(print_on)

        # Parameters related to the event analyzing
        self.ref_dir = self.raw_dir+'reference'
        if 'v6_ab2_Dc2' in self.ref_dir:
            self.Vths = 1e-1
            self.intv = 0.15
        elif 'perturb_stress' in self.ref_dir:
            self.Vths = 2e-1
            self.intv = 0.15
        else:
            self.Vths = 1e-2
            self.intv = 0.
        self.Vlb = 0
        self.cuttime,self.rths = 0, 10
        self.dt_creep,self.dt_interm,self.dt_coseismic = 2*sc.yr2sec, 0, 0.5

    def load_output(self,print_on):
        from read_outputs import load_fault_probe_outputs,load_checkpoint_info
        self.outputs,self.dep,self.params = load_fault_probe_outputs(self.save_dir,print_on=print_on)
        if os.path.exists(self.save_dir+'/checkpoint_info.csv'):
            if print_on: print('Load checkpoint info from ',self.save_dir+'/checkpoint_info.csv')
            self.ckp_dat = load_checkpoint_info(self.save_dir)
        
    def events_without_pert(self,print_on=True):
        from cumslip_compute import analyze_events
        if os.path.exists('%s/cumslip_outputs_Vths_%1.0e_srvar_%03d_rths_%d_tcreep_%d_tseis_%02d.npy'
                          %(self.ref_dir,self.Vths,self.intv*100,self.rths,self.dt_creep/sc.yr2sec,self.dt_coseismic*10)):
            self.ref_cumslip_outputs = np.load('%s/cumslip_outputs_Vths_%1.0e_srvar_%03d_rths_%d_tcreep_%d_tseis_%02d.npy'\
                                               %(self.ref_dir,self.Vths,self.intv*100,self.rths,self.dt_creep/sc.yr2sec,self.dt_coseismic*10),allow_pickle=True)
            self.ref_spin_up_idx = np.load('%s/spin_up_idx_Vths_%1.0e_srvar_%03d_rths_%d_tcreep_%d_tseis_%02d.npy'\
                                       %(self.ref_dir,self.Vths,self.intv*100,self.rths,self.dt_creep/sc.yr2sec,self.dt_coseismic*10))
            self.ref_tstart,self.ref_tend,self.ref_evdep = self.ref_cumslip_outputs[0][0],self.ref_cumslip_outputs[0][1],self.ref_cumslip_outputs[1][1]
            self.ref_rupture_length,self.ref_av_slip,self.ref_system_wide,self.ref_partial_rupture,self.ref_event_cluster,self.ref_lead_fs,self.ref_major_pr,self.ref_minor_pr \
                = analyze_events(self.ref_cumslip_outputs,self.rths)
            self.ref_idx = self.ref_system_wide[self.ref_system_wide>=self.ref_spin_up_idx][self.target_eventid]
            if print_on: print('Loaded pre-saved reference cumslip outputs')
        else:
            print('No pre-saved cumslip outputs')
        if print_on:
            print('======== Event details without perturbation ========')
            print('Event %d'%(self.ref_idx))
            print('Event depth without perturbation: %1.2f km'%(self.ref_evdep[self.ref_idx]))

    def events_with_pert(self,print_on=True):
        from cumslip_compute import analyze_events,compute_cumslip
        self.cumslip_outputs = compute_cumslip(self.outputs,self.dep,self.cuttime,self.Vlb,self.Vths,self.dt_creep,self.dt_coseismic,self.dt_interm,self.intv,print_on=print_on)
        self.tstart,self.tend,self.evdep = self.cumslip_outputs[0][0],self.cumslip_outputs[0][1],self.cumslip_outputs[1][1]
        self.system_wide = analyze_events(self.cumslip_outputs,self.rths)[2]
        if print_on:
            print('======== Event details with perturbation ========')
            print('Event depths:',self.evdep)
            print('System-wide events:',self.system_wide)
            print('Event depth of system-wide events:',self.evdep[self.system_wide])

    def load_stress_info(self,print_on=True):
        from stress_model_tools import single_case
        if not 'ref_evdep' in dir(self):
            if print_on: print('No ref_evdep - compute it first')
            self.events_without_pert(print_on=print_on)
        self.peak_dynamic,self.static = single_case(self.stress_models_dir,self.model_n,self.receivef_strike,self.ref_evdep[self.ref_idx],self.multiply,self.mu,print_off=not print_on)
