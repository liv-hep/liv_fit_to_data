#!/usr/bin/env python
# coding: utf-8



import sys
import ROOT
ROOT.gROOT.SetBatch(True)
import argparse
import logging
import re

def get_model_str(coeff):
    m_list = {"line":"(1+mu)/6.28319",
        "d[u,X,Z]" : "1+mu*(6.28069*cos(sday)-41.0569*sin(sday))",
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
                           help='regex of root file name to find toy ID')
    argparser.add_argument('--h_name', default="h_generated", help='histogram name')
    argparser.add_argument('--plot', type=int, default=None, help='sample ID for plot')
    
    if coms:
        args = argparser.parse_args(coms)
    else:
        args = argparser.parse_args()
    
    #common
    sday = ROOT.RooRealVar("sday", "sday", 0, 6.28319)
    
    #create output file
    target_file = open(args.output, 'w')
    
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
        
        #open the root file and get hist
        _f = ROOT.TFile.Open(iFile, 'r')
        h = _f.Get(args.h_name)
        h.SetDirectory(0)
        _f.Close()
        
        
        #Create data
        sigData = ROOT.RooDataHist("Data", "Data", [sday], Import=h)        
        sday.setBins(sigData.numEntries())
            
        #loop over models
        models = ["d[u,X,Z]", "d[u,Y,Z]", "d[u,X-Y,X-Y]", "d[u,X,Y]",
                 "c[u,X,Z]", "c[u,Y,Z]", "c[u,X-Y,X-Y]", "c[u,X,Y]",
                 "c[d,X,Z]", "c[d,Y,Z]", "c[d,X-Y,X-Y]", "c[d,X,Y]", "line"]
        for model_str in models:
            #parameter of interest
            if model_str == "line":
                mu = ROOT.RooRealVar("mu", "mu", 0, -1.5, 1.5);
                model = ROOT.RooGenericPdf("sig", get_model_str(model_str),[mu])
            else:
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
            
            if  args.plot==int(toy_ID):
                frame = sday.frame(Title=model_str);
                sigData.plotOn(frame);
                model.plotOn(frame);
                frame.SetAxisRange(0.996, 1.004, "Y");
                fitData = ROOT.TCanvas("fit");
                fitData.cd();
                frame.Draw();
                fitData.SaveAs(("fit_results_"+model_str+"_"+toy_ID+".root"))
                fitData.SaveAs(("fit_results_"+model_str+"_"+toy_ID+".pdf"))
                
                #create profile of mu
                print("Sday: ", sday.getValV())
                can_mu = ROOT.TCanvas("mu")
                can_mu.cd()
                frame1 = mu.frame(Bins=1000, Range=(par-err*3, par+err*3), Title=f"{model_str}")
                chi2_pdf= model.createChi2(sigData,
                                    ROOT.RooFit.DataError(ROOT.RooAbsData.SumW2))
                #chi2_pdf.plotOn(frame1, LineColor="r")
                profile_mu = chi2_pdf.createProfile({mu})
                profile_mu.plotOn(frame1, LineColor="r")
                frame1.Draw()
                can_mu.SaveAs(("profile_chi2PDF_"+model_str+"_"+toy_ID+".pdf"))
                #print(f"chi2_pdf: {chi2_pdf.getVal()}")
                
        target_file.write('\n') # start new line
        
    target_file.close()
    
    



def main():
    fit_to_data()
    
if __name__=="__main__":
    main()




