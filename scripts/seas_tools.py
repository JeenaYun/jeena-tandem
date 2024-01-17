#!/usr/bin/env python3
"""
Tools for SEAS benchmark comparison
Last modification: 2024.01.16.
by Jeena Yun
"""

import numpy as np
import os

class SEAS:
    def __init__(self,modeler,BPname,color='k',hf=10,my_output_dir=None):
        self.modeler = modeler
        self.mode = ''
        self.bpNum = int(BPname.split('-')[0].lower().split('bp')[-1])
        self.scheme = BPname.split('-')[1]
        if len(BPname.split('-')) > 2:
            self.mode = BPname.split('-')[2]
        self.save_dir = '/export/dump/jyun/BP%d'%(self.bpNum)
        self.col = color
        self.hf = hf # in meters
        if len(self.mode) > 0:
            self.comparison_dir = '%s/comparison/%s_%s_%dm'%(self.save_dir,self.modeler,self.mode.upper(),self.hf) 
        else:
            self.comparison_dir = '%s/comparison/%s_%dm'%(self.save_dir,self.modeler,self.hf) 
        if my_output_dir is None:
            if len(self.mode) > 0:
                self.my_output_dir = '%s/outputs_%s_hf%dm'%(self.save_dir,self.mode.upper(),self.hf)
            else:
                self.my_output_dir = '%s/outputs_hf%dm'%(self.save_dir,self.hf)

    def read_onfault_at_depth(self,stloc,print_on=True,new_fname=None):
        template = self.onfault_suffix(stloc)
        fname = '%s/%s.dat'%(self.comparison_dir,template)
        if self.modeler == 'yun' and not os.path.exists(fname):
            if print_on: print('No existing data file - write it')
            self.save_onfault_BP6(stloc,save_on=True,new_fname=new_fname)
        else:
            if print_on: print('Load %s'%(fname))
            self.t,self.slip,self.slip_rate,self.shear_stress,self.pore_pressure,self.darcy_vel,self.state = \
                np.loadtxt(fname,comments=['#','t'],unpack=True)

    def read_onfault_all(self,print_on=True):
        if not os.path.exists('%s/outputs.npy'%(self.my_output_dir)):
            outputs,dep = self.process_raw_onfault_outputs(print_on=print_on)
        else:
            if print_on: print('Load saved data: %s/outputs.npy'%(self.my_output_dir))
            outputs = np.load('%s/outputs.npy'%(self.my_output_dir))
            if print_on: print('Load saved data: %s/outputs_depthinfo.npy'%(self.my_output_dir))
            dep = np.load('%s/outputs_depthinfo.npy'%(self.my_output_dir))
        return outputs,dep

    def read_fault(self,target_var,print_on=True):
        vinfo = self.get_var_info(target_var,scenario=None)
        if not os.path.exists('%s/fault_%s.npy'%(self.my_output_dir,vinfo['field_name'])):
            fault_var,time,dep = self.save_fault(target_var,save_on=True,print_on=print_on)
        else:
            if print_on: print('Load saved data: %s/fault_%s.npy'%(self.my_output_dir,vinfo['field_name']))
            fault_var = np.load('%s/fault_%s.npy'%(self.my_output_dir,vinfo['field_name']))
            if print_on: print('Load saved data: %s/fault_Time.npy'%(self.my_output_dir))
            time = np.load('%s/fault_Time.npy'%(self.my_output_dir))
            if print_on: print('Load saved data: %s/fault_dep'%(self.my_output_dir))
            dep = np.load('%s/fault_dep.npy'%(self.my_output_dir))
        return fault_var,time,dep

    def read_global_outputs(self,print_on=True,new_fname=None):
        fname = '%s/global.dat'%(self.comparison_dir)
        if self.modeler == 'yun' and not os.path.exists(fname):
            if print_on: print('No existing data file - write it')
            self.save_global_BP6(save_on=True,new_fname=new_fname)
        else:
            if print_on: print('Load %s'%(fname))
            self.t,self.max_slip_rate,self.moment_rate = np.loadtxt(fname,comments=['#','t'],unpack=True)

    def process_raw_onfault_outputs(self,save_on=True,print_on=True):
        import pandas as pd
        from glob import glob
        import time
        if print_on: print('No existing outputs data - compute it...',end='')
        fnames = glob('%s/*.csv'%(self.my_output_dir))
        outputs,dep=[],[]
        ti = time.time()
        for fname in np.sort(fnames):
            dat = pd.read_csv(fname,delimiter=',',skiprows=1)
            stloc = pd.read_csv(fname,nrows=1,header=None)
            dep.append(float(stloc.values[0][-1].split(']')[0]))
            outputs.append(dat.values)
        if print_on: print('Done! (%2.4f s)'%(time.time()-ti))
        outputs = np.array(outputs)
        dep = np.array(dep)
        # Sort the outputs
        ind = np.argsort(dep)
        outputs = outputs[ind,:,:]
        dep = np.sort(dep)
        if save_on:
            if print_on: print('Save data...',end=' ')
            np.save('%s/outputs'%(self.my_output_dir),outputs)
            np.save('%s/outputs_depthinfo'%(self.my_output_dir),dep)
        return outputs,dep

    def convert2BPFormat(self,stloc,field_list,dt_min,dt_max,Nsteps,dat,out_type,new_fname=None):
        if out_type == 'onfault':
            template = self.onfault_suffix(stloc)
        elif out_type == 'global':
            template = 'global'
        elif out_type == 'evolution':
            template = field_list[-1]

        if new_fname is None:
            new_fname = '%s/%s.dat'%(self.comparison_dir,template)
        
        # Save in the given format
        fmt = ['%21.13E']
        if out_type == 'evolution':
            for i in range(dat.shape[1]-1): fmt.append('%14.6E')
            headers = self.generate_header(field_list,stloc,dt_min,dt_max,Nsteps,dat)
        else:
            for i in range(len(field_list)-1): fmt.append('%14.6E')
            headers = self.generate_header(field_list,stloc,dt_min,dt_max,Nsteps)
        np.savetxt(new_fname,dat,header=headers,fmt=fmt,delimiter='\t',comments='')

        # Save to the self object
        self.t = dat[:,0]
        if out_type == 'onfault':
            self.slip = dat[:,1]
            self.slip_rate = dat[:,2]
            self.shear_stress = dat[:,3]
            self.pore_pressure = dat[:,4]
            self.darcy_vel = dat[:,5]
            self.state = dat[:,6]
        elif out_type == 'global':
            self.max_slip_rate = dat[:,1]
            self.moment_rate = dat[:,2]
        print('Saved!')

    def save_onfault_BP6(self,stloc,save_on,darcy_order=2,new_fname=None):
        template = self.onfault_suffix(stloc)
        my_out_fname = '%s/%s.csv'%(self.my_output_dir,template)
        if not os.path.exists(my_out_fname): raise NameError('No such output file %s'%(my_out_fname))
        field_list = ['t','slip','slip_rate','shear_stress','pore_pressure','darcy_vel','state']
        self.f0 = 0.6
        self.b = 0.005
        self.V0 = 1e-6
        self.L = 0.004
        self.kappa = 1e-13 # m2
        self.eta = 1e-3 # Pa s
        outputs,dep = self.read_onfault_all(print_on=False)
        sti = np.argmin(abs(dep-stloc/1e3))
        raw_dat = outputs[sti,:,:]
        # Tandem output:   Time [s] | phi | slip [m] | traction0 [MPa] | slip-rate0 [m/s] | normal-stress [MPa]
        # Required output: Time (s) | Slip (m) | Slip_rate log10(m/s) | Shear_stress (MPa) | Pore_pressure (MPa) | Darcy_velocity (m/s) | State log10(s)
        t = raw_dat[:,0]
        slip = raw_dat[:,2]
        slip_rate = np.log10(raw_dat[:,4])
        if np.all(raw_dat[:,3] <= 0):
            shear_stress = -raw_dat[:,3]
        else:
            shear_stress = raw_dat[:,3]
        pore_pressure = 50.0 - raw_dat[:,5]
        darcy_vel = self.get_darcy_vel(stloc,save_on,order=darcy_order)
        phi = raw_dat[:,1]
        state = np.log10(np.exp(np.divide(phi-self.f0,self.b))*self.L/self.V0)    
        dat = np.c_[t,slip,slip_rate,shear_stress,pore_pressure,darcy_vel,state]
        if save_on:
            self.convert2BPFormat(stloc,field_list,min(np.diff(t)),max(np.diff(t)),len(t),dat,'onfault',new_fname)

    def save_fault(self,target_var,save_on,print_on):
        from vtk import vtkXMLUnstructuredGridReader
        from read_outputs import read_pvd
        from glob import glob
        import time
        if print_on: print('No existing fault data - compute it...',end='')
        ti = time.time()
        vinfo = self.get_var_info(target_var,scenario=None)
        # --- Read time info from pvd file
        time = read_pvd('%s/fault.pvd'%(self.my_output_dir))
        # --- Load individual vtu files and extract fault outputs
        fnames = glob('%s/fault_*.vtu'%(self.my_output_dir))
        if len(fnames) == 0:
            raise NameError('No such file found - check the input')
        var,dep = [np.array([]) for k in range(time.shape[0])],[np.array([]) for k in range(time.shape[0])]
        for file_name in fnames:
            if 'static' in file_name:
                continue
            # --- Read the source file
            reader = vtkXMLUnstructuredGridReader()
            reader.SetFileName(file_name)
            reader.Update()  # Needed because of GetScalarRange
            output = reader.GetOutput()
            k = int(file_name.split('fault_')[-1].split('_')[0])
            # --- Save into local variable
            var[k] = np.hstack((var[k],np.array(output.GetPointData().GetArray(vinfo['tandem_varname']))))
            dep[k] = np.hstack((dep[k],np.array([output.GetPoint(k)[1] for k in range(output.GetNumberOfPoints())])))
        # --- Convert the outputs into numpy array
        var = np.array(var)
        dep = np.array(dep)
        # --- Sort them along depth
        ind = np.argsort(dep,axis=1)
        var = np.take_along_axis(var, ind, axis=1).T
        dep = np.sort(dep,axis=1)[0]
        if print_on: print('Done! (%2.4f s)'%(time.time()-ti))
        if save_on:
            if print_on: print('Save the data')
            np.save('%s/fault_%s'%(self.my_output_dir,vinfo['field_name']),var)
            np.save('%s/fault_Time'%(self.my_output_dir),time)
            np.save('%s/fault_dep'%(self.my_output_dir),dep)
        return var,time,dep

    def save_global_BP6(self,save_on,new_fname=None):
        from scipy import integrate
        field_list = ['t','max_slip_rate','moment_rate']
        mu = 32.04e9 # Pa
        V,t,dep = self.read_fault('slip_rate',print_on=False)
        max_slip_rate = np.log10(np.max(V,axis=0))
        moment_rate = [integrate.simpson(mu*V[:,ti],dep*1e3) for ti in range(len(t))]
        dat = np.c_[t,max_slip_rate,moment_rate]
        if save_on:
            self.convert2BPFormat(None,field_list,min(np.diff(t)),max(np.diff(t)),len(t),dat,'global',new_fname)

    def save_evolution_BP6(self,target_var,save_on,new_fname=None):
        var_info = self.get_var_info(target_var)
        fname = '%s/%s.dat'%(self.comparison_dir,var_info['field_name'])
        if not os.path.exists(fname):
            field_list = ['z','t','max_slip_rate',var_info['field_name']]
            outputs,dep = self.read_onfault_all(print_on=False)
            t = outputs[0,:,0]
            self.read_global_outputs(print_on=False)
            if target_var == 'darcy_vel':
                darcy_vel,darcy_dep = self.get_darcy_vel(None,save_on=False,order=2)
                zi = np.where(abs(darcy_dep)<=10e3)[0]
                var = darcy_vel[:,zi].T
                zloc = np.hstack((np.zeros(2),darcy_dep[zi]))
            else:
                zi = np.where(abs(dep)<=10)[0]
                var = outputs[zi,:,var_info['output_idx']]
                zloc = np.hstack((np.zeros(2),dep[zi]*1e3))
            dat = np.vstack((zloc,np.vstack((t,self.max_slip_rate,var)).T))
            if save_on:
                self.convert2BPFormat(None,field_list,min(np.diff(t)),max(np.diff(t)),len(t),dat,'evolution',new_fname)
        else:
            print('Evolution output for %s already exists'%(var_info['field_name']))

    def get_darcy_vel(self,stloc,save_on,order=2):
        # Compute or load Darcy velocity
        if not os.path.exists('%s/darcy_vel%d.npy'%(self.my_output_dir,order)):
            print('No existing darcy_velocity data - compute it')
            outputs,dep = self.read_onfault_all(print_on=False)
            time = np.array(outputs[0,:,0])
            normalT = np.array(outputs[:,:,5])
            dep = np.array(dep)

            # --- Compute darcy 
            p = (50 - normalT)*1e6
            zloc = dep*1e3
            darcy_vel1 = np.array([-(self.kappa/self.eta)*np.gradient(p[:,t],zloc,edge_order=1) for t in range(len(time))])
            darcy_vel2 = np.array([-(self.kappa/self.eta)*np.gradient(p[:,t],zloc,edge_order=2) for t in range(len(time))])
            if save_on:
                print('Save data...',end=' ')
                np.save('%s/darcy_vel1'%(self.my_output_dir),darcy_vel1)
                np.save('%s/darcy_vel2'%(self.my_output_dir),darcy_vel2)
                np.save('%s/zloc'%(self.my_output_dir),zloc)
            if order == 1: darcy = darcy_vel1
            if order == 2: darcy = darcy_vel2
        else:
            print('Load existing darcy_velocity data')
            if order == 1: darcy = np.load('%s/darcy_vel1.npy'%(self.my_output_dir))
            if order == 2: darcy = np.load('%s/darcy_vel2.npy'%(self.my_output_dir))
            zloc = np.load('%s/zloc.npy'%(self.my_output_dir))

        if stloc is not None:
            # Extract Darcy velocity at the station location of interest
            sti = np.argmin(abs(zloc-stloc))
            darcy_vel = darcy[:,sti]
            return darcy_vel
        else:
            darcy_vel = darcy
            return darcy_vel,zloc

    def generate_header(self,field_list,stloc,dt_min,dt_max,Nsteps,dat=None):
        from datetime import datetime
        dat_fields = ''
        # field_list = ['t','slip','slip_rate','shear_stress','pore_pressure','darcy_vel','state']
        headers = ''
        headers += '# This is the file header:\n'
        headers += '# Benchmark problem = SEAS Benchmark BP%d-%s\n'%(self.bpNum,self.mode.upper())
        headers += '# Code name = Tandem\n'
        headers += '# Code version = 1.0\n'
        headers += '# Modeler = Jeena Yun\n'
        headers += '# Date = %s\n'%(datetime.today().strftime('%B %d, %Y'))
        headers += '# Element size = %d m\n'%(self.hf)
        if stloc is not None: headers += '# Station location: z = %1.1f km\n'%(stloc*1e-3)
        headers += '# Minimum time step = %1.6f\n'%(dt_min)
        headers += '# Maximum time step = %1.6f\n'%(dt_max)
        headers += '# Number of time steps in file = %d\n'%(Nsteps)
        for i in range(len(field_list)):
            if field_list[0] == 'z':
                if i == 0:
                    headers += '# Row #1 = Along-fault (m) with two zeros first \n'
                elif i < 3:
                    headers += '# Column #%d = %s\n'%(i,self.get_var_info(field_list[i])['header'])
                elif dat is not None:
                    headers += '# Column #%d-%d = %s along the fault\n'%(i,dat.shape[1],self.get_var_info(field_list[i])['header'])
            else:
                headers += '# Column #%d = %s\n'%(i+1,self.get_var_info(field_list[i])['header'])
            dat_fields += '%s '%(field_list[i])
        headers += '# The line below lists the names of the data fields:\n'
        headers += '%s\n'%(dat_fields)
        headers += '# Here is the time-series data'
        return headers

    def get_var_info(self,target_var,scenario=None):
        #  t slip slip_rate shear_stress pore_pressure darcy_vel state
        if scenario is None: out_var = None
        if target_var == 't':
            if scenario is not None: out_var = scenario.t
            head,lab,field,tandem_varname = 'Time [s]','Time [s]','t','Time'
            output_idx = 0
        elif target_var == 'slip':
            if scenario is not None: out_var = scenario.slip
            head,lab,field,tandem_varname = 'Slip [m]','Slip [m]','slip','slip0'
            output_idx = 2
        elif target_var == 'slip_rate':
            if scenario is not None: out_var = scenario.slip_rate
            head,lab,field,tandem_varname = 'Slip_rate [log10(m/s)]','$\log_{10}$(Slip Rate [m/s])','slip_rate','slip-rate0'
            output_idx = 4
        elif target_var == 'shear_stress':
            if scenario is not None: out_var = scenario.shear_stress
            head,lab,field,tandem_varname = 'Shear_stress [MPa]','Shear Stress [MPa]','shear_stress','traction0'
            output_idx = 3
        elif target_var == 'normal_stress':
            if scenario is not None: out_var = scenario.normal_stress
            head,lab,field,tandem_varname = 'Normal_stress [MPa]','Normal Stress [MPa]','normal_stress','normal-stress'
            output_idx = 5
        elif target_var == 'pore_pressure':
            if scenario is not None: out_var = scenario.pore_pressure
            head,lab,field,tandem_varname = 'Pore_pressure [MPa]','Pore Fluid Pressure [MPa]','pore_pressure',''
            output_idx = np.nan
        elif target_var == 'darcy_vel':
            if scenario is not None: out_var = scenario.darcy_vel
            head,lab,field,tandem_varname = 'Darcy_velocity [m/s]','Darcy Velocity [m/s]','darcy_vel',''
            output_idx = np.nan
        elif target_var == 'state':
            if scenario is not None: out_var = scenario.state
            head,lab,field,tandem_varname = 'State [log10(s)]','$\log_{10}$(State [s])','state','state'
            output_idx = 1
        elif target_var == 'max_slip_rate':
            if scenario is not None: out_var = scenario.max_slip_rate
            head,lab,field,tandem_varname = 'Max_slip_rate [log10(m/s)]','$\log_{10}$(Peak Slip Rate [m/s])','max_slip_rate',''
            output_idx = np.nan
        elif target_var == 'moment_rate':
            if scenario is not None: out_var = scenario.moment_rate
            head,lab,field,tandem_varname = 'Moment_density_rate [N/s]','Moment Density Rate [N/s]','moment_rate',''
            output_idx = np.nan
        var_info = {
            "header": head,
            "label": lab,
            "data": out_var,
            "output_idx": output_idx,
            "field_name": field,
            "tandem_varname": tandem_varname
            }
        return var_info

    def line_plot_macro(self,ax,stloc,scenario_list,target_var):
        for scenario in scenario_list:
            var_info = self.get_var_info(target_var,scenario)
            if scenario.modeler == 'yun':
                ax.plot(scenario.t,var_info['data'],color=scenario.col,lw=2.5,linestyle='--',zorder=3,label='%s'%(scenario.modeler))
            else:
                ax.plot(scenario.t,var_info['data'],color=scenario.col,lw=2.5,label='%s'%(scenario.modeler))
        ylab = var_info['label']
        ax.legend(fontsize=15)
        ax.set_xlabel('Time [s]',fontsize=17)
        ax.set_ylabel(ylab,fontsize=17)
        if stloc is not None: ax.set_title('File: %s (z = %1.1f km)'%(scenario.onfault_suffix(stloc),stloc/1e3),fontsize=21,fontweight='bold')
        ax.grid(True,alpha=0.5)

    def change_save_dir(self,new_save_dir):
        self.save_dir = new_save_dir
    
    def onfault_suffix(self,stloc):
        if self.bpNum == 1:
            template = 'fltst_dp%03d'%(stloc*1e-3*10)
        elif self.bpNum == 6:
            if stloc >= 0:
                template = 'fltst_strk+%02d'%(abs(stloc)*1e-3*10)
            else:
                template = 'fltst_strk-%02d'%(abs(stloc)*1e-3*10) 
        return template