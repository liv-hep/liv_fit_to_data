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
        plt.xlim(-1e-5, 1e-5)
        plt.savefig(f"SigFit_summary_sample{sp}.pdf", bbox_inches='tight')
        plt.cla()
            

            
null_spurious_results = "/Users/abletimin/cernbox/LIV/software/null_test/null_test_results.txt"

col_names = ["sample ID"]
parameters = ["d[u,X,Z]", "d[u,Y,Z]", "d[u,X-Y,X-Y]", "d[u,X,Y]",
              "c[u,X,Z]", "c[u,Y,Z]", "c[u,X-Y,X-Y]", "c[u,X,Y]",
              "c[d,X,Z]", "c[d,Y,Z]", "c[d,X-Y,X-Y]", "c[d,X,Y]"]
for d in parameters:
    col_names += [d, f"{d}_err", f"{d}_chi2_ndf", f"{d}_chi2_p0"]
spurious_tests = pd.read_csv(null_spurious_results, sep=' ',index_col=False, names=col_names)
Pars = spurious_tests[parameters]



plot_each_sample(spurious_tests, sp_ids=[0,1])

pd_stats = pd.DataFrame()
pd_stats["sample ID"] = [0]
fig, axes =  plt.subplots(1,1, sharey=True,figsize=(6,6))
for d in parameters:
    axes.hist(Pars[d].to_numpy(), bins=100, label=d)
    plt.xlabel(f"coefficient {d}")
    plt.ylabel("counts")
    #plt.title("Null samples: spurious signal test")
    plt.xlim(-1e-5, 1e-5)
    plt.ylim(0, 40)
    plt.text(3e-6, 35, f"mean: {Pars[d].mean():.3e}")
    plt.text(3e-6, 30, f"std: {Pars[d].std():.3e}")
    pd_stats[d] = Pars[d].mean()
    pd_stats[f"{d}_err"] = Pars[d].std()
    #plt.show()
    plt.savefig(f"distribution_plots_{d}.pdf", bbox_inches='tight')
    plt.cla()



chi2_p0 = spurious_tests[[f"{i}_chi2_p0" for i in parameters]]
fig, axes =  plt.subplots(1,1, sharey=True,figsize=(6,6))
for d in parameters:
    axes.hist(chi2_p0[f"{d}_chi2_p0"].to_numpy(), bins=100, label=d)
    plt.xlabel(f"chi2_p0: {d}")
    plt.ylabel("counts")
    #plt.title("Null samples: spurious signal test")
    #plt.xlim(-1e-5, 1e-5)
    plt.ylim(0, 40)
    #plt.text(3e-6, 35, f"mean: {chi2_p0[f'{d}_chi2_p0'].mean():.3e}")
    #plt.text(3e-6, 30, f"std: {chi2_p0[f'{d}_chi2_p0'].std():.3e}")
    #plt.show()
    plt.savefig(f"Stats_chi2_p0_test_{d}.pdf", bbox_inches='tight')
    plt.cla()



sample_id=0
fig, axes =  plt.subplots(1,1, sharey=True,figsize=(4,10))
plot_sample(axes, pd_stats, sample_id)
#plot_sample(axes, df_truth, sp, truth=True)
#axes.set_title("Null 1K samples: summary ")
plt.setp(axes, yticks=[i for i in range(len(parameters))], yticklabels=parameters)
plt.yticks([i for i in range(len(parameters))])
plt.xlabel("average value")
#plt.ylabel("coefficient $d_{i}$")
plt.xlim(-5e-5, 5e-5)
plt.xticks([-5e-5,-4e-5,-3e-5,-2e-5,-1e-5,0, 1e-5, 2e-5, 3e-5, 4e-5, 5e-5])
plt.savefig(f"SigFit_summary_AllSamples.pdf", bbox_inches='tight')






