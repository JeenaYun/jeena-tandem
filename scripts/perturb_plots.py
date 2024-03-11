import numpy as np
import matplotlib.pylab as plt
import myplots
import pandas as pd
mp = myplots.Figpref()
plt.rcParams['font.size'] = '15'

def plot_triggering_response(law='aging'):
    if law == 'aging': resp = pd.read_csv('perturb_stress/triggering_response_aging.csv')
    elif law == 'NnDaging': resp = pd.read_csv('perturb_stress/triggering_response_NnDaging.csv')
    peak_dynamic = resp['Peak Dynamic \n dCFS [MPa]']
    static = resp['Static \n dCFS [MPa]']
    t_response = resp['Time \n Difference [h]']

    plt.subplots(figsize=(11,8))
    cb = plt.scatter(peak_dynamic,static,150,c=t_response,vmin=t_response.min(),vmax=t_response.max(),ec='k',marker='s',cmap='PuBu_r',zorder=3)
    plt.colorbar(cb).set_label('Triggering Response [hr]',fontsize=17,rotation=270,labelpad=30)
    plt.xlabel('Peak Dynamic Stress Change at the Hypocenter [MPa]',fontsize=17)
    plt.ylabel('Static Stress Change at the Hypocenter [MPa]',fontsize=17)
    plt.grid(True,alpha=0.5)
    plt.tight_layout()
    plt.show()