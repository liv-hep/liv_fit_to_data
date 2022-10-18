#!/usr/bin/env python
# coding: utf-8


import pandas as pd
pd.options.display.float_format = '{:,.5e}'.format

import matplotlib.pyplot as plt
params = {'legend.fontsize': 'x-large',
         'axes.labelsize': 'x-large',
         'axes.titlesize':20,
         'xtick.labelsize':20,
         'ytick.labelsize':20}
plt.rcParams.update(params)

def plot_err(ax,x,y,xerr=None,yerr=None, color='black'):
    #2 sigma
    xerr_2 = None if xerr is None else  2*xerr
    yerr_2 = None if yerr is None else  2*yerr
    
    if xerr is None and yerr is None:
        label = "Truth"
    else:
        label = "Estimated"
    ax.errorbar(x, y, xerr = xerr_2, yerr=yerr_2, 
               fmt = 'o',color = 'black', 
               ecolor = 'orange', 
               elinewidth = 5, capsize=8, alpha=0.75 )
    
    ax.errorbar(x, y, xerr = xerr, yerr=yerr, 
               fmt = 'o',color = color, 
               ecolor = 'green', 
               elinewidth = 7, capsize=10, label=label)
    ax.axvline(x=0.0, color='k', ls='--') 
    
    
def plot_sample(ax, pd_data, sample_ID, truth=False):
    sample = pd_data[pd_data["sample ID"]==sample_ID]
    pars = parameters
    
    #plot truth
    if truth:
        for i, d in enumerate(pars):
            par = sample[d].values[0]
            plot_err(ax,x=par,y=i,xerr=None,yerr=None, color='red')
    else:
            
        for i, d in enumerate(pars):
            par = sample[d].values[0]
            err = sample["%s_err"%d].values[0]
            plot_err(ax,x=par,y=i,xerr=err,yerr=None) #plot one and two sigma err
            

def plot_each_sample(pd_data, sp_ids):
    y_list = [i for i in range(len(parameters))]
    fig, axes =  plt.subplots(1,1, sharey=True,figsize=(4,10))
    for sp in sp_ids:
        plot_sample(axes, pd_data, sp)
        axes.set_title("Sample %i"%sp)
        plt.setp(axes, yticks=y_list, yticklabels=parameters)
        plt.yticks(y_list)
        plt.xlabel("fitted value")
        #plt.ylabel("coefficient $d_{i}$")
        plt.xlim(-5e-5, 5e-5)
        plt.xticks([i*1e-5 for i in range(-5,5,)])
        plt.savefig(f"SigFit_summary_sample{sp}.pdf", bbox_inches='tight')
        plt.cla()
            


import argparse

parser = argparse.ArgumentParser(description='Results based on many samples')
parser.add_argument('--input_file', type=str, help='name of input files produced from fit script')
parser.add_argument('--sample_ids', default=0, nargs='+', type=int, help='Sample ID')
parser.add_argument('--print', default=False, action='store_true', help='print fit values')
args = parser.parse_args()
            
null_spurious_results = args.input_file

col_names = ["sample ID"]
parameters = ["d[u,X,Z]", "d[u,Y,Z]", "d[u,X-Y,X-Y]", "d[u,X,Y]",
              "c[u,X,Z]", "c[u,Y,Z]", "c[u,X-Y,X-Y]", "c[u,X,Y]",
              "c[d,X,Z]", "c[d,Y,Z]", "c[d,X-Y,X-Y]", "c[d,X,Y]"]
for d in parameters:
    col_names += [d, f"{d}_err", f"{d}_chi2_ndf", f"{d}_chi2_p0"]
spurious_tests = pd.read_csv(null_spurious_results, sep=' ',index_col=False, names=col_names)
Pars = spurious_tests[parameters]



plot_each_sample(spurious_tests, sp_ids=args.sample_ids)


if args.print:
    for i in args.sample_ids:
        _sample = spurious_tests[spurious_tests["sample ID"]==i]
        #print starts
        print(f"Sample {i}:            value           err    ")
        for p in parameters[::-1]:
            print(f"{p:12}: ", f"{_sample[p].values[0]: 1.4E} +/-", f"{_sample[p+'_err'].values[0]:1.4E}")
        print('\n')



