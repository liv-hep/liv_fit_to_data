#!/usr/bin/env python
# coding: utf-8


import pandas as pd
import numpy as np
#pd.options.display.float_format = '{:,.5e}'.format

from matplotlib import ticker
formatter = ticker.ScalarFormatter(useMathText=True)
formatter.set_scientific(True)
formatter.set_powerlimits((0,1))

import matplotlib.pyplot as plt
params = {'legend.fontsize': 'x-large',
         'axes.labelsize': 'x-large',
         'axes.titlesize':20,
         'xtick.labelsize':20,
         'ytick.labelsize':20}
plt.rcParams.update(params)

import mplhep as hep
#hep.style.use(hep.style.ROOT) # For now ROOT defaults to CMS
# Or choose one of the experiment styles
#hep.style.use(hep.style.ATLAS)
plt.style.use(hep.style.ATLAS)

coef_latex = {
        "d[u,X,Z]" : r"$d_{\it u}^{\it X,Z}$",
        "d[u,Y,Z]" : r"$d_{\it u}^{\it Y,Z}$",
        "d[u,X-Y,X-Y]" : r"$d_{\it u}^{\it XX-YY}$",
        "d[u,X,Y]" :  r"$d_{\it u}^{\it X,Y}$",
        "c[u,X,Z]" : r"$c_{\it u}^{\it X,Z}$",
        "c[u,Y,Z]" : r"$c_{\it u}^{\it Y,Z}$",
        "c[u,X-Y,X-Y]" : r"$c_{\it u}^{\it XX-YY}$",
        "c[u,X,Y]" : r"$c_{\it u}^{\it X,Y}$",
        "c[d,X,Z]" : r"$c_{\it d}^{\it X,Z}$",
        "c[d,Y,Z]" : r"$c_{\it d}^{\it Y,Z}$",
        "c[d,X-Y,X-Y]" : r"$c_{\it d}^{\it XX-YY}$",
        "c[d,X,Y]" : r"$c_{\it d}^{\it X,Y}$"
    }

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
            
        for i, d in enumerate(pars[:-4]):
            par = sample[d].values[0]
            err = sample["%s_err"%d].values[0]
            plot_err(ax[1],x=par,y=i,xerr=err,yerr=None) #plot one and two sigma err
            
        for i, d in enumerate(pars[-4:]):
            par = sample[d].values[0]
            err = sample["%s_err"%d].values[0]
            plot_err(ax[0],x=par,y=i,xerr=err,yerr=None) #plot one and two sigma err
            


import argparse

parser = argparse.ArgumentParser(description='Results based on many samples')
parser.add_argument('--input_file', type=str, help='name of input files produced from fit script')

args = parser.parse_args()
            
null_spurious_results = args.input_file

col_names = ["sample ID"]
parameters = ["d[u,X,Z]", "d[u,Y,Z]", "d[u,X-Y,X-Y]", "d[u,X,Y]",
              "c[u,X,Z]", "c[u,Y,Z]", "c[u,X-Y,X-Y]", "c[u,X,Y]",
              "c[d,X,Z]", "c[d,Y,Z]", "c[d,X-Y,X-Y]", "c[d,X,Y]"]
for d in parameters:
    col_names += [d, f"{d}_err", f"{d}_chi2", f"{d}_chi2_p0"]
spurious_tests = pd.read_csv(null_spurious_results, sep=' ',index_col=False, names=col_names)
Pars = spurious_tests[parameters]



pd_stats = pd.DataFrame()
pd_stats["sample ID"] = [0]
fig, axes =  plt.subplots(1,1,figsize=(6,6))
#axes.xaxis.set_major_formatter(formatter)
for d in parameters:
    axes.hist(Pars[d].to_numpy(), bins=20, label=d)
    plt.xlabel(r"coefficient"+coef_latex[d])
    plt.ylabel("counts")
    #plt.title("Null samples: spurious signal test")
    #plt.xlim(-1e-5, 1e-5)
    #plt.ylim(0, 40)
    #plt.text(3e-6, 35, f"mean: {Pars[d].mean():.3e}")
    #plt.text(3e-6, 30, f"std: {Pars[d].std():.3e}")
    pd_stats[d] = Pars[d].mean()
    pd_stats[f"{d}_err"] = Pars[d].std()
    #plt.show()
    plt.savefig(f"distribution_plots_{d}.pdf", bbox_inches='tight')
    plt.cla()

#plot Err distributions
fig, axes =  plt.subplots(1,1,figsize=(6,6))
for d in parameters:
    #axes.xaxis.set_major_formatter(formatter)
    _values = spurious_tests[f"{d}"]
    _errors = spurious_tests[f"{d}_err"]
    _rel =_errors.to_numpy()/_values.to_numpy()
    _rel = np.abs(_rel)
    axes.hist(_errors, bins=20, label=coef_latex[d]+f": {_errors.mean()} ")
    plt.legend()
    #plt.xlabel(f"coefficient {d} - STD")
    plt.ylabel("counts")
    #plt.title("Null samples: spurious signal test")
    #plt.xlim(-1e-5, 1e-5)
    #plt.ylim(0, 40)
    #plt.text(3e-6, 35, f"mean: {Pars[d].mean():.3e}")
    #plt.text(3e-6, 30, f"std: {Pars[d].std():.3e}")
    #pd_stats[d] = Pars[d].mean()
    #pd_stats[f"{d}_err"] = Pars[d].std()
    #plt.show()
    plt.savefig(f"distribution_plots_{d}_errs.pdf", bbox_inches='tight')
    plt.cla()


chi2_p0 = spurious_tests[[f"{i}_chi2_p0" for i in parameters]]
fig, axes =  plt.subplots(1,1, sharey=True,figsize=(6,6))
for d in parameters:
    axes.hist(chi2_p0[f"{d}_chi2_p0"].to_numpy(), bins=20, label=d)
    plt.xlabel("chi2_p0: "+coef_latex[d])
    plt.ylabel("counts")
    #plt.title("Null samples: spurious signal test")
    #plt.xlim(-1e-5, 1e-5)
    plt.ylim(0, 40)
    #plt.text(3e-6, 35, f"mean: {chi2_p0[f'{d}_chi2_p0'].mean():.3e}")
    #plt.text(3e-6, 30, f"std: {chi2_p0[f'{d}_chi2_p0'].std():.3e}")
    #plt.show()
    plt.savefig(f"Stats_chi2_p0_test_{d}.pdf", bbox_inches='tight')
    plt.cla()

chi2 = spurious_tests[[f"{i}_chi2" for i in parameters]]
fig, axes =  plt.subplots(1,1, sharey=True,figsize=(6,6))
for d in parameters:
    axes.hist(chi2[f"{d}_chi2"].to_numpy(), bins=20, label=d)
    plt.xlabel("chi2: "+coef_latex[d])
    plt.ylabel("counts")
    #plt.title("Null samples: spurious signal test")
    #plt.xlim(-1e-5, 1e-5)
    #plt.ylim(0, 40)
    #plt.text(3e-6, 35, f"mean: {chi2_p0[f'{d}_chi2_p0'].mean():.3e}")
    #plt.text(3e-6, 30, f"std: {chi2_p0[f'{d}_chi2_p0'].std():.3e}")
    #plt.show()
    plt.savefig(f"Stats_chi2_test_{d}.pdf", bbox_inches='tight')
    plt.cla()



sample_id=0
fig, axes =  plt.subplots(2,1,figsize=(5,12), gridspec_kw={'height_ratios': [1,2]})
plot_sample(axes, pd_stats, sample_id)
#axes[0].set_title("Sample %i"%sp)
labels_latex = [coef_latex[l] for l in parameters ]
axes[1].set_yticks(list(range(len(parameters)-4)), labels_latex[:-4])
axes[0].set_yticks(list(range(4)), labels_latex[-4:])
        
axes[1].set_xlabel("Average fitted value")
        
axes[1].xaxis.set_major_formatter(formatter)
axes[0].xaxis.set_major_formatter(formatter)

axes[0].xaxis.set_major_locator(plt.MaxNLocator(6))
axes[1].xaxis.set_major_locator(plt.MaxNLocator(6))

hep.atlas.text(text="Internal", loc=0, ax=axes[0])
hep.atlas.label(data=True, loc=0,lumi=139, com=13, ax=axes[0])

plt.savefig(f"SigFit_summary_AllSamples.pdf", bbox_inches='tight')


#print starts
print("                value           err    ")
for p in parameters[::-1]:
    print(f"{p:12}: ", f"{pd_stats[p].loc[0]: 1.4E} +/-", f"{pd_stats[p+'_err'].loc[0]:1.4E}")



