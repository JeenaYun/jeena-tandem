#!/usr/bin/env python3
"""
Define general setups and often used values
Last modification: 2024.06.06.
by Jeena Yun
"""

import numpy as np
import os

class setups:
    def __init__(self):
        self.yr2sec = 365*24*60*60
        self.wk2sec = 7*24*60*60

    def get_setup_dir(self):
        if 'j4yun' in os.getcwd(): # local
            # self.setup_dir = '/Users/j4yun/Dropbox/Codes/Ridgecrest_CSC/jeena-tandem/setup_files'
            setup_dir = '/Users/j4yun/Dropbox/Codes/Ridgecrest_CSC/jeena-tandem/setup_files/supermuc'
        elif 'di75weg' in os.getcwd(): # supermuc
            # self.setup_dir = '/hppfs/work/pn49ha/di75weg/jeena-tandem/setup_files/supermuc'
            setup_dir = '/hppfs/work/pn49ha/di75weg/jeena-tandem/setup_files/supermuc'
        elif 'jyun' in os.getcwd(): # LMU server
            # self.setup_dir = '/home/jyun/Tandem'
            setup_dir = '/home/jyun/Tandem'
        return setup_dir
    
    def model_code(self,model_n):
        split_n = model_n.split('_')
        if len(split_n) == 2: # e.g., 'vert_slow' --> vs
            code = split_n[0][0]+split_n[-1][0]
        elif len(split_n) == 3: # e.g., 'vert_slow_X2' --> vsX2_
            code = split_n[0][0]+split_n[1][0]+split_n[-1]+'_'
        elif len(split_n) == 4: # e.g., 'vert_slow_dyn_X2' --> vsdynX2_
            code = split_n[0][0]+split_n[1][0]+split_n[2]+split_n[-1]+'_'
        else:
            raise TypeError('Very long model name \'%s\'- please check'%(model_n))
        return code
    
    def code2name(self,code):
        # e.g., vs340, vsX2_350
        if code[0] == 'v': 
            model_n = 'vert'
        elif code[0] == 'd':
            model_n = 'dipping'
        if code[1] == 'f':
            model_n += '_fast'
        elif code[1] == 's':
            model_n += '_slow'
        if 'X' in code:
            model_n += '_X%d'%(int(code.split('X')[-1].split('_')[0]))
            strike = int(code.split('_')[-1])
        if 'dyn' in code:
            model_n += '_dyn'
            strike = int(code.split('_')[-1])
        elif 'static' in code:
            model_n += '_static'
            strike = int(code.split('_')[-1])
        elif 'flipstat' in code:
            model_n += '_flipstat'
            strike = int(code.split('_')[-1])
        if not 'strike' in locals():
            strike = int(code[2:])
        return model_n,strike

    def tandem_modeltag(self,branch_name):
        model_tag = 'reference'
        target_eventid,seissol_model_n,receivef_strike,multiply,time_diff_in_h,mu = None,None,None,None,None,None
        if 'pert' in branch_name:
            multiply = int(1)
            time_diff_in_h = 16.2
            mu = 0.4
            target_eventid = int(branch_name.split('pert')[-1].split('_')[0])
            tails = branch_name.split('pert%d_'%(target_eventid))[-1]
            if len(tails.split('_')) > 1:
                if 'X' in tails:
                    seissol_model_code = tails.split('_')[0] + '_' + tails.split('_')[1]
                    multiply = int(seissol_model_code.split('X')[-1].split('_')[0])
                if 'h' in tails:
                    if len(tails.split('h')[0].split('_')[-1]) <= 2 and len(tails.split('h')[0].split('_')[-1]) > 0: # varying_time
                        time_diff_in_h = int(tails.split('h')[0].split('_')[-1])
                    if len(tails.split('h')) > 2 or len(tails.split('h')[0].split('_')[-1]) > 2: # diffwavelength
                        model_tag = tails.split('_')[-1].split('h')[0]+'h'
                    elif 'hf' in tails: # hf10_reference
                        model_tag = 'hf' + tails.split('hf')[-1]
                    if 'X' not in tails:
                        seissol_model_code = tails.split('h')[0].split('_')[0]
                if 'X' not in tails and 'h' not in tails:
                    if 'dyn' in tails or 'stat' in tails:
                        if len(tails.split('_')) > 2:
                            seissol_model_code = tails.split('_')[0]+'_'+tails.split('_')[1]
                        else:
                            seissol_model_code = tails
                    else:
                        seissol_model_code = tails.split('_')[0]
                    if tails.split(seissol_model_code+'_')[-1] != 'stress_dep':
                        model_tag = tails.split(seissol_model_code+'_')[-1]
            else:
                seissol_model_code = tails
            seissol_model_n,receivef_strike = self.code2name(seissol_model_code)
        else:
            if branch_name != 'reference':
                model_tag = branch_name
        return model_tag,target_eventid,seissol_model_n,receivef_strike,multiply,time_diff_in_h,mu
    
    def write_faultprobe_loc(self,prefix_or_Hs,fid,dmin,dmax,dip=90,write_on=False):
        if isinstance(prefix_or_Hs, str):
            import change_params
            ch = change_params.variate()
            Hs = ch.load_parameter(prefix_or_Hs)[1]
        else:
            Hs = prefix_or_Hs
        loc,c,d = [],0,0
        if write_on: fid.write('probes = [\n')
        if dip == 90:
            while d < Hs[0]:
                if write_on: 
                    if abs(d - Hs[0]) < dmin*0.1:
                        fid.write('    { name = "fp%03d", x = [0.0, %1.4f] }\n'%(c,-d))
                    else:
                        fid.write('    { name = "fp%03d", x = [0.0, %1.4f] },\n'%(c,-d))
                loc.append(-d)
                if d + dmin <= Hs[1]+Hs[2]+dmin*0.1:
                    d += dmin
                else:
                    d += dmax
                c += 1
        else:
            dip = np.deg2rad(dip)
            while d <= Hs[0]:
                x = -d/np.tan(np.pi-dip)
                if write_on: fid.write('{ name = "fp%03d", x = [%1.4f, %1.4f] },\n'%(c,x,-d))
                loc.append([x,-d])
                if d < Hs[1]:
                    d += dmin # 0.5
                else:
                    d += dmax #5
                c += 1
        if write_on: fid.write(']\n\n')
        return np.array(loc)

    def write_domainprobe_loc(self,fid,xmax,dx,write_on=False):
        loc,c,d = [],0,0
        if write_on: fid.write('probes = [\n')
        while d <= xmax:
            if d == xmax:
                if write_on: fid.write('    { name = "dp%03d", x = [%1.4f, 0.0] }\n'%(c,d))
            else:
                if write_on: fid.write('    { name = "dp%03d", x = [%1.4f, 0.0] },\n'%(c,d))
            loc.append(d)
            d += dx
            c += 1
        if write_on: fid.write(']\n\n')
        return np.array(loc)
    
    def sec2hms(self,sec):
        """
        Convert seconds into hour-minute-second format
        """
        m, s = divmod(sec, 60)
        h, m = divmod(m, 60)

        print('Input time: %2.2f s'%sec)
        print('=',end=' ')

        if h != 0:
            print('%d h'%h,end=' ')            
        if m != 0:
            print('%d m'%m,end=' ')
        if s != 0:
            print('%d s'%s)

    def base_event_criteria(self,save_dir,image='sliprate'):
        if image == 'sliprate':
            vmax = 1e1
            try:
                params = np.load('%s/const_params.npy'%(save_dir),allow_pickle=True)
                vmin = params.item().get('Vp')*1e-3
            except:
                vmin = 1e-12
        elif image == 'shearT':
            vmin,vmax = -5,5
        else:
            vmin,vamx = None,None

        if 'v6_ab2_Dc2' in save_dir:
            Vths = 1e-1
            SRvar = 0.15
        elif 'perturb_stress' in save_dir:
            Vths = 2e-1
            if 'diffwavelength' in save_dir or 'slowVpl' in save_dir:
                SRvar = 0.15
            else: # including reference
                SRvar = 0.1
        else:
            Vths = 1e-2
            SRvar = 0.1
        Vlb = 0
        dt_interm = 0
        cuttime = 0
        rths = 10
        dt_creep = 2*self.yr2sec
        dt_coseismic = 0.5

        return vmin,vmax,Vths,SRvar,Vlb,dt_interm,cuttime,rths,dt_creep,dt_coseismic

    def base_val(self):
        # Base value used most commonly used
        Wf = 24
        y = np.linspace(0,-Wf*2,1000)
        z = -y

        H = 12.0
        h = 5.0
        H2 = 2.0
        Hs = [Wf,H,h,H2]

        Vp = 1e-9
        rho0 = 2.670
        V0 = 1.0e-6
        Dc = 0.004
        f0 = 0.6
        dmin,dmax=0.02,1
        others = [dmin,dmax,Vp,rho0,V0,f0]

        b = 0.019
        a_b1 = 0.012
        a_b2 = -0.004
        a_b3 = 0.015
        a_b4 = 0.024

        tau03 = -22.5
        tau02 = -30
        tau01 = -10

        sigma02 = 50
        sigma01 = 10

        sigma0 = sigma02*np.ones(z.shape)
        sigma0[z < H2] = sigma02 + (sigma02 - sigma01)*(z[z < H2]-H2)/H2
        
        a_b = a_b4*np.ones(z.shape)
        a_b[z < Wf] = a_b3 + (a_b4-a_b3)*(z[z < Wf]-H-h)/(Wf-H-h)
        a_b[z < H+h] = a_b2 + (a_b3-a_b2)*(z[z < H+h]-H)/h
        a_b[z < H] =a_b2*np.ones(z[z < H].shape)
        a_b[z < H2] = a_b2 + (a_b2 - a_b1)*(z[z < H2]-H2)/H2

        b = b*np.ones(a_b.shape)
        a = a_b + b

        tau0 = tau03*np.ones(z.shape)
        tau0[z < H+h] = tau02 + (tau03-tau02)*(z[z < H+h]-H)/h
        tau0[z < H] =tau02*np.ones(z[z < H].shape)
        tau0[z < H2] = tau02 + (tau02 - tau01)*(z[z < H2]-H2)/H2

        L = Dc*np.ones(z.shape)
        return y,Hs,a,b,a_b,tau0,sigma0,L,others
    
    def params(self,prefix_in):
        if len(prefix_in.split('/')) > 1:
            prefix = prefix_in.split('/')[0]
        else:
            prefix = prefix_in

        if 'BP1' in prefix:
            Wf = 40
            y = np.linspace(0,-Wf,1000)
            z = -y

            H = 15.0
            h = 3.0
            Hs = [Wf,H,h]

            a0 = 0.010
            amax = 0.025
            b = 0.015

            a = amax*np.ones(z.shape)
            a[z < H+h] = a0 + (amax-a0)*(z[z < H+h]-H)/h
            a[z < H] = a0*np.ones(z[z < H].shape)
            b = b*np.ones(a.shape)
            a_b = a - b

            sigma01 = 50
            mu0 = 32.038120320
            rho0 = 2.670
            Vinit = 1.0e-9
            f0 = 0.6
            V0 = 1.0e-6
            Dc = 0.008
            Vp = 1e-9
            others = [Vp,rho0,V0,f0]

            sigma0 = sigma01*np.ones(z.shape)
            mu = mu0*np.ones(z.shape)
            eta = np.sqrt(mu * rho0) / 2.0
            Vi = Vinit*np.ones(z.shape)
            
            e = np.exp((f0 + b * np.log(V0 / Vi)) / amax)
            tau0 = -(sigma0 * amax * np.arcsinh((Vi / (2.0 * V0)) * e) + eta * Vi)
            L = Dc*np.ones(z.shape)
            
        elif prefix == 'test01':
            Wf = 40
            y = np.linspace(0,-Wf,1000)
            z = -y

            b = 0.015
            H = 8.0
            h = 3.0
            H2 = 2.0
            h2 = 0.5
            Hs = [Wf,H,h,H2,h2]

            a0 = 0.010
            amax = 0.025
            a1 = 0.02

            a = amax*np.ones(z.shape)
            a[z < H+h] = a0 + (amax-a0)*(z[z < H+h]-H)/h
            a[z < H] = a0*np.ones(z[z < H].shape)
            a[z < H2] = a0 + (a0-a1)*(z[z < H2]-H2)/h2
            a[z < H2-h2] = a1*np.ones(z[z < H2-h2].shape)
            b = b*np.ones(a.shape)
        
        elif prefix == 'LnF16':
            Wf = 24
            y = np.linspace(0,-Wf*2,1000)
            z = -y

            H = 9.0
            h = 6.0
            H2 = 2.0
            Hs = [Wf,H,h,H2]

            a0 = 0.02
            amax = 0.023
            a_b0 = 7e-3
            a_bmin = -3e-3
            a_bmax = 0.023
            a_b1 = 15e-3

            a_b = a_bmax*np.ones(z.shape)
            a_b[z < Wf] = a_b1 + (a_bmax-a_b1)*(z[z < Wf]-H-h)/(Wf-H-h)
            a_b[z < H+h] = a_bmin + (a_b1-a_bmin)*(z[z < H+h]-H)/h
            a_b[z < H] =a_bmin*np.ones(z[z < H].shape)
            a_b[z < H2] = a_b0*np.ones(z[z < H2].shape)

            a = amax*np.ones(z.shape)
            a[z < Wf] = a0 + (amax-a0)*(z[z < Wf]-H-h)/(Wf-H-h)
            a[z < H+h] = a0*np.ones(sum(z < H+h))
            b = a - a_b

        elif prefix == 'Thakur20_positivetau':
            y,Hs,a,b,a_b,_tau0,sigma0,L,others = self.base_val()

            tau03 = 22.5
            tau02 = 30
            tau01 = 10
            tau0 = tau03*np.ones(z.shape)
            tau0[z < H+h] = tau02 + (tau03-tau02)*(z[z < H+h]-H)/h
            tau0[z < H] =tau02*np.ones(z[z < H].shape)
            tau0[z < H2] = tau02 + (tau02 - tau01)*(z[z < H2]-H2)/H2

        elif prefix == 'Thakur20_failed' or prefix == 'Thakur20_reproduce' or prefix == 'Thakur20_smalltmax' or prefix == 'DZ_triangular_homogeneous' or prefix == 'Thakur20_L8':
            y,Hs,_a,_b,a_b,tau0,sigma0,L,others = self.base_val()
            
            b = 0.015
            b = b*np.ones(a_b.shape)
            a = a_b + b

        elif prefix == 'lithostatic_sn':
            y,Hs,a,b,a_b,_tau0,_sigma0,L,others = self.base_val()
            
            f0 = others[-1]
            surf = 10
            sigma_grad = 15

            sigma0 = sigma_grad*abs(y)
            tau0 = -sigma0*f0

            sigma0 += surf
            tau0 -= surf

        elif prefix == 'small_domain':
            Wf = 14
            y = np.linspace(0,-Wf*2,1000)
            z = -y

            H = 12.0
            H2 = 2.0
            Hs = [Wf,H,H2]

            Vp = 1e-9
            rho0 = 2.670
            V0 = 1.0e-6
            f0 = 0.6
            others = [Vp,rho0,V0,f0]

            Dc = 0.004

            b = 0.019
            a_b1 = 0.015
            a_b2 = -0.004

            tau01 = -10
            tau02 = -30

            sigma01 = 10
            sigma02 = 50
            
            a_b = a_b1*np.ones(z.shape)
            a_b[z < Wf] = a_b2 + (a_b1-a_b2)*(z[z < Wf]-H)/(Wf-H)
            a_b[z < H] =a_b2*np.ones(z[z < H].shape)
            a_b[z < H2] = a_b2 + (a_b2 - a_b1)*(z[z < H2]-H2)/H2

            b = b*np.ones(a_b.shape)
            a = a_b + b

            tau0 = tau02*np.ones(z.shape)
            tau0[z < H2] = tau02 + (tau02 - tau01)*(z[z < H2]-H2)/H2

            sigma0 = sigma02*np.ones(z.shape)
            sigma0[z < H2] = sigma02 + (sigma02 - sigma01)*(z[z < H2]-H2)/H2

            L = Dc*np.ones(z.shape)

        elif prefix == 'mtmod_team3':
            Wf = 100
            y = np.linspace(0,-Wf,2500)
            z = -y

            dip = np.deg2rad(30)
            x = np.linspace(0,Wf/np.tan(dip),2500)
            H2 = 80 * np.sin(dip)
            H = 60 * np.sin(dip)
            h = 20 * np.sin(dip)
            Hs = [Wf,H,h]

            avs = 0.025
            if 'shallowVS' in prefix_in:
                avw_shallow = 0.02
            else:
                avw_shallow = 0.012
            avw_asperity = 0.011
            b = 0.015

            a = avs*np.ones(z.shape)
            if 'lina' in prefix_in or 'linear_base' in prefix_in:
                a[z < H2] = avs + (avs-avw_asperity)*(z[z < H2]-H2)/(H2-H)
                a[z < H] = avw_asperity*np.ones(z[z < H].shape)
                a[z < h] = avw_asperity + (avw_asperity-avw_shallow)*(z[z < h]-h)/h
            else:
                a[z < H] = avw_asperity*np.ones(z[z < H].shape)
                a[z < h] = avw_shallow*np.ones(z[z < h].shape)
            b = b*np.ones(a.shape)
            a_b = a - b

            if 'highsn' in prefix_in or 'linear_base' in prefix_in or 'linearsn' in prefix_in:
                sigma_vs = 50
                sigma_asperity = 50
            elif 'lowsn' in prefix_in:
                sigma_vs = 30
                sigma_asperity = 30                
            else:
                sigma_vs = 20
                sigma_asperity = 50
            sigma_shallow = 5
            cs0 = 3.464e3
            rho0 = 2.670
            if 'patchmu' in prefix_in:
                cs_high = 3.464e3
                cs_low = 2.887e3
                mu_sed = 6.8e9
                sed_xlim = 35
                sed_ylim = 5
            else:
                mu0 = cs0**2*rho0
            Vinit = 1.0e-9
            f0 = 0.6
            V0 = 1.0e-6
            Dc = 5e-3
            Dc_asperity = 1e-2
            Vp = 1e-9
            dmin,dmax=0.5,5
            others = [dmin,dmax,Vp,rho0,V0,f0]

            sigma0 = sigma_vs*np.ones(z.shape)
            if 'linear_base' in prefix_in or 'linearsn' in prefix_in:
                sigma0[z < H] = sigma_asperity*np.ones(z[z < H].shape)
                sigma0[z < h] = sigma_asperity + (sigma_asperity-sigma_shallow)*(z[z < h]-h)/h
            else:
                sigma0[z < H] = sigma_asperity*np.ones(z[z < H].shape)
                sigma0[z < h] = sigma_shallow*np.ones(z[z < h].shape)

            L = Dc*np.ones(z.shape)
            if 'lindc' in prefix_in or 'linear_base' in prefix_in:
                L[z < H2] = Dc + (Dc-Dc_asperity)*(z[z < H2]-H2)/(H2-H)
                L[z < H] = Dc_asperity*np.ones(z[z < H].shape)
                L[z < h] = Dc_asperity + (Dc_asperity-Dc)*(z[z < h]-h)/h
            else:
                L[z < H] = Dc_asperity*np.ones(z[z < H].shape)
                L[z < h] = Dc*np.ones(z[z < h].shape)
            
            if 'gradmu' in prefix_in:
                print('gradmu')
                mu = np.sqrt(z*60)+2.5
            elif 'patchmu' in prefix_in:
                print('patchmu')
                mu_high = cs_high**2*rho0
                mu_low = cs_low**2*rho0
                mu = mu_high*np.ones(z.shape)
                idx = np.where(x >= -z/np.tan(np.pi-dip))
                mu[idx] = mu_low*np.ones(mu[idx].shape)
                mu[idx][np.where(np.logical_and(x <= sed_xlim, y<= sed_ylim))] = \
                    mu_sed*np.ones(mu[idx][np.where(np.logical_and(x <= sed_xlim, y<= sed_ylim))].shape)
            else:
                mu = mu0*np.ones(z.shape)
            others.append(mu)
            eta = np.sqrt(mu * rho0) / 2.0
            Vi = Vinit*np.ones(z.shape)
            # tau0 = f0*sigma0
            e = np.exp((f0 + b * np.log(V0 / Vi)) / avs)
            tau0 = -(sigma0 * avs * np.arcsinh((Vi / (2.0 * V0)) * e) + eta * Vi)
            # tau0 = -(sigma0 * f0 + np.log(Vp/np.cos(dip)/V0))
            # tau0[z < h] = -sigma0[z < h] * f0
            
            return y,Hs,a,b,a_b,tau0,sigma0,L,others

        else:
            y,Hs,a,b,a_b,tau0,sigma0,L,others = self.base_val()

        return y,Hs,a,b,a_b,tau0,sigma0,L,others