#!/usr/bin/env python
# coding: utf-8



import sys
import ROOT
ROOT.gROOT.SetBatch(True)
import atlasplots as aplt
aplt.set_atlas_style()

import argparse
import logging
import re
import numpy as np

coef_latex = {
        "d[u,X,Z]" : r"$d_{\it u}^{\it X,Z}$",
        "d[u,Y,Z]" : r"$d_{\it u}^{\it Y,Z}$",
        "d[u,X-Y,X-Y]" : r"$d_{\it u}^{\it X-Y,X-Y}$",
        "d[u,X,Y]" :  r"$d_{\it u}^{\it X,Y}$",
        "c[u,X,Z]" : r"$c_{\it u}^{\it X,Z}$",
        "c[u,Y,Z]" : r"$c_{\it u}^{\it Y,Z}$",
        "c[u,X-Y,X-Y]" : r"$c_{\it u}^{\it X-Y,X-Y}$",
        "c[u,X,Y]" : r"$c_{\it u}^{\it X,Y}$",
        "c[d,X,Z]" : r"$c_{\it d}^{\it X,Z}$",
        "c[d,Y,Z]" : r"$c_{\it d}^{\it Y,Z}$",
        "c[d,X-Y,X-Y]" : r"$c_{\it d}^{\it X-Y,X-Y}$",
        "c[d,X,Y]" : r"$c_{\it d}^{\it X,Y}$"
    }

def get_model_str(coeff):
    m_list = {"d[u,X,Z]" : "1+mu*(6.28069*cos(sday)-41.0569*sin(sday))",
        "d[u,Y,Z]" : "1+mu*(41.0569*cos(sday)+6.28069*sin(sday))",
        "d[u,X-Y,X-Y]" : "1+mu*(77.6067*cos(2*sday)+24.3128*sin(2*sday))",
        "d[u,X,Y]" :  "1+mu*(-48.6256*cos(2*sday)+155.213*sin(2*sday))",
        "c[u,X,Z]" : "1+mu*(8.084*cos(sday)-52.8451*sin(sday))",
        "c[u,Y,Z]" : "1+mu*(52.8451*cos(sday)+8.084*sin(sday))",
        "c[u,X-Y,X-Y]" : "1+mu*(99.8891*cos(2*sday)+31.2935*sin(2*sday))",
        "c[u,X,Y]" : "1+mu*(-62.5869*cos(2*sday)+199.778*sin(2*sday))",
        "c[d,X,Z]" : "1+mu*(0.181551*cos(sday)-1.1868*sin(sday))",
        "c[d,Y,Z]" : "1+mu*(1.1868*cos(sday)+0.181551*sin(sday))",
        "c[d,X-Y,X-Y]" : "1+mu*(2.24331*cos(2*sday)+0.702788*sin(2*sday))",
        "c[d,X,Y]" : "1+mu*(-1.40558*cos(2*sday)+4.48662*sin(2*sday))"
    }

    return m_list[coeff]
    

def fit_to_data(coms=None):
    argparser = argparse.ArgumentParser(description='fit double ratio')
    argparser.add_argument('--input_list',required=True,
                           type=str, help='text file, contains list of root files')
    argparser.add_argument('--output',required=True,
                           type=str, help='output file name')
    
    argparser.add_argument('--id_regex', required=True, type=str,
                           help='regex <_seed(.+?).root> of root file name to find toy ID,')
    argparser.add_argument('--h_name', default="h_generated", help='histogram name')
    argparser.add_argument('--plot', type=int, nargs='+', default=1, help='sample ID for plot')
    argparser.add_argument('--ratio_plot', action='store_true', default=False, help='sample ID for plot')
    
    if coms:
        args = argparser.parse_args(coms)
    else:
        args = argparser.parse_args()
    
    #common
    sday = ROOT.RooRealVar("sday", "#omega T", 0, 6.28319)
    
    #create output file
    target_file = open(args.output, 'w')
    #create output file
    residual_file = open("residual_12func.txt", 'w')
    
    #read list of root files
    toy_files = open(args.input_list, 'r')
    root_list = toy_files.readlines()
    toy_files.close()
    
    if len(root_list)<1: 
        logging.error("root list is empty!")
        sys.exit()
        
    for iFile in root_list:
        iFile=iFile.strip()
        
        #get toy_ID
        try:
            toy_ID = re.search(args.id_regex, iFile).group(1)
        except AttributeError:
            # AAA, ZZZ not found in the original string
            logging.error("can not extract toy ID!")
            sys.exit()
        
        #store toy ID
        target_file.write(str(toy_ID)+' ')
        residual_file.write(str(toy_ID)+' ')
        
        #open the root file and get hist
        _f = ROOT.TFile.Open(iFile, 'r')
        h = _f.Get(args.h_name)
        h.SetDirectory(0)
        _f.Close()
        
        MaxYvalue = h.GetBinContent(h.GetMaximumBin())
        MinYvalue = h.GetBinContent(h.GetMinimumBin())
        MaxDelta = max(abs(1-MaxYvalue)*2., abs(1-MinYvalue)*2.)
        
        #Create data
        sigData = ROOT.RooDataHist("Data", "Data", [sday], Import=h)        
        sday.setBins(sigData.numEntries())
            
        #loop over models
        models = ["d[u,X,Z]", "d[u,Y,Z]", "d[u,X-Y,X-Y]", "d[u,X,Y]",
                 "c[u,X,Z]", "c[u,Y,Z]", "c[u,X-Y,X-Y]", "c[u,X,Y]",
                 "c[d,X,Z]", "c[d,Y,Z]", "c[d,X-Y,X-Y]", "c[d,X,Y]"]
        for model_str in models:
            #parameter of interest
            mu = ROOT.RooRealVar("mu", "mu", 0, -0.5, 0.5);
            model = ROOT.RooGenericPdf("sig", get_model_str(model_str),[sday, mu])
            
            model.chi2FitTo(sigData)
                        #ROOT.RooFit.RecoverFromUndefinedRegions(1.)
                        #ROOT.RooFit.IntegrateBins(0.)
                      
            
            par = mu.getValV()
            err = mu.getError()
            
            
            #Save fit results.
            chi2 = model.createChi2(sigData, #ROOT.RooFit.Range("fullRange"),
                                    ROOT.RooFit.DataError(ROOT.RooAbsData.SumW2)).getVal()
            degree_freedom = int(sigData.numEntries() - 1)
            chi2_p0 = ROOT.Math.chisquared_cdf_c(chi2, degree_freedom)
            
            #Store results to a text file 
            target_file.write(str(par)+' ')
            target_file.write(str(err)+' ')
            target_file.write(str(chi2)+' ')
            target_file.write(str(chi2_p0)+' ')
            
            frame = sday.frame(Title=model_str);
            sigData.plotOn(frame);
            model.plotOn(frame);
            frame.SetAxisRange(1-MaxDelta, 1+MaxDelta, "Y")
            frame.GetYaxis().SetTitle("R")
            frame.GetYaxis().SetTitleOffset(2)
            hresid = frame.residHist()
            residual  = sday.frame(Title="Residual Distribution")
            residual.addPlotable(hresid, "P")
            Nr = hresid.GetN()
            
            res_points = []
            mean_stats = []
            for i in range(Nr):
                res_points.append(  hresid.GetPointY(i))
                mean_stats.append( hresid. GetErrorY(i) )
                
            res_mean, res_std = np.mean(res_points), np.std(res_points)
            mean_stats = np.mean(mean_stats)
            residual_file.write(str(res_mean)+' ')
            residual_file.write(str(res_std)+' ')
            if model_str == models[-1]:
                residual_file.write(str(mean_stats))
                
            if  int(toy_ID) in  args.plot:
                if args.ratio_plot:
                    TopC, (Upad, Lpad) = aplt.ratio_plot(name="ratio_plot", figsize=(800, 800), hspace=0.05)
                    Upad.cd()
                    frame.Draw()
                    frame.GetXaxis().SetLabelOffset(2)
                    Upad.add_margins(left=0.15)
                    # Add the ATLAS Label
                    aplt.atlas_label(text="Internal", loc="upper left")
                    #Upad.text(0.2, 0.84, "#sqrt{s} = 13 TeV, 139 fb^{-1}", size=22, align=13)
                    Upad.text(0.2, 0.84, "#sqrt{s} = 13 TeV", size=22, align=13)
                    # Add extra space at top of plot to make room for labels
                    Upad.add_margins(top=0.15)
                    
                    Lpad.cd()
                    residual.GetYaxis().SetRangeUser(res_mean-3.5*res_std, res_mean+3.5*res_std,)
                    residual.GetYaxis().SetTitle("Data-Fit")
                    residual.GetYaxis().SetTitleOffset(2)
                    residual.Draw()
                    fConfidenceInterval1 = ROOT.TGraphErrors()
                    fConfidenceInterval2 = ROOT.TGraphErrors()
                    for i in range(Nr):
                        if i ==0:
                            fConfidenceInterval1.AddPoint(0,res_mean)
                            fConfidenceInterval2.AddPoint(0,res_mean)
                        elif i == Nr-1:
                            fConfidenceInterval1.AddPoint(6.28319,res_mean)
                            fConfidenceInterval2.AddPoint(6.28319,res_mean)
                        else:
                            fConfidenceInterval1.AddPoint(hresid.GetPointX(i),res_mean)
                            fConfidenceInterval2.AddPoint(hresid.GetPointX(i),res_mean)
                        fConfidenceInterval1.SetPointError(i, 0.0, res_std)
                        fConfidenceInterval2.SetPointError(i, 0.0, 2*res_std)
                    
                    fConfidenceInterval2.GetXaxis().SetRangeUser(0,6.28319)
                    fConfidenceInterval1.GetXaxis().SetRangeUser(0,6.28319)
                    fConfidenceInterval2.SetFillColor(ROOT.kGreen);
                    fConfidenceInterval1.SetFillColor(ROOT.kYellow);
                    fConfidenceInterval2.Draw("I3")
                    fConfidenceInterval1.Draw("3")
                    residual.Draw("same")
                    
                    line = ROOT.TLine(0, 0, 6.28319, 0)
                    Lpad.plot(line)
                    Lpad.add_margins(left=0.15)
                    TopC.savefig(("plots/fit_results_"+model_str+"_"+toy_ID+"_residual_12func.pdf"))
                
                fitDataFig, fitData = aplt.subplots(1, 1, name="fitplot", figsize=(800, 600))
                fitData.cd()
                frame.Draw()
                # Add the ATLAS Label
                aplt.atlas_label(text="Internal", loc="upper left")
                #fitData.text(0.2, 0.84, "#sqrt{s} = 13 TeV, 139 fb^{-1}", size=22, align=13)
                fitData.text(0.2, 0.84, "#sqrt{s} = 13 TeV", size=22, align=13)
                fitDataFig.savefig(("plots/fit_results_"+model_str+"_"+toy_ID+"_12func.pdf"))
                
                #create profile of mu
                print("Sday: ", sday.getValV())
                Scanfig, Scan = aplt.subplots(1, 1, name="Scan", figsize=(800, 600))
                Scan.cd()
                frame1 = mu.frame(Bins=1000, Range=(par-err*3, par+err*3), Title=f"{model_str}")
                chi2_pdf= model.createChi2(sigData,
                                    ROOT.RooFit.DataError(ROOT.RooAbsData.SumW2))
                #chi2_pdf.plotOn(frame1, LineColor="r")
                profile_mu = chi2_pdf.createProfile({mu})
                profile_mu.plotOn(frame1, LineColor="r")
                frame1.Draw()
                Scan.add_margins(left=0.15)
                #Scan.add_margins(top=0.15)
                # Add the ATLAS Label
                aplt.atlas_label(text="Internal", loc="upper left")
                #Scan.text(0.2, 0.84, "#sqrt{s} = 13 TeV, 139 fb^{-1}", size=22, align=13)
                Scan.text(0.2, 0.84, "#sqrt{s} = 13 TeV", size=22, align=13)
                Scanfig.savefig(("plots/profile_chi2PDF_"+model_str+"_"+toy_ID+"_12func.pdf"))
                #print(f"chi2_pdf: {chi2_pdf.getVal()}")
                
        target_file.write('\n') # start new line
        residual_file.write('\n') # start new line
        
    target_file.close()
    residual_file.close()
    
    



def main():
    fit_to_data()
    
if __name__=="__main__":
    main()




