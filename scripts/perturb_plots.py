import numpy as np
import matplotlib.pylab as plt
import myplots
import pandas as pd
mp = myplots.Figpref()
plt.rcParams['font.size'] = '15'

def pub_triggering_response(ax,ref,pert,after_pert,lag,noline,after_tstart):
    ref_outputs = np.copy(ref.outputs)
    after_pert_outputs = np.copy(after_pert.outputs)
    ref_outputs[:,:,0] = ref_outputs[:,:,0] - ref.tstart[ref.idx]
    after_pert_outputs[:,:,0] = after_pert_outputs[:,:,0] - ref.tstart[ref.idx]
    tvar = 'sliprate'
    inc1,inc2 = 1e3,5e4
    if lag > 0:
        time_tag = "advance"
        xlmin,xlmax = -10*3600, 5*3600
    else:
        time_tag = "delay"
        xlmin,xlmax = -5*3600, 10*3600
    i1 = np.where(np.logical_and(ref_outputs[0,:,0] >= xlmin, ref_outputs[0,:,0] <= xlmax))[0]
    _,max_ref = fout_time_max(ax,ref_outputs[:,i1,:],tvar,lab='Unperturbed',plot_in_sec=True,col='k')
    _,max_after_pert = fout_time_max(ax,after_pert_outputs[:,1:,:],tvar,lab='Perturbed',plot_in_sec=True,col=mp.myblue)
    xl = [xlmin,xlmax]
    yl = ax.get_ylim()
    ax.vlines(x=0,ymin=yl[0]*2,ymax=yl[1]*2,lw=2.5,colors='0.62',linestyles='--',zorder=0)
    ax.text((xl[1]-xl[0])*0.01,-yl[1]*2.5,'Unperturbed event time',fontsize=13,color='0.62',fontweight='bold')
    ax.vlines(x=(after_tstart-ref.tstart[ref.idx]),ymin=yl[0]*2,ymax=yl[1]*2,lw=2.5,colors=mp.mynavy,linestyles='--',zorder=0)
    ax.text((after_tstart-ref.tstart[ref.idx])+(xl[1]-xl[0])*0.01,-yl[1]*2.5,'Perturbed event time',fontsize=13,color=mp.mynavy,fontweight='bold')
    if abs(lag) < 3600:
        ax.text(xl[1]-(xl[1]-xl[0])*0.025,yl[1]*0.75,'Time %s of %g s'%(time_tag,abs(lag)),fontsize=20,color='k',fontweight='bold',ha='right',va='top')
        ax.set_xlabel('Time relative to the unperturbed event [s]',fontsize=17)
    else:
        ax.text(xl[1]-(xl[1]-xl[0])*0.025,yl[1]*0.75,'Time %s of %1.1f hr'%(time_tag,abs(lag)/3600),fontsize=20,color='k',fontweight='bold',ha='right',va='top')
        xt = np.linspace(xlmin,xlmax,8)
        xtl = ['%d'%(ixt/3600) for ixt in xt]
        ax.set_xticks(ticks=xt,labels=xtl)
        ax.set_xlabel('Time relative to the unperturbed event time [hr]',fontsize=17)
    ax.set_ylabel('log$_{10}$(Peak Slip Rate [m/s])',fontsize=17)
    ax.set_xlim(xl)
    minsr = min([min(max_ref),min(max_after_pert)])
    maxsr = max([max(max_ref),max(max_after_pert)])
    ax.set_ylim(minsr-(yl[1]-maxsr),yl[1])
    # ax.set_ylim(-yl[1]*6.5,yl[1])
    ax.legend(fontsize=15,loc='upper left')
    ax.grid(True,alpha=0.5)
    return ax

def triggering_response(ax,ref,pert,after_pert,lag,noline=False):
    tvar = 'sliprate'
    inc1,inc2 = 1e3,5e4
    i1 = np.where(np.logical_and(ref.outputs[0,:,0]>=pert.outputs[0,0,0]-inc1,ref.outputs[0,:,0]<=after_pert.outputs[0,-1,0]+inc2))[0]
    fout_time_max(ax,ref.outputs[:,i1,:],tvar,plot_in_sec=True,lab='Unperturbed',col='k')
    fout_time_max(ax,pert.outputs[:,1:,:],tvar,plot_in_sec=True,lab='During perturbation',col=mp.mypink)
    time_tag = "advance" if lag > 0 else "delay"
    fout_time_max(ax,after_pert.outputs[:,1:,:],tvar,plot_in_sec=True,lab='After perturbation',col=mp.myblue)
    yl = ax.get_ylim()
    ax.vlines(x=ref.tstart[ref.idx],ymin=yl[0],ymax=yl[1],lw=2.5,colors='0.62',linestyles='--',zorder=0)
    if not noline :
        ax.vlines(x=after_pert.tstart[after_pert.system_wide],ymin=yl[0],ymax=yl[1],lw=2.5,colors=mp.mynavy,linestyles='--',zorder=0)
    xl = ax.get_xlim()
    ax.text(ref.tstart[ref.idx]+(xl[1]-xl[0])*0.01,-yl[1]*3.8,'Event %d'%(ref.idx),fontsize=13,color='0.62',fontweight='bold')
    if abs(lag) < 3600:
        ax.text(xl[1]-(xl[1]-xl[0])*0.025,yl[1]*0.75,'Time %s of %1.4f s'%(time_tag,abs(lag)),fontsize=20,color='k',fontweight='bold',ha='right',va='top')
    else:
        ax.text(xl[1]-(xl[1]-xl[0])*0.025,yl[1]*0.75,'Time %s of %1.4f hr'%(time_tag,abs(lag)/3600),fontsize=20,color='k',fontweight='bold',ha='right',va='top')
    ax.legend(fontsize=15,loc='upper left')
    return ax

def fout_time(ax,outputs,dep,target_depth,target_var,plot_in_sec,ls='-',col='k',lab='',abs_on=False,t0=0):
    time,var,xlab,ylab,fign,indx = get_var(outputs,dep,target_depth,target_var,plot_in_sec,abs_on)
    ax.plot(time-t0,var,color=col, lw=2.5,label=lab,linestyle=ls)
    ax.set_xlabel(xlab,fontsize=17)
    ax.set_ylabel(ylab,fontsize=17)
    if target_depth < 1e-1:
        ax.set_title('Depth = surface',fontsize=20,fontweight = 'bold')
    else:
        ax.set_title('Depth = %1.2f [km]'%abs(dep[indx]),fontsize=20,fontweight = 'bold')

def fout_time_max(ax,outputs,target_var,plot_in_sec,toff=0,ls='-',col='k',lab='',abs_on=False):
    time,var,xlab,ylab,fign,_ = get_var(outputs,None,None,target_var,plot_in_sec,abs_on)
    if abs(toff) > 0: time += toff
    ax.plot(time,var,color=col, lw=2.5,label=lab,linestyle=ls)
    ax.set_xlabel(xlab,fontsize=17)
    ax.set_ylabel(ylab,fontsize=17)
    return ax,var
# def fout_time_max(ax,outputs,target_var,plot_in_sec,toff=0,ls='-',col='k',lab='',abs_on=False):
#     time,var,xlab,ylab,fign,_ = get_var(outputs,None,None,target_var,plot_in_sec,abs_on)
#     if abs(toff) > 0: time += toff
#     ax.plot(time,var,color=col, lw=2.5,label=lab,linestyle=ls)
#     ax.set_xlabel(xlab,fontsize=17)
#     ax.set_ylabel(ylab,fontsize=17)
#     return ax,var

def fout_time_max_diff(ax,outputs,outputs2,target_var,plot_in_sec,ls='-',col='k',lab='',abs_on=False):
    time1,var1,xlab,ylab,fign,_ = get_var(outputs,None,None,target_var,plot_in_sec,abs_on)
    time2,var2,_,_,_,_ = get_var(outputs2,None,None,target_var,plot_in_sec,abs_on)
    ax.plot(time,var2-var1,color=col,lw=2,label=lab,linestyle=ls)
    ax.set_xlabel(xlab,fontsize=17)
    ax.set_ylabel(ylab,fontsize=17)
    return ax

def get_var(outputs,dep,target_depth,target_var,plot_in_sec,abs_on):
    if target_depth == None:
        print('Mode: Maximum along fault')
        indx = None
    else:
        indx = np.argmin(abs(abs(dep) - abs(target_depth)))
        print('Depth = %1.2f [km]'%abs(dep[indx]))

    if target_var == 'state':
        var_idx,ylab,fign = 1,'State Variable','state'
    elif target_var == 'slip':
        var_idx,ylab,fign = 2,'Cumulative Slip [m]','cumslip'
    elif target_var == 'shearT':
        var_idx,ylab,fign = 3,'Shear Stress [MPa]','shearT'
    elif target_var == 'sliprate':
        var_idx,ylab,fign = 4,'log$_{10}$(Slip Rate [m/s])','sliprate'
    elif target_var == 'normalT':
        var_idx,ylab,fign = 5,'Normal Stress [MPa]','normalT'

    if target_depth == None:
        if var_idx == 4:
            var = np.log10(np.max(np.array(outputs[:,:,var_idx]),axis=0))
        else:
            var = np.max(np.array(outputs[:,:,var_idx]),axis=0)
        ylab = 'Peak ' + ylab
    else:
        if var_idx == 4:
            if np.all(np.array(outputs[indx])[:,var_idx]>0):
                var = np.log10(np.array(outputs[indx])[:,var_idx])
            else:
                print('Negative slip rate - taking absolute')
                var = np.log10(abs(np.array(outputs[indx])[:,var_idx]))
        else:
            var = np.array(outputs[indx])[:,var_idx]
    if abs_on:
        var = abs(var)
        ylab = 'Absolute ' + ylab
    if plot_in_sec:
        time = np.array(outputs[0])[:,0]
        xlab = 'Time [s]'
    else:
        time = np.array(outputs[0])[:,0]/sc.yr2sec
        xlab = 'Time [yrs]'
    return time,var,xlab,ylab,fign,indx

def compare_dCFS_at_depth(ax,dCFSt_in,time_in,dCFSt_out,time_out,ls1='-',ls2='-',col1='k',col2=mp.myburgundy,lab1='',lab2=''):
    ax.plot(time_in,dCFSt_in,color=col1,lw=2,label='Input (SeisSol)'+lab1,linestyle=ls1,zorder=3)
    ax.plot(time_out,dCFSt_out,color=col2,lw=2,label='Output (Tandem)'+lab2,linestyle=ls2,zorder=3)
    ax.hlines(y=0,xmin=0,xmax=int(len(time_in)*0.01),linestyle='--',lw=2,color='0.62')
    ax.set_xlabel('Time Since Perturbation [s]',fontsize=17)
    ax.set_ylabel(r'$\Delta$CFS [MPa]',fontsize=17)
    ax.grid(True,alpha=0.5)
    return ax

def plot_summary(law='aging'):
    if law == 'aging': resp = pd.read_csv('perturb_stress/triggering_response_aging.csv',skiprows=1)
    elif law == 'LnDaging': resp = pd.read_csv('perturb_stress/triggering_response_LnDaging.csv')
    peak_dynamic = resp['Peak Dynamic \n dCFS [MPa]']
    static = resp['Static \n dCFS [MPa]']
    t_response = resp['Time \n Difference [h]']

    fig,ax = plt.subplots(figsize=(11,8))
    cb = ax.scatter(peak_dynamic,static,150,c=t_response,vmin=t_response.min(),vmax=t_response.max(),ec='k',marker='s',cmap='PuBu_r',zorder=3)
    plt.colorbar(cb).set_label('Triggering Response [hr]',fontsize=17,rotation=270,labelpad=30)
    ax.set_xlabel('Peak Dynamic Stress Change at the Hypocenter [MPa]',fontsize=17)
    ax.set_ylabel('Static Stress Change at the Hypocenter [MPa]',fontsize=17)
    ax.grid(True,alpha=0.5)
    return ax