import os
import sys
from argparse import ArgumentParser

import ROOT

"""
    SNDLHCplotter.py    A multi-purpose histogram plotter for SND@LHC (D. Centanni 2023)

    Command-Line Usage
    ------------------
    To run the script, open a terminal and execute the following command:
    python -i SNDLHCplotter.py [options] [arguments]

    | Option            | Description                                                                                           |
    | ----------------- | ----------------------------------------------------------------------------------------------------- |
    | --help            | Show the help message and exit.                                                                       |
    | -f, --inputFile   | Specify the input file path.                                                                          |
    | -c, --inputCanvas | Specify the input canvas file path.                                                                   |
    | -e, --extratext   | Add extratext below the SND@LHC writing.                                                              |
    | -hname            | Specify the name(s) of the histogram(s) to be plotted.                                                |
    | --scale           | Specify the scale factor to be applied to each histogram.                                             |
    | --auto            | Enables the auto mode: automatically plots histograms according to the arguments provided.            |
    | --dataMC          | Enables the Data-MonteCarlo comparison mode: data histogram must contain DATA in its name! (for now). |

    Examples
    --------
    1. Auto-mode, single histogram:
        python -i SNDLHCplotter.py -f histofile.root -hname Nscifi_hits -e Preliminary --auto
    2. Auto-mode, multi histograms:
        python -i SNDLHCplotter.py -f histofile.root -hname Nscifi_hits1 Nscifi_hits3 Nscifi_hits3 -e Preliminary --auto
    3. Auto-mode, Data-Montecarlo comparison:
        python -i SNDLHCplotter.py -f histofile.root -hname DATA_Nscifi_hits MC_Nscifi_hits --auto
    4. ...

    Still WIP
"""


def init_style():

    #for the canvas:
    ROOT.gStyle.SetCanvasBorderMode(0)
    ROOT.gStyle.SetCanvasColor(ROOT.kWhite)
    ROOT.gStyle.SetCanvasDefH(600) #Height of canvas
    ROOT.gStyle.SetCanvasDefW(600) #Width of canvas
    ROOT.gStyle.SetCanvasDefX(10)   #Position on screen
    ROOT.gStyle.SetCanvasDefY(10)


    ROOT.gStyle.SetPadBorderMode(0)
    ROOT.gStyle.SetPadColor(ROOT.kWhite)
    ROOT.gStyle.SetPadGridX(False)
    ROOT.gStyle.SetPadGridY(False)
    ROOT.gStyle.SetGridColor(0)
    ROOT.gStyle.SetGridStyle(3)
    ROOT.gStyle.SetGridWidth(1)

    #For the frame:
    ROOT.gStyle.SetFrameBorderMode(0)
    ROOT.gStyle.SetFrameBorderSize(1)
    ROOT.gStyle.SetFrameFillColor(0)
    ROOT.gStyle.SetFrameFillStyle(0)
    ROOT.gStyle.SetFrameLineColor(1)
    ROOT.gStyle.SetFrameLineStyle(1)
    ROOT.gStyle.SetFrameLineWidth(3)

    #For the histo:
    ROOT.gStyle.SetHistLineColor(ROOT.kBlue)
    ROOT.gStyle.SetHistLineStyle(0)
    ROOT.gStyle.SetHistLineWidth(2)


    ROOT.gStyle.SetEndErrorSize(2)


    ROOT.gStyle.SetMarkerStyle(20)

    #For the fit/function:
    ROOT.gStyle.SetOptFit(1)
    ROOT.gStyle.SetFitFormat("5.4g")
    ROOT.gStyle.SetFuncColor(2)
    ROOT.gStyle.SetFuncStyle(1)
    ROOT.gStyle.SetFuncWidth(1)

    #For the date:
    ROOT.gStyle.SetOptDate(0)


    # For the statistics box:
    ROOT.gStyle.SetOptFile(0)
    ROOT.gStyle.SetOptStat(0) # To display the mean and RMS:   SetOptStat("mr")
    ROOT.gStyle.SetStatColor(ROOT.kWhite)
    ROOT.gStyle.SetStatFont(42)
    ROOT.gStyle.SetStatFontSize(0.025)
    ROOT.gStyle.SetStatTextColor(1)
    ROOT.gStyle.SetStatFormat("6.4g")
    ROOT.gStyle.SetStatBorderSize(1)
    ROOT.gStyle.SetStatH(0.1)
    ROOT.gStyle.SetStatW(0.15)

    # Margins:
    #ROOT.gStyle.SetPadTopMargin(0.05)
    #ROOT.gStyle.SetPadBottomMargin(0.15)
    #ROOT.gStyle.SetPadLeftMargin(0.15)
    #ROOT.gStyle.SetPadRightMargin(0.05)

    # For the Global title:

    ROOT.gStyle.SetOptTitle(0)
    ROOT.gStyle.SetTitleFont(42)
    ROOT.gStyle.SetTitleColor(1)
    ROOT.gStyle.SetTitleTextColor(1)
    ROOT.gStyle.SetTitleFillColor(10)
    ROOT.gStyle.SetTitleFontSize(0.05)


    # For the axis titles:
    
    ROOT.gStyle.SetTitleColor(1, "XYZ")
    ROOT.gStyle.SetTitleFont(42, "XYZ")
    ROOT.gStyle.SetTitleSize(0.06, "XYZ")
    ROOT.gStyle.SetTitleXOffset(1)
    ROOT.gStyle.SetTitleYOffset(1.25)
    

    # For the axis labels:
    
    ROOT.gStyle.SetLabelColor(1, "XYZ")
    ROOT.gStyle.SetLabelFont(42, "XYZ")
    ROOT.gStyle.SetLabelOffset(0.007, "XYZ")
    ROOT.gStyle.SetLabelSize(0.04, "XYZ")
    

    # For the axis:

    ROOT.gStyle.SetAxisColor(1, "XYZ")
    ROOT.gStyle.SetStripDecimals(True)
    ROOT.gStyle.SetTickLength(0.03, "XYZ")
    ROOT.gStyle.SetNdivisions(510, "XYZ")
    ROOT.gStyle.SetPadTickX(1)  # To get tick marks on the opposite side of the frame
    ROOT.gStyle.SetPadTickY(1)
    

    # Change for log plots:
    #ROOT.gStyle.SetOptLogx(0)
    #ROOT.gStyle.SetOptLogy(0)
    #ROOT.gStyle.SetOptLogz(0)

    #Legend options:
    #ROOT.gStyle.SetLegendBorderSize(0)
    #ROOT.gStyle.SetLegendTextSize(0.022)

    # Postscript options:
    #ROOT.gStyle.SetPaperSize(20.,26.)
    #ROOT.gStyle.SetHatchesLineWidth(5)
    #ROOT.gStyle.SetHatchesSpacing(0.05)

def writeSND(pad,
    text_factor=0.9,
    text_offset=0.01,
    extratext=None,
    text_in=True,
    rfrac=0.,
    maintext='SND@LHC',
    drawLogo=True):

    pad.Update()

    l = pad.GetLeftMargin()
    t = pad.GetTopMargin()
    r = pad.GetRightMargin()
    b = pad.GetBottomMargin()

    SNDTextSize = t*text_factor
    SNDTextVerticalOffset = text_offset

    pad.cd()

    latex = ROOT.TLatex()
    latex.SetNDC()
    latex.SetTextAngle(0)
    latex.SetTextColor(ROOT.kBlack)

    latex.SetTextFont(61)
    latex.SetTextAlign(11)
    latex.SetTextSize(SNDTextSize)
    latex.SetText(0,0,maintext)

    sndX = SNDTextSize*2*(1-rfrac)

    if not text_in: latex.DrawLatex(l, 1-t+SNDTextVerticalOffset, maintext)
    else: latex.DrawLatex(l+0.03, 1-t-SNDTextVerticalOffset-1.2*SNDTextSize, maintext)

    extraTextSize = SNDTextSize*0.8
    latex.SetTextFont(52)
    latex.SetTextSize(extraTextSize)
    latex.SetTextAlign(11)
    if not text_in: latex.DrawLatex(l+0.03 + 1.5*sndX, 1-t+SNDTextVerticalOffset, extratext)
    else: latex.DrawLatex(l+0.03, 1-t-SNDTextVerticalOffset-2*SNDTextSize, extratext)

    pad.Update()
    #plegendbox = ([l+0.3,1-t-0.2, 1-r-0.03,1-t-0.03])
    """if drawLogo and text_in:
        padLogo = ROOT.TPad("logo","logo",l+0.03,1-t-0.2-0.03,l+0.03+0.2,1-t-0.03)
        padLogo.SetFillStyle(4000)
        padLogo.SetFillColorAlpha(0, 0)
        padLogo.Draw()
        logo =ROOT.TImage.Open('/Users/danielecentanni/cernbox2/Misc/Cosmetics/Large__SND_Logo_black_cut.png')
        logo.SetConstRatio(True)
        #logo.DrawText(0, 0, 'SND', 98)
        padLogo.cd()
        logo.Draw()"""
    return

def load_hists(histfile, query=None):
    f = ROOT.TFile.Open(histfile)
    histlist = {}
    keylist = f.GetListOfKeys()
    for key in keylist:
        if query is not None and key.GetName() not in query:
            continue
        hist = f.Get(key.GetName())
        # check if histogram is readable
        try:
            hist.SetDirectory(ROOT.gROOT)
        except:
            print('### WARNING ###: key "'+str(key.GetName())+'" does not correspond to valid hist.')
            continue
        hist.SetName(key.GetName())
        histlist[key.GetName()] = hist
    if len(histlist) == 0: raise Exception('ERROR: histlist is empty!')
    f.Close()
    return histlist

def drawSingleHisto(hist, canvas=None, xaxtitle=None, yaxtitle=None, 
            label=None, color=None, logy=False, drawoptions='',
	        extratext=None,topmargin=None, bottommargin=None,
	        leftmargin=None, rightmargin=None,
	        xaxlabelfont=None, xaxlabelsize=None, outpath='', rebin=None, sigma=list(), scale=1., xaxrange=None):

    if not canvas:
        canvas = ROOT.TCanvas("c", "c", 800, 600)

    if color is None: color = ROOT.kAzure-4

    if xaxlabelfont is None: xaxlabelfont = 4 
    if xaxlabelsize is None: xaxlabelsize = 22
    yaxlabelfont = 4; yaxlabelsize = 22
    axtitlefont = 6; axtitlesize = 26
    legendfont = 5
    if leftmargin is None: leftmargin = 0.15
    if rightmargin is None: rightmargin = 0.05
    if topmargin is None: topmargin = 0.05
    if bottommargin is None: bottommargin = 0.15
    canvas.SetBottomMargin(bottommargin)
    canvas.SetLeftMargin(leftmargin)
    canvas.SetRightMargin(rightmargin)
    canvas.SetTopMargin(topmargin)

    pentryheight = 0.2
    plegendbox = ([leftmargin+0.30,1-topmargin-pentryheight-0.01, 1-rightmargin-0.03,1-topmargin-0.03])
    hist.SetLineColor(color)
    hist.SetLineWidth(2)

    if rebin is not None:
        hist.Rebin(int(hist.GetNbinsX()/rebin))

    if scale !=1.:
        hist.Scale(scale)
    
    if label is not None:
        leg = ROOT.TLegend(plegendbox[0],plegendbox[1],plegendbox[2],plegendbox[3])
        leg.SetTextFont(10*legendfont+2)
        leg.SetFillColor(ROOT.kWhite)
        leg.SetBorderSize(0)
        if label=='auto': label = hist.GetTitle()
        leg.AddEntry(hist,label,"l")
        leg.AddEntry(0, 'Entries: {:.2e}'.format(hist.GetEntries()), '')
        leg.AddEntry(0, 'Integral: {:.2e}'.format(hist.Integral()), '')
        leg.AddEntry(0, 'Mean: {:.2e}'.format(hist.GetMean()), '')
        leg.AddEntry(0, 'Std dev: {:.2e}'.format(hist.GetStdDev()), '')
        #leg.AddEntry(0,'#sigma: {:.2e}'.format(sigma[0]), '')
        #leg.AddEntry(0,'#sigma error: {:.2e}'.format(sigma[1]), '')

    xax = hist.GetXaxis()
    #xax.SetNdivisions(5,4,0,ROOT.kTRUE)
    xax.SetLabelFont(10*xaxlabelfont+3)
    xax.SetLabelSize(xaxlabelsize)
    if xaxtitle is not None:
        xax.SetTitle(xaxtitle)
    xax.SetTitleFont(10*axtitlefont+3)
    xax.SetTitleSize(axtitlesize)
    xax.SetTitleOffset(1.2)
    xax.CenterTitle(True)
    if xaxrange:
        xax.SetRangeUser(xaxrange[0], xaxrange[1])
    if not logy:
        hist.SetMaximum(hist.GetMaximum()*1.2)
        hist.SetMinimum(0.)
    else:
        hist.SetMaximum(hist.GetMaximum()*10)
        #hist.SetMinimum(hist.GetMaximum()/1e7)
        canvas.SetLogy()
    yax = hist.GetYaxis()
    yax.SetMaxDigits(3)
    yax.SetNdivisions(8,4,0,ROOT.kTRUE)
    yax.SetLabelFont(10*yaxlabelfont+3)
    yax.SetLabelSize(yaxlabelsize)
    if yaxtitle is not None: 
        yax.SetTitle(yaxtitle)
    yax.SetTitleFont(10*axtitlefont+3)
    yax.SetTitleSize(axtitlesize)
    yax.SetTitleOffset(1.2)
    yax.CenterTitle(True)
    
    hist.Draw(drawoptions)
    ROOT.gPad.RedrawAxis()
    writeSND(canvas, extratext=extratext)
    if label is not None: leg.DrawClone("same")
    ROOT.gPad.Update()
    canvas.Draw()
    canvas.SaveAs(outpath+hist.GetName()+'.pdf', 'pdf')


def drawDATAMC(histlist, c1=None, figname='DATA-MC', xaxtitle=None, yaxtitle=None,
	    normalize=False, lumi=None, dolegend=True, labellist=None, logy=False, extra_text = '', rebin=None, outpath='.', xaxrange=[]):

    if not c1:
        c1 = ROOT.TCanvas()
    
    xaxlabelfont = 4 
    xaxlabelsize = 22
    yaxlabelfont = 4; yaxlabelsize = 22
    axtitlefont = 6; axtitlesize = 26
    legendfont = 5
    leftmargin = 0.15
    rightmargin = 0.05
    topmargin = 0.05
    bottommargin = 0.15
    c1.SetBottomMargin(bottommargin)
    c1.SetLeftMargin(leftmargin)
    c1.SetRightMargin(rightmargin)
    c1.SetTopMargin(topmargin)


    pentryheight = 0.06
    nentries = 1 + len(histlist)
    if nentries>3: pentryheight = pentryheight*0.8
    plegendbox = ([leftmargin+0.45,1-topmargin-pentryheight*nentries, 1-rightmargin-0.03,1-topmargin-0.03])
    
    if rebin is not None:
        for hist in histlist:
            hist.Rebin(int(hist.GetNbinsX()/rebin))

    pairs = list()
    for hist in histlist:
        hist.SetStats(0)
        pairs.append([hist.GetMaximum(), hist])
    maxpair = max(pairs,key=lambda item:item[0])


    if normalize:
        for hist in histlist:
            if hist.Integral() == 0: 
                print(hist.GetName(), 'has null integral, skipping')
                return            
            hist.Scale(1./hist.Integral())
    elif lumi:
        for hist in histlist:
            if hist.Integral() == 0: 
                print(hist.GetName(), 'has null integral, skipping')
                return  
            if not 'DATA' in hist.GetName():
                hist.Scale(lumi)
            else:
                hist.Scale(1.)
    
    if not logy:
        maxpair[1].SetMaximum(maxpair[1].GetMaximum()*1.2)
        maxpair[1].SetMinimum(0.)
        for h in histlist:
            h.SetMaximum(maxpair[1].GetMaximum()*1.2)
    else:
        maxpair[1].SetMaximum(maxpair[1].GetMaximum()*10)
        for h in histlist:
            h.SetMaximum(maxpair[1].GetMaximum()*10)
        c1.SetLogy()
        
    data_index = -1
    for i, h in enumerate(histlist):
        if 'DATA' in h.GetName():
            h.SetMarkerColor(ROOT.kBlack)
            h.SetLineColor(ROOT.kBlack)
            h.SetMarkerStyle(8)
            h.SetMarkerSize(0.5)
            data_index = i
        else:
            h.SetLineWidth(1)
            h.SetFillColor(ROOT.TColor.GetColor("#7d99d1"))
            h.SetLineColor(ROOT.TColor.GetColor('#0000ee'))
            h.SetFillStyle(1001)

    legend = ROOT.TLegend(plegendbox[0],plegendbox[1],plegendbox[2],plegendbox[3])
    legend.SetNColumns(1)
    legend.SetName('legend')
    legend.SetFillColor(ROOT.kWhite)
    legend.SetTextFont(10*legendfont+3)
    legend.SetBorderSize(0)
    for i,hist in enumerate(histlist):
        label = hist.GetTitle()
        if labellist is not None: label = labellist[i]
        else:
            if 'DATA' in hist.GetName():
                if lumi:
                    legend.AddEntry(hist, 'Data L_{int} = '+str(lumi)+' fb^{-1}', "PEL")
                else:
                    legend.AddEntry(hist, 'Data', "PEL")
            else:
                legend.AddEntry(hist, 'Background', "FEL")
        legend.AddEntry(hist, 'Integral: {:.2e}'.format(hist.Integral()), '')
        legend.AddEntry(hist, 'Mean: {:.2e}'.format(hist.GetMean()), '')
    
    for h in histlist:
        xax = h.GetXaxis()
        xax.SetLabelSize(xaxlabelsize)
        xax.SetLabelFont(10*xaxlabelfont+3)
        if xaxtitle is not None:
            xax.SetTitle(xaxtitle)
        xax.SetTitleFont(10*axtitlefont+3)
        xax.SetTitleSize(axtitlesize)
        xax.SetTitleOffset(1.2)
        if xaxrange:
            xax.SetRangeUser(xaxrange[0], xaxrange[1])
        # Y-axis layout
        yax = h.GetYaxis()
        yax.SetMaxDigits(3)
        yax.SetLabelFont(10*yaxlabelfont+3)
        yax.SetLabelSize(yaxlabelsize)
        if yaxtitle is not None:
            yax.SetTitle(yaxtitle)
        yax.SetTitleFont(10*axtitlefont+3)
        yax.SetTitleSize(axtitlesize)
        yax.SetTitleOffset(1.2)
        yax.CenterTitle(True)
        hist.SetMaximum(maxpair[1].GetMaximum()*1.2)

    for i in range(len(histlist)):
        drawopt = ''
        if i!= data_index:
            if histlist[i].GetEntries() < 20: drawopt = 'E'
            histlist[i].Draw("HIST SAME "+drawopt)
    histlist[data_index].Draw("* SAME")
    
    
    ROOT.gPad.RedrawAxis()
    writeSND(c1, extratext=extra_text)
    if dolegend: legend.DrawClone("same")
    ROOT.gPad.Update()
    c1.Draw()
    c1.SaveAs(outpath+figname+'.pdf', 'pdf')

def draw2dHisto(hist, canvas=None,xaxtitle=None, yaxtitle=None, 
            label=None, drawoptions='COLZ',
	        extratext=None,topmargin=None, bottommargin=None,
	        leftmargin=None, rightmargin=None,
	        xaxlabelfont=None, xaxlabelsize=None, outpath=''):

    if not canvas:
        canvas = ROOT.TCanvas()

    if xaxlabelfont is None: xaxlabelfont = 4 
    if xaxlabelsize is None: xaxlabelsize = 22
    yaxlabelfont = 4; yaxlabelsize = 22
    axtitlefont = 6; axtitlesize = 26
    legendfont = 5
    if leftmargin is None: leftmargin = 0.15
    if rightmargin is None: rightmargin = 0.05
    if topmargin is None: topmargin = 0.05
    if bottommargin is None: bottommargin = 0.15
    canvas.SetBottomMargin(bottommargin)
    canvas.SetLeftMargin(leftmargin)
    canvas.SetRightMargin(rightmargin)
    canvas.SetTopMargin(topmargin)

    pentryheight = 0.15
    plegendbox = ([leftmargin+0.45,1-topmargin-pentryheight, 1-rightmargin-0.03,1-topmargin-0.03])
    
    if label is not None:
        hist.SetTitle(label)
    
    hist.SetStats(0)

    xax = hist.GetXaxis()
    #xax.SetNdivisions(5,4,0,ROOT.kTRUE)
    xax.SetLabelFont(10*xaxlabelfont+3)
    xax.SetLabelSize(xaxlabelsize)
    if xaxtitle is not None:
        xax.SetTitle(xaxtitle)
    xax.SetTitleFont(10*axtitlefont+3)
    xax.SetTitleSize(axtitlesize)
    xax.SetTitleOffset(1.2)

    yax = hist.GetYaxis()
    yax.SetMaxDigits(3)
    yax.SetNdivisions(8,4,0,ROOT.kTRUE)
    yax.SetLabelFont(10*yaxlabelfont+3)
    yax.SetLabelSize(yaxlabelsize)

    if yaxtitle is not None: 
        yax.SetTitle(yaxtitle)
    yax.SetTitleFont(10*axtitlefont+3)
    yax.SetTitleSize(axtitlesize)
    yax.SetTitleOffset(1.2)
    
    hist.Draw(drawoptions)
    ROOT.gPad.RedrawAxis()
    writeSND(canvas, extratext=extratext, text_in=False)
    ROOT.gPad.Update()
    canvas.Draw()
    canvas.SaveAs(outpath+hist.GetName()+'.pdf', 'pdf')

def drawMultiHisto(histlist, c1=None, figname='multihisto', xaxtitle=None, yaxtitle=None,
	    normalize=False, dolegend=True, labellist=None, 
	    colorlist=None, logy=False, drawoptions='', extra_text = '', rebin=None, outpath='.', scale=1., xaxrange=None):

    if not c1: c1 = ROOT.TCanvas("c", "c", 800, 600)

    if colorlist is None:
        colorlist = ([ROOT.kAzure-4, ROOT.kRed, ROOT.kGreen+1, ROOT.kViolet, ROOT.kMagenta-9,
                        ROOT.kTeal-6, ROOT.kAzure+6, ROOT.kOrange, ROOT.kGreen-1])
    if( len(histlist)>len(colorlist) ):
        raise Exception('ERROR: histogram list is longer than color list')
    if(labellist is not None and len(labellist)!=len(histlist)):
        raise Exception('ERROR: length of label list does not agree with histogram list')
    
    xaxlabelfont = 4 
    xaxlabelsize = 22
    yaxlabelfont = 4; yaxlabelsize = 22
    axtitlefont = 6; axtitlesize = 26
    legendfont = 5
    leftmargin = 0.15
    rightmargin = 0.05
    topmargin = 0.05
    bottommargin = 0.15
    c1.SetBottomMargin(bottommargin)
    c1.SetLeftMargin(leftmargin)
    c1.SetRightMargin(rightmargin)
    c1.SetTopMargin(topmargin)

    pentryheight = 0.08
    nentries = 1 + len(histlist)
    if nentries>3: pentryheight = pentryheight*0.8
    plegendbox = ([leftmargin+0.30,1-topmargin-pentryheight*nentries, 1-rightmargin-0.03,1-topmargin-0.03])
    
    if rebin is not None:
        for hist in histlist:
            hist.Rebin(int(hist.GetNbinsX()/rebin))
    
    if scale !=1.:
        for hist in histlist: hist.Scale(scale)

    pairs = list()
    for hist in histlist:
        hist.SetStats(0)
        pairs.append([hist.GetMaximum(), hist])
    maxpair = max(pairs,key=lambda item:item[0])


    if normalize:
        for hist in histlist:
            hist.Scale(1./hist.Integral())
    
    if not logy:
        maxpair[1].SetMaximum(maxpair[1].GetMaximum()*1.2)
        maxpair[1].SetMinimum(0.)
        for h in histlist:
            h.SetMaximum(maxpair[1].GetMaximum()*1.2)
    else:
        maxpair[1].SetMaximum(maxpair[1].GetMaximum()*10)
        for h in histlist:
            h.SetMaximum(maxpair[1].GetMaximum()*10)
        c1.SetLogy()
    
    for i,hist in enumerate(histlist):
        hist.SetLineWidth(2)
        hist.SetLineColor(colorlist[i])
        hist.SetMarkerSize(0)

    legend = ROOT.TLegend(plegendbox[0],plegendbox[1],plegendbox[2],plegendbox[3])
    legend.SetNColumns(1)
    legend.SetName('legend')
    legend.SetFillColor(ROOT.kWhite)
    legend.SetTextFont(10*legendfont+3)
    legend.SetBorderSize(0)
    for i,hist in enumerate(histlist):
        label = hist.GetName()
        if labellist is not None: label = labellist[i]
        legend.AddEntry(hist,label,"FL")
        legend.AddEntry(hist, 'Integral: {:.2e}'.format(hist.Integral()), '')
        legend.AddEntry(hist, 'Mean: {:.2e}'.format(hist.GetMean()), '')
    

    for h in histlist: 
        xax = h.GetXaxis()
        xax.SetLabelSize(xaxlabelsize)
        xax.SetLabelFont(10*xaxlabelfont+3)
        if xaxtitle is not None:
            xax.SetTitle(xaxtitle)
        elif 'Momentum' in h.GetTitle():
            xax.SetTitle('Momentum [GeV/c]')
        elif 'Energy' in h.GetTitle():
            xax.SetTitle('Energy [GeV]')
        xax.SetTitleFont(10*axtitlefont+3)
        xax.SetTitleSize(axtitlesize)
        xax.SetTitleOffset(1.2)
        xax.CenterTitle(True)
        if xaxrange:
            xax.SetRangeUser(xaxrange[0], xaxrange[1])
        # Y-axis layout
        yax = h.GetYaxis()
        yax.SetMaxDigits(3)
        yax.SetLabelFont(10*yaxlabelfont+3)
        yax.SetLabelSize(yaxlabelsize)
        if yaxtitle:
            yax.SetTitle(yaxtitle)
        elif 'Momentum' in h.GetTitle() and not yaxtitle:
            yax.SetTitle('dN/dpdt [(GeV/c)^{-1}s^{-1}]')
        elif 'Energy' in h.GetTitle() and not yaxtitle:
            yax.SetTitle('dN/dEdt [GeV^{-1}s^{-1}]')
        yax.SetTitleFont(10*axtitlefont+3)
        yax.SetTitleSize(axtitlesize)
        yax.SetTitleOffset(1.2)
        yax.CenterTitle(True)
        hist.SetMaximum(maxpair[1].GetMaximum())

    histlist[0].Draw(drawoptions)
    for hist in histlist[1:]:
        hist.Draw('same '+drawoptions)
    
    ROOT.gPad.RedrawAxis()
    writeSND(c1, extratext=extra_text)
    if dolegend: legend.DrawClone("same")
    ROOT.gPad.Update()
    c1.Draw()
    c1.SaveAs(outpath+figname+'.pdf', 'pdf')
    

parser = ArgumentParser()
parser.add_argument("-f", "--inputFile", dest="inputFile", help="single input file", required=False)
parser.add_argument("-c", "--inputCanvas", dest="inputCanvas", help="single input canvas", required=False)
parser.add_argument("-e", "--extratext", dest="extratext", help="extratext written below SND@LHC", default=None, required=False)
parser.add_argument('-hname', nargs='+', dest="hname", help='List of histos to be drawn', required=False)
parser.add_argument("--scale", dest="scalefactor", help="scale factor", required=False, type=float, default=1.)
parser.add_argument("--auto", dest="auto", action='store_true', help='Enables automatic mode',required=False, default=False)
#parser.add_argument("--divide", dest="divide", action='store_true', required=False, default=False)
parser.add_argument("--dataMC", dest="dataMC", help='Enables dataMC comparison mode: data histogram must contain DATA in its name', action='store_true', required=False, default=False)
options = parser.parse_args()

if options.inputFile:
    tmp = options.inputFile.split('.')
    outpath = 'plots_'+tmp[0]+'/'
    if not os.path.exists(outpath):
            os.makedirs(outpath)
    if options.hname and len(options.hname)> 1:
        Hlist = load_hists(options.inputFile, query=options.hname)
    else:
        Hlist = load_hists(options.inputFile)

canvases    = {}
extratext=''
if options.extratext:
    extratext=options.extratext

if options.inputFile:
    init_style()
    if not options.hname and options.auto:
        for i_h,h in enumerate(Hlist.values()):
            if i_h not in canvases.keys():
                canvases[i_h] = ROOT.TCanvas("c"+str(i_h), "c"+str(i_h), 800, 600)
            htype = h.IsA().GetName()
            if 'TH1' in htype:
                drawSingleHisto(h, canvases[i_h], drawoptions='HIST', extratext=extratext, logy=True, outpath=outpath)
            elif 'TH2' in htype:
                draw2dHisto(h, canvases[i_h], extratext=extratext, outpath=outpath)
    elif options.auto and len(options.hname) < 2:
        i_h = 0
        options.hname = options.hname[0]
        canvases[i_h] = ROOT.TCanvas("c"+str(i_h), "c"+str(i_h), 800, 800)
        htype = Hlist[options.hname].IsA().GetName()
        sel_hist = Hlist[options.hname]
        if 'TH1' in htype:
            drawSingleHisto(Hlist[options.hname], canvases[i_h], drawoptions='HIST', extratext=extratext, logy=True, outpath=outpath, scale=options.scalefactor, label=sel_hist.GetTitle(), xaxtitle=sel_hist.GetXaxis().GetTitle(), yaxtitle=sel_hist.GetYaxis().GetTitle()) #,xaxrange[])
        elif 'TH2' in htype:
            draw2dHisto(Hlist[options.hname], canvases[i_h], extratext=extratext, outpath=outpath)
    elif options.auto and len(options.hname)>1:
        i_h = 0
        canvases[i_h] = ROOT.TCanvas("c"+str(i_h), "c"+str(i_h), 800, 800)
        if options.dataMC:
            drawDATAMC(list(Hlist.values()), canvases[i_h], xaxtitle=list(Hlist.values())[0].GetXaxis().GetTitle(), yaxtitle=list(Hlist.values())[0].GetYaxis().GetTitle(), normalize=True, extra_text='DATA-MC Comparison')
        else:
            drawMultiHisto(list(Hlist.values()), canvases[i_h], logy=True, drawoptions='HIST', extra_text=extratext, outpath=outpath, scale=options.scalefactor, yaxtitle=list(Hlist.values())[0].GetYaxis().GetTitle(), xaxtitle=list(Hlist.values())[0].GetXaxis().GetTitle())

elif options.inputCanvas:
    f = ROOT.TFile.Open(options.inputCanvas)
    keylist = f.GetListOfKeys()
    clist = list()
    for key in keylist:
        canvas = f.Get(key.GetName())
        canvas.SetName(key.GetName())
        clist.append(canvas)
    #f.Close()
    histlist = list()
    legendlist = list()
    for c in clist:
        _list = c.GetListOfPrimitives()
        for l in _list:
            #print(l.IsA().GetName())
            if 'TH1' in l.IsA().GetName():
                histlist.append(l)
            elif 'TLegend' in l.IsA().GetName():
                legendlist.append(l)
    init_style()
    if len(histlist)==1:
        canvases[0] = ROOT.TCanvas("c"+str(0), "c"+str(0), 800, 600)
        h = histlist[0]
        drawSingleHisto(h, canvases[0], drawoptions=h.GetDrawOption(), extratext=extratext, logy=True, outpath='')
    elif len(histlist)== 2:
        #for p in legendlist[0].GetListOfPrimitives():
        #    print(p.GetLabel())
        canvases[0] = ROOT.TCanvas("c"+str(0), "c"+str(0), 800, 600)
        #drawDATAMC(histlist=histlist, c1=canvases[0], xaxtitle='US QDC', yaxtitle='a.u.', 
        #           dolegend=True, labellist=['Data: 39 fb^{-1}', 'MonteCarlo shifted'], figname='USQDCcomparison', rebin=110)
        drawDATAMC(histlist=histlist, c1=canvases[0], xaxtitle='N SciFi hits', yaxtitle='a.u.', 
                   dolegend=True, labellist=['Data: 39 fb^{-1}', 'MonteCarlo'], figname='Nsfhits', logy=True, extra_text=extratext)
            


# edit the last part in order to take and sort all of the items present in the .root file (frame, th1, tlegend, tpavetext...)