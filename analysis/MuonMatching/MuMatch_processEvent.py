import os
import sys
import time
from array import array
from datetime import date
import numpy as np


import ROOT

#ROOT.gROOT.SetBatch(True)

today = date.today().strftime('%d%m%y')

geofiles    = {'DATA': '/afs/cern.ch/work/d/dannc/public/MuonMatching/files/geofile_sndlhc_TI18_2022_NagoyaEmu.root',
               '2023': '/eos/experiment/sndlhc/convertedData/physics/2023/geofile_sndlhc_TI18_V3_2023.root'}

xaxlabelfont = 4 
xaxlabelsize = 15
yaxlabelfont = 4; yaxlabelsize = 15
axtitlefont = 6; axtitlesize = 18
legendfont = 5
leftmargin = 0.15
rightmargin = 0.05
topmargin = 0.05
bottommargin = 0.15

def bookHist(h,key=None,title='',nbinsx=100,xmin=0,xmax=1,nbinsy=0,ymin=0,ymax=1,nbinsz=0,zmin=0,zmax=1):
  if key==None : 
    print('missing key')
    return
  rkey = str(key) # in case somebody wants to use integers, or floats as keys 
  if key in h:    h[key].Reset()  
  elif nbinsz >0:       h[key] = ROOT.TH3D(rkey,title,nbinsx,xmin,xmax,nbinsy,ymin,ymax,nbinsz,zmin,zmax) 
  elif nbinsy >0:       h[key] = ROOT.TH2D(rkey,title,nbinsx,xmin,xmax,nbinsy,ymin,ymax) 
  else:                 h[key] = ROOT.TH1D(rkey,title,nbinsx,xmin,xmax)
  h[key].SetDirectory(ROOT.gROOT)

def getOriginAndDims(nodepath):
    nav = ROOT.gGeoManager.GetCurrentNavigator()
    nav.cd(nodepath)
    O = {'X':0, 'Y':0, 'Z':0}
    D = {'X':0, 'Y':0, 'Z':0}
    N = nav.GetCurrentNode()
    S = N.GetVolume().GetShape()
    D['X'], D['Y'], D['Z'] = S.GetDX(),S.GetDY(),S.GetDZ()
    O['X'], O['Y'], O['Z'] = S.GetOrigin()[0],S.GetOrigin()[1],S.GetOrigin()[2]
    OriginArray = array('d', O.values())
    OriginTrans = array('d', [0, 0, 0])
    nav.LocalToMaster(OriginArray, OriginTrans)
    O['X'], O['Y'], O['Z'] = OriginTrans[0],OriginTrans[1],OriginTrans[2]
    return O, D

def GetTrackPos(trackfile, trid):
    import fedrarootlogon
    import Fedra2sndsw as EmuConv
    dproc = ROOT.EdbDataProc()
    gAli = dproc.PVR()
    scancond = ROOT.EdbScanCond()
    scancond.SetSigma0(0.5, 0.5, 0.0015, 0.0015) #change sigma0
    scancond.SetDegrad(4) #change angular degradation
    gAli.SetScanCond(scancond)
    dproc.ReadTracksTree(gAli, trackfile, "trid=={}".format(trid))
    track = gAli.eTracks[0]
    globaltrackarr = EmuConv.converttrack(track, brickID=21, refplate=57) # careful here there are more than one array (segments)
    for x,y,z,tx,ty,tz in globaltrackarr:
        track_conv_pos = ROOT.TVector3(x, y, z)
        track_conv_angles = ROOT.TVector3(tx,ty,tz)
    return track_conv_pos, track_conv_angles

def ScifiAvgPos(event, scifiDet, scifiplane, area_dim, track_conv_pos):
    avg_sf_x, avg_sf_y = getWAvgScifiPos(event, scifiDet)
    ret = False
    value = avg_sf_x[scifiplane]
    if ROOT.TMath.Abs(avg_sf_x[scifiplane]-track_conv_pos.X())< area_dim/2. and ROOT.TMath.Abs(avg_sf_y[scifiplane]-track_conv_pos.Y()) < area_dim/2.:
        ret = True
    else: return False, 0
    return ret, value

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
    ROOT.gStyle.SetTitleSize(0.04, "XYZ")
    ROOT.gStyle.SetTitleXOffset(0.8)
    ROOT.gStyle.SetTitleYOffset(1.2)
    

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

def Pos2Wall(muVtxZ, ievent):
    dz = 11.95
    WallStartpoints = {1: 289.374023, 2: 302.383125, 3: 315.372394, 4: 328.371518, 5: 341.370641}
    Wall = None
    for i, start in WallStartpoints.items():
        if i < 5:
            if muVtxZ < start + WallStartpoints[i+1]-WallStartpoints[i]  and muVtxZ > start: Wall = i-1
        else:
            if muVtxZ < start+dz and muVtxZ > start: Wall = i-1
    if Wall is None: print('Ev ', ievent, ', Wall not found! Z= ', muVtxZ)
    return Wall

def doLegend(hist1, hist2):
    pentryheight = 0.04
    nentries = 2
    legendfont = 5
    p1topmargin = 0.07 
    p1bottommargin = 0.15
    leftmargin = 0.30
    rightmargin = 0.07
    plegendbox = ([leftmargin+0.3,1-p1topmargin-0.03-pentryheight*nentries,
                    1-rightmargin-0.03,1-p1topmargin-0.03])
    legend = ROOT.TLegend(plegendbox[0],plegendbox[1],plegendbox[2],plegendbox[3])
    legend.SetNColumns(1)
    legend.SetFillColor(ROOT.kWhite)
    legend.SetTextFont(10*legendfont+3)
    #legend.SetBorderSize(0)
    label1 = hist1.GetName()
    label2 = hist2.GetName()
    legend.AddEntry(hist1,label1,"p")
    legend.AddEntry(hist2,label2,"p")
    legend.DrawClone('SAME')

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

def createCanvas(noPlots):
    fact = 1.5
    if noPlots == 1:
        xPad = 1; yPad = 1; width = fact*550; height = fact*0.90*width
    elif noPlots == 2:
        xPad = 2; yPad = 1; width = fact*600; height = fact*0.50*width
    elif noPlots == 3:
        xPad = 3; yPad = 1; width = fact*900; height = fact*0.4*width
    elif noPlots == 4:
        xPad = 2; yPad = 2; width = fact*600; height = fact*width
    else:
        xPad = 3; yPad = 2; width = 800; height = 0.55*width
    noPadPerCanv = xPad * yPad
    nCanvases = int(noPlots/6)+1
    canvs = {}
    for i in range(nCanvases):
        #canvs['canv'+str(i)] = ROOT.TCanvas("canv"+str(i), "Variables", int(width), int(height))
        canvs['canv'+str(i)] = ROOT.TCanvas("canv"+str(i), "Variables", 1200, int(0.55*1200))
        if not noPlots == 1: canvs['canv'+str(i)].Divide(xPad, yPad)
    #canv = ROOT.TCanvas("canv", "Variables", int(width), int(height))
    #canv = ROOT.TCanvas("canv", "Variables", 1200, int(0.55*1200))
    return canvs

def drawDATAMC(histlist, c1=None, xaxtitle=None, yaxtitle=None,
	    normalize=False, lumi=None, dolegend=True, labellist=None, logy=False, extra_text = '', rebin=None, xaxrange = [], yaxrange = []):
    
    xaxlabelfont = 4 
    xaxlabelsize = 15
    yaxlabelfont = 4; yaxlabelsize = 15
    axtitlefont = 6; axtitlesize = 18
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
    
    pairs = list()
    for hist in histlist:
        hist.SetStats(0)
        pairs.append([hist.GetMaximum(), hist])
    maxpair = max(pairs,key=lambda item:item[0])
    
    if not logy:
        maxpair[1].SetMaximum(maxpair[1].GetMaximum()*1.2)
        maxpair[1].SetMinimum(0.)
    else:
        maxpair[1].SetMaximum(maxpair[1].GetMaximum()*10)
        for h in histlist:
            h.SetMaximum(maxpair[1].GetMaximum()*10)
        c1.SetLogy()
        
    data_index = -1
    for i, h in enumerate(histlist):
        h.SetTitle('')
        if 'DATA' in h.GetName():
            if len(histlist) == 1:
                h.SetFillColor(ROOT.kAzure-4)
            h.SetMarkerColor(ROOT.kBlack)
            h.SetLineColor(ROOT.kBlack)
            h.SetMarkerStyle(8)
            h.SetMarkerSize(0.5)
            data_index = i
        elif 'PMU' in h.GetName() or 'background' in h.GetName():
            h.SetLineWidth(1)
            h.SetFillColor(ROOT.TColor.GetColor("#ff0000"))
            h.SetLineColor(ROOT.TColor.GetColor('#ff0000'))
            h.SetFillStyle(3554)
        else:
            h.SetLineWidth(1)
            h.SetFillColorAlpha(ROOT.TColor.GetColor("#7d99d1"), 0.5)
            h.SetLineColor(ROOT.TColor.GetColor('#0000ee'))
            h.SetFillStyle(1001)
            #h.Scale(lumi)
        

    legend = ROOT.TLegend(plegendbox[0],plegendbox[1],plegendbox[2],plegendbox[3])
    #legend = ROOT.TLegend()
    legend.SetNColumns(1)
    legend.SetName('legend')
    legend.SetFillColor(ROOT.kWhite)
    legend.SetTextFont(10*legendfont+3)
    legend.SetBorderSize(0)
    for i,h in enumerate(histlist):
        if 'DATA' in h.GetName():
            if lumi:
                legend.AddEntry(h, 'Data L_{int} = '+str(lumi)+' fb^{-1}', "PEL")
            else:
                legend.AddEntry(h, 'Data', "PEL")
        elif 'PMU' in h.GetName():
            legend.AddEntry(h, 'Background (PMU)', "FEL")
        else:
            legend.AddEntry(h, 'Signal (DIS)', "FEL")
        
    
    for h in histlist:
        xax = h.GetXaxis()
        xax.SetLabelSize(xaxlabelsize)
        xax.SetLabelFont(10*xaxlabelfont+3)
        if xaxtitle is not None:
            xax.SetTitle(xaxtitle)
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
        if yaxtitle is not None:
            yax.SetTitle(yaxtitle)
        yax.SetTitleFont(10*axtitlefont+3)
        yax.SetTitleSize(axtitlesize)
        yax.SetTitleOffset(1.5)
        yax.CenterTitle(True)
        h.SetMaximum(maxpair[1].GetMaximum()*1.2)
        if yaxrange:
            yax.SetRangeUser(yaxrange[0], yaxrange[1])
    
    
    for i in range(len(histlist)):
        drawopt = ''
        if i!= data_index:
            if histlist[i].GetEntries() < 20: drawopt = 'E'
            histlist[i].Draw("HIST SAME "+drawopt)
    if len(histlist)==1:
        histlist[data_index].Draw("HIST")
    else:
        histlist[data_index].Draw("* SAME")

    
    ROOT.gPad.RedrawAxis()
    writeSND(c1, extratext=extra_text)
    if dolegend: legend.DrawClone("same")
    ROOT.gPad.Update()
    c1.Draw()

def GetBar(detID):
    plane = int((detID/1000)%10)
    bar = int((detID%10000)%1000)
    return plane, bar

def getAvgScifiPos(event, scifiDet):
    n_sf_hits_x ={1:0, 2:0, 3:0, 4:0, 5:0}
    n_sf_hits_y ={1:0, 2:0, 3:0, 4:0, 5:0}
    avg_sf_x = {1:0, 2:0, 3:0, 4:0, 5:0}
    avg_sf_y = {1:0, 2:0, 3:0, 4:0, 5:0}
    a, b = ROOT.TVector3(), ROOT.TVector3()
    for aHit in event.Digi_ScifiHits:
        if not aHit.isValid(): continue
        plane = aHit.GetStation()
        detID = aHit.GetDetectorID()
        scifiDet.GetSiPMPosition(detID, a, b)
        if aHit.isVertical():
            n_sf_hits_x[plane]+=1
            avg_sf_x[plane]+= (a.X() + b.X())/2.
        else:
            n_sf_hits_y[plane]+=1
            avg_sf_y[plane]+= (a.Y() + b.Y())/2.
    for iplane in range(1, 5):
        if n_sf_hits_x[iplane]:
            avg_sf_x[iplane]/=n_sf_hits_x[iplane]
        if n_sf_hits_y[iplane]:
            avg_sf_y[iplane]/=n_sf_hits_y[iplane]
    return avg_sf_x, avg_sf_y

def getHitQDC(digi):
    ns = max(1, digi.GetnSides())
    HitQDC = 0
    for side in range(ns):
        for m in range(digi.GetnSiPMs()):
            qdc = digi.GetSignal(m+side*digi.GetnSiPMs())
            if not qdc < 0 :
                HitQDC += qdc
    return HitQDC

def getWAvgScifiPos(event, scifiDet):
    n_sf_hits_x ={1:0, 2:0, 3:0, 4:0, 5:0}
    n_sf_hits_y ={1:0, 2:0, 3:0, 4:0, 5:0}
    avg_sf_x = {1:0, 2:0, 3:0, 4:0, 5:0}
    avg_sf_y = {1:0, 2:0, 3:0, 4:0, 5:0}
    qdc_hits_x = {1:0, 2:0, 3:0, 4:0, 5:0}
    qdc_hits_y = {1:0, 2:0, 3:0, 4:0, 5:0}
    a, b = ROOT.TVector3(), ROOT.TVector3()
    for aHit in event.Digi_ScifiHits:
        if not aHit.isValid(): continue
        plane = aHit.GetStation()
        detID = aHit.GetDetectorID()
        scifiDet.GetSiPMPosition(detID, a, b)
        HitQDC = getHitQDC(aHit)
        if not HitQDC: continue
        if aHit.isVertical():
            n_sf_hits_x[plane]+=1
            qdc_hits_x[plane]+=HitQDC
            avg_sf_x[plane]+= HitQDC*(a.X() + b.X())/2.
        else:
            n_sf_hits_y[plane]+=1
            qdc_hits_y[plane]+=HitQDC
            avg_sf_y[plane]+= HitQDC*(a.Y() + b.Y())/2.
    for iplane in range(1, 5):
        if n_sf_hits_x[iplane]:
            avg_sf_x[iplane]/=qdc_hits_x[iplane]
        if n_sf_hits_y[iplane]:
            avg_sf_y[iplane]/=qdc_hits_y[iplane]
    return avg_sf_x, avg_sf_y

def GetAvgScifiPos(DigiScifiHits):
    n_sf_hits_x = [0]*5
    n_sf_hits_y = [0]*5
    avg_sf_x = [0.]*5
    avg_sf_y = [0.]*5
    a, b = ROOT.TVector3(), ROOT.TVector3()
    for hit in  DigiScifiHits :
        if not hit.isValid() :
            continue
        plane = hit.GetStation() - 1
        if hit.isVertical() :
            n_sf_hits_x[plane] += 1
            avg_sf_x[plane] += (a.X() + b.X())/2.
        else :
            n_sf_hits_y[plane] += 1
            avg_sf_y[plane] += (a.Y() + b.Y())/2.
    for i_plane in range(5) :
        if n_sf_hits_x[i_plane] :
            avg_sf_x[i_plane] /= n_sf_hits_x[i_plane]
        if n_sf_hits_y[i_plane] :
            avg_sf_y[i_plane] /= n_sf_hits_y[i_plane]
    return avg_sf_x, avg_sf_y


TDC2ns = 1E9/160.316E6
def CorrectScifi(event, scifiDet):
  import rootUtils as ut
  nsf_statID = {1:0, 2:0, 3:0, 4:0, 5:0}
  nsf_statID_corr = {1:0, 2:0, 3:0, 4:0, 5:0}
  time_plane = {1:0, 2:0, 3:0, 4:0, 5:0}
  Nsf = 0
  Nsf_corr = 0
  hist = {}
  a, b = ROOT.TVector3(), ROOT.TVector3()
  avg_sf_x, avg_sf_y = GetAvgScifiPos(event.Digi_ScifiHits)
  for st in range(1, 6):
    ut.bookHist(hist, 'ScifiHitTime_'+str(st), "Scifihittime corrected station "+str(st), 20, 0, 50)
  for aHit in event.Digi_ScifiHits:
    if not aHit.isValid(): continue
    scifiDet.GetSiPMPosition(aHit.GetDetectorID(), a, b)
    station = aHit.GetStation()
    if aHit.isVertical() :
        L = b.Y() - avg_sf_y[station-1]      
    else :
        L = avg_sf_x[station-1] - a.X()
    Nsf+=1
    nsf_statID[station]+=1
    time_plane[station] = aHit.GetTime()*TDC2ns
    time_plane[station] = scifiDet.GetCorrectedTime(aHit.GetDetectorID(), time_plane[station], L)
    hist['ScifiHitTime_'+str(station)].Fill(time_plane[station])
  for station, sfhit in nsf_statID.items():
    ibin = hist['ScifiHitTime_'+str(station)].GetMaximumBin()
    if sfhit > 40:
      Nsf_corr+= hist['ScifiHitTime_'+str(station)].Integral(ibin, ibin+2)
      nsf_statID_corr[station] = hist['ScifiHitTime_'+str(station)].Integral(ibin, ibin+2)
    else:
      Nsf_corr+=sfhit
      nsf_statID_corr[station] = sfhit
  del hist
  return Nsf_corr, Nsf, nsf_statID_corr

def getTimeCorrectedRange(event, scifiDet):
    import rootUtils as ut
    rangePerStation = {1:[], 2:[], 3:[], 4:0, 5:[]}
    avg_sf_x, avg_sf_y = getAvgScifiPos(event, scifiDet)
    hist = {}
    for iplane in range(1, 6):
        a, b = ROOT.TVector3(), ROOT.TVector3()
        ut.bookHist(hist, 'ScifiHitTime_'+str(iplane), "Scifihittime corrected station "+str(iplane), 20, 0, 50)
        for aHit in event.Digi_ScifiHits:
            if not aHit.isValid(): continue
            if not aHit.GetStation()==iplane: continue
            scifiDet.GetSiPMPosition(aHit.GetDetectorID(), a, b)
            L = None
            if aHit.isVertical(): L = b.Y()-avg_sf_y[iplane]
            else: L = avg_sf_x[iplane]-a.X()
            hit_time = scifiDet.GetCorrectedTime(aHit.GetDetectorID(), aHit.GetTime()*TDC2ns, L)
            hist['ScifiHitTime_'+str(iplane)].Fill(hit_time)
        ibin = -1
        ibin = hist['ScifiHitTime_'+str(iplane)].GetMaximumBin()
        rangePerStation[iplane] = [hist['ScifiHitTime_'+str(iplane)].GetBinLowEdge(ibin),  hist['ScifiHitTime_'+str(iplane)].GetBinLowEdge(ibin+3)]
    return rangePerStation

def isInTimeRange(hit_time, time_low, time_up):
    if hit_time > time_low and hit_time <= time_up: return True
    else: return False

def scifiCluster(DigiScifiBranch, scifiDet):
    clusters = []
    hitDict = {}
    clusScifi   = ROOT.TObjArray(100)
    for k in range(DigiScifiBranch.GetEntries()):
        d = DigiScifiBranch[k]
        if not d.isValid(): continue 
        hitDict[d.GetDetectorID()] = k
    hitList = list(hitDict.keys())
    if len(hitList)>0:
            hitList.sort()
            tmp = [ hitList[0] ]
            cprev = hitList[0]
            ncl = 0
            last = len(hitList)-1
            hitvector = ROOT.std.vector("sndScifiHit*")()
            for i in range(len(hitList)):
                if i==0 and len(hitList)>1: continue
                c=hitList[i]
                neighbour = False
                if (c-cprev)==1:    # does not account for neighbours across sipms
                    neighbour = True
                    tmp.append(c)
                if not neighbour  or c==hitList[last]:
                    first = tmp[0]
                    N = len(tmp)
                    hitvector.clear()
                    for aHit in tmp: hitvector.push_back( DigiScifiBranch[hitDict[aHit]])
                    aCluster = ROOT.sndCluster(first,N,hitvector,scifiDet,False)
                    clusters.append(aCluster)
                    if c!=hitList[last]:
                            ncl+=1
                            tmp = [c]
                    elif not neighbour :   # save last channel
                        hitvector.clear()
                        hitvector.push_back( DigiScifiBranch[hitDict[c]])
                        aCluster = ROOT.sndCluster(c,1,hitvector,scifiDet,False)
                        clusters.append(aCluster)
                cprev = c
    clusScifi.Delete()            
    for c in clusters:  
        clusScifi.Add(c)
    return clusScifi

def GetP(px, py, pz):
    return ROOT.TMath.Sqrt(px*px+py*py+pz*pz)
def GetPlane(fDetectorID):
    return int(fDetectorID/1000)%10
def GetSystem(fDetectorID):
    return ROOT.TMath.Floor(fDetectorID/10000)

def getScifiHitDensity(hitcoll, width=1.):
    if len(hitcoll) == 0: return 0
    weights = []
    for i in hitcoll:
        neighbour_no_of_hits = 0
        for j in hitcoll:
            if i == j: continue
            if ROOT.TMath.Abs(i-j) <= width: neighbour_no_of_hits += 1
        weights.append(neighbour_no_of_hits)
    sum_weights = sum(weights)
    if sum_weights: return sum_weights
    else: return 0

def getCorrUShits(digiBranch, hit2MC, pointBranch, thresh=2.8e-3/2.):
    Nus = 0
    nus_statID = {1:0, 2:0, 3:0, 4:0, 5:0}
    for aHit in digiBranch:
        detID = aHit.GetDetectorID()
        plane = aHit.GetPlane()+1
        if not aHit.isValid(): continue
        if not aHit.GetSystem() == 2: continue
        tot_eloss = 0
        for mc_point_i, _ in hit2MC.wList(detID):
            tot_eloss = tot_eloss + pointBranch[mc_point_i].GetEnergyLoss() #GeV
        if tot_eloss < thresh: continue
        Nus+=1
        nus_statID[plane]+=1
    return Nus, nus_statID


from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument("-f", nargs='+', dest="inputFiles", help="input files", required=False)
parser.add_argument("-o", dest="outdir", help="output dir", required=False, default='./')
parser.add_argument("--prepare", dest="prepare", required=False, default=False, action='store_true')
parser.add_argument("--process", dest="process", required=False, default=False, action='store_true')
parser.add_argument("--merge", dest="merge", required=False, default=False, action='store_true')
parser.add_argument("--compare", dest="compare", required=False, default=False, action='store_true')
parser.add_argument("--lumi", dest="lumi", type=float, required=False, default=None)
parser.add_argument("--norm", dest="norm", required=False, default=False, action='store_true')
parser.add_argument("--procID", dest="procID", required=False, default=None, type=int)
parser.add_argument("--trid", nargs='+', dest="trid", required=False, default=None, type=int)
parser.add_argument("-t", dest="trackFile", help="track file", required=False)
parser.add_argument("--auto", dest="auto", required=False, default=False, action='store_true')
parser.add_argument("--sfplane", dest="sfplane", required=False, default=2, type=int)
args = parser.parse_args()

outdir = args.outdir

if args.trid and len(args.trid) < 2:
    args.trid = args.trid[0]

def mergeDATA_MC():
    import rootUtils as ut
    files       = {}
    for f in args.inputFiles:
        if 'PMU' in f:
            files['PMU'] = f
        elif 'DATA' in f:
            files['DATA'] = f
        else:
            files['DISMC'] = f
    foutName = 'DATA_varhistos_from_processeddata.root'
    fout = ROOT.TFile.Open(args.outdir+foutName, "RECREATE")
    h = {}
    for key, f in files.items():
        print("Reading file: ", f, "key is ", key)
        ut.bookHist(h, key+"_Nscifi", "Nhits Scifi;N ", 300, 0, 3000)
        for n in range(1, 6):
            ut.bookHist(h, key+"_Nscifi"+str(n), "Nhits Scifi, station "+str(n)+";N ", 300, 0, 3000)
        ut.bookHist(h, key+"_Nscifi_plane", "Nhits Scifi per plane;N ", 300, 0, 3000)
        for n in range(1, 6):
            ut.bookHist(h, key+"_Nscificlus"+str(n), "Ncluster Scifi, station "+str(n)+";N ", 201, -0.5, 200.5)

        for n in range(1, 6):
            ut.bookHist(h, key+"_ScifiFrac"+str(n), "Scifi hit fraction in station "+str(n)+";N ", 200, 0, 1.)
            ut.bookHist(h, key+"_ScifiHitDensityX"+str(n), "Scifi X hit density in station "+str(n)+";N ", 250, 0, 25000)
            ut.bookHist(h, key+"_ScifiHitDensityY"+str(n), "Scifi Y hit density in station "+str(n)+";N ", 250, 0, 25000)

        ut.bookHist(h, key+"_ScifiFrac3_4_5", "Scifi hit fraction for SF3-4-5;N ", 200, 0, 1.)

        for n in range(1, 6):
            ut.bookHist(h, key+"_ScifiHitDensity_Mean"+str(n), "Mean Scifi hit density in station "+str(n)+";N ", 250, 0, 25000)
        ut.bookHist(h, key+"_Nus", ';N. fired bars US;N ', 51, -0.5, 50.5)
        ut.bookHist(h, key+"_Nus_plane", ';N. fired bars US per station;N ', 11, 0, 11)
        for n in range(1, 6):
           ut.bookHist(h, key+"_Nus"+str(n), ';N. fired bars US, station '+str(n)+';N ', 11, -0.5, 10.5) 
        for n in range(2, 6):
            ut.bookHist(h, key+"_deltaUsBar"+str(n-1)+str(n), ';deltaUsBar'+str(n-1)+str(n)+';N ', 400, -20, 20) 

        ut.bookHist(h, key+'_maxdelta', ';MaxDelta', 1000, -50, 50)
        for n in range(1, 5):
            ut.bookHist(h, key+'_deltahit'+str(n)+str(n+1), ';Delta '+str(n)+'-'+str(n+1), 1000, -50, 50)

        ut.bookHist(h, key+'_QDCtot',';US total charge;N', 800, 0, 80000)
        for n in range(1, 6):
            ut.bookHist(h, key+'_QDCbar'+str(n),';US QDC/bar plane '+str(n)+';N', 800, 0, 80000)

        ut.bookHist(h, key+"_Nds", ';N. fired bars DS;N ', 101, -0.5, 100.5)
        ut.bookHist(h, key+"_Nds_plane", ';N. fired bars DS per station;N ', 101, 0, 100)
        for n in range(1, 5):
           ut.bookHist(h, key+"_Nds"+str(n), ';N. fired bars DS, station '+str(n)+';N ', 101, -0.5, 100.5) 

        fin = ROOT.TFile(f)
        tree = fin.tree
        for n in range(tree.GetEntries()):
            rc = tree.GetEvent(n)
            h[key+'_Nscifi'].Fill(tree.Nscifi, tree.weight)
            h[key+'_Nscifi1'].Fill(tree.Nscifi1, tree.weight)
            h[key+'_Nscifi2'].Fill(tree.Nscifi2, tree.weight)
            h[key+'_Nscifi3'].Fill(tree.Nscifi3, tree.weight)
            h[key+'_Nscifi4'].Fill(tree.Nscifi4, tree.weight)
            h[key+'_Nscifi5'].Fill(tree.Nscifi5, tree.weight)
            h[key+'_Nscifi_plane'].Fill(tree.Nscifi_plane, tree.weight)
            h[key+'_Nscificlus1'].Fill(tree.Nscifi_clus1, tree.weight)
            h[key+'_Nscificlus2'].Fill(tree.Nscifi_clus2, tree.weight)
            h[key+'_Nscificlus3'].Fill(tree.Nscifi_clus3, tree.weight)
            h[key+'_Nscificlus4'].Fill(tree.Nscifi_clus4, tree.weight)
            h[key+'_Nscificlus5'].Fill(tree.Nscifi_clus5, tree.weight)
            h[key+'_ScifiFrac1'].Fill(tree.ScifiFrac1, tree.weight)
            h[key+'_ScifiFrac2'].Fill(tree.ScifiFrac2, tree.weight)
            h[key+'_ScifiFrac3'].Fill(tree.ScifiFrac3, tree.weight)
            h[key+'_ScifiFrac4'].Fill(tree.ScifiFrac4, tree.weight)
            h[key+'_ScifiFrac5'].Fill(tree.ScifiFrac5, tree.weight)
            h[key+"_ScifiFrac3_4_5"].Fill(tree.ScifiFrac3+tree.ScifiFrac4+tree.ScifiFrac5, tree.weight)
            h[key+'_Nus'].Fill(tree.Nus, tree.weight)
            h[key+'_Nus_plane'].Fill(tree.Nus_plane, tree.weight)
            h[key+'_Nus1'].Fill(tree.Nus1, tree.weight)
            h[key+'_Nus2'].Fill(tree.Nus2, tree.weight)
            h[key+'_Nus3'].Fill(tree.Nus3, tree.weight)
            h[key+'_Nus4'].Fill(tree.Nus4, tree.weight)
            h[key+'_Nus5'].Fill(tree.Nus5, tree.weight)
            h[key+'_deltaUsBar12'].Fill(tree.deltaBar12, tree.weight)
            h[key+'_deltaUsBar23'].Fill(tree.deltaBar23, tree.weight)
            h[key+'_deltaUsBar34'].Fill(tree.deltaBar34, tree.weight)
            h[key+'_deltaUsBar45'].Fill(tree.deltaBar45, tree.weight)
            h[key+'_Nds'].Fill(tree.Nds, tree.weight)
            h[key+'_Nds_plane'].Fill(tree.Nds_plane, tree.weight)
            h[key+'_Nds1'].Fill(tree.Nds1, tree.weight)
            h[key+'_Nds2'].Fill(tree.Nds2, tree.weight)
            h[key+'_Nds3'].Fill(tree.Nds3, tree.weight)
            h[key+'_Nds4'].Fill(tree.Nds4, tree.weight)
            h[key+'_QDCtot'].Fill(tree.QDCtot, tree.weight)
            h[key+'_QDCbar1'].Fill(tree.QDCbar1, tree.weight)
            h[key+'_QDCbar2'].Fill(tree.QDCbar2, tree.weight)
            h[key+'_QDCbar3'].Fill(tree.QDCbar3, tree.weight)
            h[key+'_QDCbar4'].Fill(tree.QDCbar4, tree.weight)
            h[key+'_QDCbar5'].Fill(tree.QDCbar5, tree.weight)
            h[key+'_maxdelta'].Fill(tree.maxdelta, tree.weight)
            #print(tree.deltahit12)
            h[key+'_deltahit12'].Fill(tree.deltahit12, tree.weight)
            h[key+'_deltahit23'].Fill(tree.deltahit23, tree.weight)
            h[key+'_deltahit34'].Fill(tree.deltahit34, tree.weight)
            h[key+'_deltahit45'].Fill(tree.deltahit45, tree.weight)
            h[key+"_ScifiHitDensityX1"].Fill(tree.ScifiHitDensityX1, tree.weight)
            h[key+"_ScifiHitDensityX2"].Fill(tree.ScifiHitDensityX2, tree.weight)
            h[key+"_ScifiHitDensityX3"].Fill(tree.ScifiHitDensityX3, tree.weight)
            h[key+"_ScifiHitDensityX4"].Fill(tree.ScifiHitDensityX4, tree.weight)
            h[key+"_ScifiHitDensityX5"].Fill(tree.ScifiHitDensityX5, tree.weight)
            h[key+"_ScifiHitDensityY1"].Fill(tree.ScifiHitDensityY1, tree.weight)
            h[key+"_ScifiHitDensityY2"].Fill(tree.ScifiHitDensityY2, tree.weight)
            h[key+"_ScifiHitDensityY3"].Fill(tree.ScifiHitDensityY3, tree.weight)
            h[key+"_ScifiHitDensityY4"].Fill(tree.ScifiHitDensityY4, tree.weight)
            h[key+"_ScifiHitDensityY5"].Fill(tree.ScifiHitDensityY5, tree.weight)
            h[key+"_ScifiHitDensity_Mean1"].Fill(tree.ScifiHitDensity_Mean1, tree.weight)
            h[key+"_ScifiHitDensity_Mean2"].Fill(tree.ScifiHitDensity_Mean2, tree.weight)
            h[key+"_ScifiHitDensity_Mean3"].Fill(tree.ScifiHitDensity_Mean3, tree.weight)
            h[key+"_ScifiHitDensity_Mean4"].Fill(tree.ScifiHitDensity_Mean4, tree.weight)
            h[key+"_ScifiHitDensity_Mean5"].Fill(tree.ScifiHitDensity_Mean5, tree.weight)
        fout.cd()
        for name, hist in h.items():
            if key in name: 
                print("Writing with", key, 'and name', name)
                hist.Write()
    fout.Write()
    fout.Close()
    if args.compare: return foutName

def plotHistos():
    if len(args.inputFiles) == 1: f = args.inputFiles[0]
    histlist = load_hists(f)
    #Varlist = ['Nscifi', 'Nus', 'Nds', 'QDCtot', 'maxdelta']
    #Varlist = ['Nscifi', 'Nus', 'Nds', 'Nus_plane', 'maxdelta']
    Varlist = ['Nscifi','Nscifi1','Nscifi2','Nscifi3','Nscifi4','Nscifi5','Nscifi_plane','ScifiFrac1','ScifiFrac2','ScifiFrac3','ScifiFrac4','ScifiFrac5','ScifiFrac3_4_5', 'Nus','Nus1','Nus2','Nus3','Nus4','Nus5','Nus_plane','deltaUsBar12','deltaUsBar23','deltaUsBar34','deltaUsBar45','Nds','Nds_plane','Nds1','Nds2','Nds3', 'Nds4','QDCtot','QDCbar1','QDCbar2','QDCbar3','QDCbar4','QDCbar5','maxdelta','deltahit12','deltahit23','deltahit34','deltahit45', 'ScifiHitDensity_Mean1','ScifiHitDensity_Mean2','ScifiHitDensity_Mean3','ScifiHitDensity_Mean4','ScifiHitDensity_Mean5']
    noPlots = len(Varlist)
    global canvs
    canvs = createCanvas(noPlots)
    for icanv, canv in enumerate(canvs.values()):
        ipad = 0
        min = 6*icanv
        max = 6*(icanv+1)
        if max > len(Varlist): max= len(Varlist)
        for var in Varlist[min:max]:
            hlist = [h for name, h in histlist.items() if 'PMU_'+var == name or 'DATA_'+var == name or 'DISMC_'+var == name]
            if len(hlist) == 0: continue
            #print('Var is', var, 'Selected histos', hlist, 'name', hlist[0].GetName(), hlist[1].GetName(), hlist[2].GetName())
            pad = canv.cd(ipad+1)
            logy = False
            norm = True
            axtitle = 'a.u.'
            if 'Nscifi' in var or var == 'QDCtot' or 'ScifiHitDensity' in var: logy=True
            if 'Nscifi' in var:
                yaxrange=[1e-4, 30]
            else:
                yaxrange = None
            if args.lumi:
                norm = False
                axtitle='N'
                logy=True
                if args.norm: 
                    norm = True
                    axtitle= 'a.u.'
            drawDATAMC(hlist, c1=pad, xaxtitle=var, yaxtitle=axtitle, normalize=norm, extra_text='Comparison', logy=logy, lumi=args.lumi, yaxrange=yaxrange)
            if 'delta' in var: drawDATAMC(hlist, c1=pad, xaxtitle=var, yaxtitle=axtitle, normalize=norm, extra_text='Comparison', logy=logy, xaxrange=[-10,40], rebin=100, lumi=args.lumi)
            if var == 'Nds': drawDATAMC(hlist, c1=pad, xaxtitle=var, yaxtitle=axtitle, normalize=norm, extra_text='Comparison', logy=logy, xaxrange=[2,23], lumi=args.lumi)
            if var == 'QDCtot': drawDATAMC(hlist, c1=pad, xaxtitle=var, yaxtitle=axtitle, normalize=norm, extra_text='Comparison', logy=logy, xaxrange=[0,30000], lumi=args.lumi)
            if 'QDCbar' in var: drawDATAMC(hlist, c1=pad, xaxtitle=var, yaxtitle=axtitle, normalize=norm, extra_text='Comparison', logy=True, xaxrange=[0,10000], lumi=args.lumi)
            if var == 'Nscifi': drawDATAMC(hlist, c1=pad, xaxtitle=var, yaxtitle=axtitle, normalize=norm, extra_text='Comparison', logy=logy, xaxrange=[0,1500], lumi=args.lumi, yaxrange=yaxrange)
            if var == 'ScifiFrac3_4_5': drawDATAMC(hlist, c1=pad, xaxtitle=var, yaxtitle=axtitle, normalize=norm, extra_text='Comparison', logy=logy, lumi=args.lumi, rebin=500)
            ipad+=1
        if not canv.GetListOfPrimitives(): continue
        canv.SaveAs("prova"+str(icanv)+".pdf", "pdf")

def ProcessFile(file, geofile):
    import rootUtils as ut
    import SndlhcGeo
    geo = SndlhcGeo.GeoInterface(geofile)
    scifiDet = ROOT.gROOT.GetListOfGlobals().FindObject('Scifi')
    muFilterDet = ROOT.gROOT.GetListOfGlobals().FindObject('MuFilter')

    isMC = False
    treeName = 'rawConv'

    ch = ROOT.TChain(treeName)
    ch.Add(file)

    if ch.GetEntries() == 0 :
        treeName = "cbmsim"
        isMC = True
        del ch
        ch = ROOT.TChain(treeName)
        ch.Add(file)
    
    obj     = {}
    h       = {}
    WEIGHT   = 1
    tag = 'DATA'


    nevents = ch.GetEntries()
    print('N. of events:', nevents, 'Tag is', tag)

    variables = "ev_ID:event:weight:Nscifi:Nscifi1:Nscifi2:Nscifi3:Nscifi4:Nscifi5:Nscifi_plane:Nscifi_clus1:Nscifi_clus2:Nscifi_clus3:Nscifi_clus4:Nscifi_clus5:ScifiFrac1:ScifiFrac2:ScifiFrac3:ScifiFrac4:ScifiFrac5:Nus:Nus1:Nus2:Nus3:Nus4:Nus5:Nus_plane:deltaBar12:deltaBar23:deltaBar34:deltaBar45:Nds:Nds_plane:Nds1:Nds2:Nds3:Nds4:QDCL:QDCR:QDCtot:QDCbar1:QDCbar2:QDCbar3:QDCbar4:QDCbar5:maxdelta:deltahit12:deltahit23:deltahit34:deltahit45:ScifiHitDensityX1:ScifiHitDensityY1:ScifiHitDensityX2:ScifiHitDensityY2:ScifiHitDensityX3:ScifiHitDensityY3:ScifiHitDensityX4:ScifiHitDensityY4:ScifiHitDensityX5:ScifiHitDensityY5:ScifiHitDensity_Mean1:ScifiHitDensity_Mean2:ScifiHitDensity_Mean3:ScifiHitDensity_Mean4:ScifiHitDensity_Mean5:deltahit12_bug:deltahit23_bug:deltahit34_bug:deltahit45_bug:runID"
    if isMC:
        variables = "ev_ID:event:weight:muVtx_x:muVtx_y:muVtx_z:E_mu:Nscifi:Nscifi1:Nscifi2:Nscifi3:Nscifi4:Nscifi5:Nscifi_plane:Nscifi_clus1:Nscifi_clus2:Nscifi_clus3:Nscifi_clus4:Nscifi_clus5:ScifiFrac1:ScifiFrac2:ScifiFrac3:ScifiFrac4:ScifiFrac5:Nus:Nus1:Nus2:Nus3:Nus4:Nus5:Nus_plane:deltaBar12:deltaBar23:deltaBar34:deltaBar45:Nds:Nds_plane:Nds1:Nds2:Nds3:Nds4:QDCL:QDCR:QDCtot:QDCbar1:QDCbar2:QDCbar3:QDCbar4:QDCbar5:maxdelta:deltahit12:deltahit23:deltahit34:deltahit45:ScifiHitDensityX1:ScifiHitDensityY1:ScifiHitDensityX2:ScifiHitDensityY2:ScifiHitDensityX3:ScifiHitDensityY3:ScifiHitDensityX4:ScifiHitDensityY4:ScifiHitDensityX5:ScifiHitDensityY5:ScifiHitDensity_Mean1:ScifiHitDensity_Mean2:ScifiHitDensity_Mean3:ScifiHitDensity_Mean4:ScifiHitDensity_Mean5:E_end:E_had:dis_flag"
    
    foutName = tag+'-ProcessedEvents.root'
    if args.procID != None: foutName = tag+'-ProcessedEvents_'+str(args.procID)+'.root'
    fout = ROOT.TFile.Open(outdir+'/'+foutName, 'recreate')
    data = ROOT.TNtuple("tree", "ProcessedData", variables)
    #data = ROOT.TTree("tree", "ProcessedData")
    vardict = {}

    vLeft, vRight = ROOT.TVector3(), ROOT.TVector3()
    HTC_nevents = 10000

    for i_event, event in enumerate(ch):
        scifiDet.InitEvent(event.EventHeader)
        muFilterDet.InitEvent(event.EventHeader)
        if args.procID != None:
            if not (i_event > args.procID*HTC_nevents and i_event < HTC_nevents*(args.procID+1)): continue
        if not i_event%10000: print('Sanity check', i_event)
        column = []
        column.append(i_event)
        column.append(ch.EventHeader.GetEventNumber())
        if isMC:
            muontrack = event.MCTrack[0]
        column.append(WEIGHT)

        #variables
        Nus     = 0
        Nsf     = 0
        Nds     = 0
        Stotr = 0
        Stotl = 0
        US_QDC = 0
        nsf_statID = {1:0, 2:0, 3:0, 4:0, 5:0}
        nsf_statID_bug = {1:0, 2:0, 3:0, 4:0, 5:0}
        nus_statID = {1:0, 2:0, 3:0, 4:0, 5:0}
        nds_statID = {1:0, 2:0, 3:0, 4:0}
        QDCus_statID = {1:0, 2:0, 3:0, 4:0, 5:0}
        E_start = -1000
        E_end = -1000
        E_had = -1000

        NsfClPl_H       =  {1:0, 2:0, 3:0, 4:0, 5:0}
        NsfClPl_V       =  {1:0, 2:0, 3:0, 4:0, 5:0}

        Scifi_HitCollectionX = {1:[], 2:[], 3:[], 4:[], 5:[]}
        Scifi_HitCollectionY = {1:[], 2:[], 3:[], 4:[], 5:[]}

        Nsfcl= 0
        if not isMC:
            DATA_scifiCluster = scifiCluster(event.Digi_ScifiHits, scifiDet)
            for aCl in DATA_scifiCluster:
                detID = aCl.GetFirst()
                Nsfcl+=1
                station = int(detID/1e+6)
                if int(detID/100000)%10 == 1: 
                    NsfClPl_V[int(detID/1e+6)]+=1
                else:
                    NsfClPl_H[int(detID/1e+6)]+=1
        else:
            for aCl in event.Cluster_Scifi: # MonteCarlo clustering
                detID = aCl.GetFirst()
                Nsfcl+=1
                station = int(detID/1e+6)
                if int(detID/100000)%10 == 1: 
                    NsfClPl_V[int(detID/1e+6)]+=1
                else:
                    NsfClPl_H[int(detID/1e+6)]+=1

        if isMC:
            E_start = event.MCTrack[0].GetEnergy()

        #### TIME CORRECTION
        if not isMC:
            avg_sf_x, avg_sf_y = getAvgScifiPos(event, scifiDet)
            rangePerStation = getTimeCorrectedRange(event, scifiDet)

        for aHit in event.Digi_ScifiHits:
            if not aHit.isValid(): continue
            station = aHit.GetStation()
            detID = aHit.GetDetectorID()
            scifiDet.GetSiPMPosition(detID, vLeft, vRight)
            nsf_statID_bug[station]+=1
            
            if not isMC:
                L = None
                if aHit.isVertical(): L = vRight.Y()-avg_sf_y[station]
                else: L = avg_sf_x[station]-vLeft.X()
                hit_time = scifiDet.GetCorrectedTime(detID, aHit.GetTime()*TDC2ns, L)
                if not isInTimeRange(hit_time, rangePerStation[station][0], rangePerStation[station][1]): continue

            if aHit.isVertical():
                Scifi_HitCollectionX[station].append(vLeft.X())
            else:
                Scifi_HitCollectionY[station].append(vRight.Y())

        Nsf_corr, Nsf_bug, nsf_statID_corr = CorrectScifi(event=event, scifiDet=scifiDet)
        if isMC:
            Nsf = Nsf_bug
            nsf_statID = nsf_statID_bug
        else:
            Nsf = Nsf_corr
            nsf_statID = nsf_statID_corr

        for aHit in event.Digi_MuFilterHits:
            detID = aHit.GetDetectorID()
            nSiPMs = aHit.GetnSiPMs()
            nSides  = aHit.GetnSides()
            allChannels = aHit.GetAllSignals(False)
            MuFistation = aHit.GetPlane()
            if not aHit.isValid(): continue
            if aHit.GetSystem()==2:
                Nus+=1
                nus_statID[MuFistation+1]+=1
                Nleft   = 0
                Nright  = 0
                Sleft   = 0
                Sright  = 0
                for c in allChannels:
                    if  nSiPMs > c[0]:  # left side
                        Nleft+=1
                        Sleft+=c[1]
                    else:
                        Nright+=1
                        Sright+=c[1]
                Stotr +=Sright #QDC US value NOT CALIBRATED
                Stotl +=Sleft
                QDChit = 0
                for key, value in allChannels:
                    US_QDC += value
                    QDChit +=value
                p, bar = GetBar(detID)
                QDCus_statID[MuFistation+1]+=QDChit
            if aHit.GetSystem()==3:
                Nds+=1
                nds_statID[MuFistation+1]+=1

        if isMC:
            Nus_corr, nus_statID_corr = getCorrUShits(event.Digi_MuFilterHits, event.Digi_MuFilterHits2MCPoints[0], event.MuFilterPoint)
            Nus = Nus_corr
            nus_statID = nus_statID_corr

        FirstSFHit = -1
        deltahits = {2:0, 3:0, 4:0, 5:0}
        ScifiFrac = {1:None, 2:None, 3:None, 4:None, 5:None}
        FirstSFHit = next((i for i, x in enumerate(nsf_statID.values()) if x), None)+1
        for detID in range(1, 6):
            if detID > FirstSFHit and nsf_statID[detID-1] and detID > 1:
                deltahits[detID] = float((nsf_statID[detID]-nsf_statID[detID-1])/nsf_statID[detID-1])
        MaxDelta = max([value for key, value in deltahits.items() if key > 2])
        MaxKey = [key for key, value in deltahits.items() if value == MaxDelta]
        if not isMC:
            deltahits_bug = {2:0, 3:0, 4:0, 5:0}
            for detID in range(1,6):
                if detID > FirstSFHit and nsf_statID_bug[detID-1] and detID > 1:
                    deltahits_bug[detID] = float((nsf_statID_bug[detID]-nsf_statID_bug[detID-1])/nsf_statID_bug[detID-1])
        for detID in range(1,6):
            ScifiFrac[detID]=float(nsf_statID[detID]/Nsf)
        for key in QDCus_statID.keys():
            if nus_statID[key] == 0: continue
            QDCus_statID[key] = float(QDCus_statID[key]/nus_statID[key])
        
        deltaBars = {2:0, 3:0, 4:0, 5:0}
        for plane in range(2, 6):
            if nus_statID[plane-1] == 0: continue
            deltaBars[plane] = float((nus_statID[plane]-nus_statID[plane-1])/nus_statID[plane-1])

        
        if isMC: US_QDC = US_QDC - 100

        ## Fill the column with variables
        column.append(Nsf)
        for n in nsf_statID.values():
            column.append(n)
        column.append(float(Nsf/5.))
        for n in NsfClPl_H.keys():
            column.append(NsfClPl_H[n]+NsfClPl_V[n])
        for n in ScifiFrac.values():
            column.append(n)
        column.append(Nus)
        for n in nus_statID.values():
            column.append(n)
        column.append(float(Nus/5.))
        for n in range(2, 6):
            column.append(deltaBars[n])
        column.append(Nds)
        column.append(float(Nds/7.))
        for n in nds_statID.values():
            column.append(n)
        column.append(Stotl)
        column.append(Stotr)
        column.append(US_QDC)
        for n in QDCus_statID.values():
            column.append(n)
        column.append(MaxDelta)
        for d in deltahits.values():
            column.append(d)
        for i in range(1, 6):
            column.append(getScifiHitDensity(Scifi_HitCollectionX[i]))
            column.append(getScifiHitDensity(Scifi_HitCollectionY[i]))
        for i in range(1, 6):
            column.append((getScifiHitDensity(Scifi_HitCollectionX[i])+getScifiHitDensity(Scifi_HitCollectionY[i]))/2)
        if not isMC:
            for d in deltahits_bug.values():
                column.append(d)
        if isMC: 
            column.append(E_end)
            column.append(E_had)
            column.append(dis_flag)
        if not isMC: column.append(ch.EventHeader.GetRunId())
        theTuple = array('f', column)
        data.Fill(theTuple)
    
    fin = ROOT.TFile.Open(file)
    if fin.Get("cutFlow"):
        cutflow =  fin.Get("cutFlow").Clone("cutFlow")
    else:
        print('No cutflow histogram found!')
    fout.cd()
    data.Write()
    cutflow.Write()
    fin.Close()
    if args.compare: return foutName



if not args.inputFiles:
    #raise Exception('No inputfiles provided!')
    pass

elif args.process:
    for f in args.inputFiles:
        pmu = False
        tag = ''
        if 'PMU' in f: 
            pmu = True
            tag = 'PMU'
        else:
            tag = 'DATA'
        ProcessFile(f, geofile=geofiles[tag])

if args.compare:
    files = {}
    for f in args.inputFiles:
        pmu = False
        tag = ''
        if 'PMU' in f: 
            pmu = True
            tag = 'PMU'
        elif 'DATA' in f:
            tag = 'DATA'
        else: tag = 'DIS'
        files[tag] = ProcessFile(f, geofile=geofiles[tag], pmu=pmu)
    args.inputFiles = [file for file in files.values()]
    fout = mergeDATA_MC()
    args.inputFiles = [fout]
    #plotHistos()

if args.merge:
    mergeDATA_MC()

def CompareCutflow(lumi=0.63, runN = ''):
    hists = {}
    hname = 'cutFlow2_extended2_extended_more2'
    colorlist = [ROOT.kAzure-4, ROOT.kRed, ROOT.kGreen+1]
    global canv
    canv = ROOT.TCanvas("canv", "canv")
    canv.SetLogy()
    for f in args.inputFiles:
        pmu = False
        tag = ''
        if 'PMU' in f: 
            pmu = True
            tag = 'PMU'
        elif 'DATA' in f:
            tag = 'DATA'
        else: tag = 'DIS'
        hists[tag] = load_hists(f, query=hname)
    for key in hists.keys():
        if key == 'DATA': continue
        hists[key][hname].Scale(lumi)
    for i, key in enumerate(hists.keys()):
        hist = hists[key][hname]
        hist.SetTitle(key)
        hist.GetXaxis().SetBinLabel(2, "Hits in Veto")
        hist.GetXaxis().SetBinLabel(3, "SciFi station 1 fired")
        if key == 'DATA':
            if runN: 
                hist.SetTitle(key+' Run-'+str(runN)+' L_{int} = '+str(lumi)+' fb^{-1}')
            elif lumi:
                hist.SetTitle(key+' L_{int} = '+str(lumi)+' fb^{-1}')
        elif lumi:
             hist.SetTitle(key+'@ L_{int}')
        hist.SetLineColor(colorlist[i])
        canv.cd()
        if i == 0: hist.Draw("HIST TEXT10 E")
        else: hist.Draw("HIST TEXT10 SAMES E")
        """if i == 0: hist.Draw("HIST")
        else: hist.Draw("HIST SAMES")"""
        hist.GetYaxis().SetRangeUser(1, 1e10)
    ROOT.gPad.BuildLegend()



def analyseScifiDensity(tag):
    import rootUtils as ut
    if len(args.inputFiles) == 1: f = args.inputFiles[0]
    else: raise Exception("More than one file provided!")
    fin = ROOT.TFile(f)
    tree = fin.tree
    h = {}
    for n in range(1, 6):
        ut.bookHist(h, str(tag)+"ScifiHitDensity_Mean"+str(n), "Mean Scifi hit density in station "+str(n)+";N ", 250, 0, 25000)
    ut.bookHist(h, str(tag)+"ScifiHitDensity_sum", "Sum of Scifi hit densities;N; sum of hit densities", 250, 0, 25000)
    for n in range(tree.GetEntries()):
        rc = tree.GetEvent(n)
        hit_density = {}
        hit_density[1] = float((tree.ScifiHitDensityX1+tree.ScifiHitDensityY1)/2.)
        hit_density[2] = float((tree.ScifiHitDensityX2+tree.ScifiHitDensityY2)/2.)
        hit_density[3] = float((tree.ScifiHitDensityX3+tree.ScifiHitDensityY3)/2.)
        hit_density[4] = float((tree.ScifiHitDensityX4+tree.ScifiHitDensityY4)/2.)
        hit_density[5] = float((tree.ScifiHitDensityX5+tree.ScifiHitDensityY5)/2.)
        for plane in range(1, 6):
            h[str(tag)+'ScifiHitDensity_Mean'+str(plane)].Fill(hit_density[plane], tree.weight)
        sum_hit_density = sum([x for x in hit_density.values()])
        if sum_hit_density > 2000: print('Ev no', n)
        h[str(tag)+'ScifiHitDensity_sum'].Fill(sum_hit_density, tree.weight)
       
    fout = ROOT.TFile.Open("analyseScifiDensity_"+str(tag)+".root", "RECREATE")
    for _h in h.values():
        _h.Write()
    fout.Write()
    fout.Close()
    fin.Close()

def plotTogether():
    hs ={}
    for _f in args.inputFiles:
        tag = ''
        if 'DATA' in _f:
            tag='DATA'
        elif 'PMU' in _f:
            tag='PMU'
        elif 'DIS' in _f:
            tag='DIS'
        hs[tag] = load_hists(_f)
    histlist = {}
    for tag, dic in hs.items():
        for name, h in dic.items():
            histlist[name] = h
    Varlist = ['ScifiHitDensity_Mean1', 'ScifiHitDensity_Mean2', 'ScifiHitDensity_Mean3', 'ScifiHitDensity_Mean4', 'ScifiHitDensity_Mean5', 'ScifiHitDensity_sum']
    noPlots = len(Varlist)
    global canvs
    canvs = createCanvas(noPlots)
    for icanv, canv in enumerate(canvs.values()):
        ipad = 0
        min = 6*icanv
        max = 6*(icanv+1)
        if max > len(Varlist): max= len(Varlist)
        for var in Varlist[min:max]:
            hlist = [h for name, h in histlist.items() if 'PMU'+var == name or 'DATA'+var == name or 'DIS'+var == name]
            #print('Var is', var, 'Selected histos', hlist, 'name', hlist[0].GetName(), hlist[1].GetName(), hlist[2].GetName())
            pad = canv.cd(ipad+1)
            logy = False
            norm = True
            axtitle = 'a.u.'
            if 'ScifiHitDensity' in var: logy=True
            if 'Nscifi' in var:
                yaxrange=[1e-4, 30]
            else:
                yaxrange = None
            if args.lumi:
                norm = False
                axtitle='N'
                logy=True
                if args.norm: 
                    norm = True
                    axtitle= 'a.u.'
            drawDATAMC(hlist, c1=pad, xaxtitle=var, yaxtitle=axtitle, normalize=norm, extra_text='Comparison', logy=logy, lumi=args.lumi, yaxrange=yaxrange)   
            ipad+=1

    
def PlotTogether2D():
    files = {}
    for f in args.inputFiles:
        if 'PMU' in f:
            files['PMU'] = f
        elif 'DATA' in f:
            files['DATA'] = f
        else:
            files['DIS'] = f
    global h
    h = {}
    for key, f in files.items():
        h[key] = ROOT.TH2I("Var_"+key, "Var"+key, 11, 0, 11, 11, 0, 11)
        h[key].SetDirectory(ROOT.gROOT)
        fin = ROOT.TFile.Open(f)
        tree = fin.tree
        print(h[key])
        for n in range(tree.GetEntries()):
            rc = tree.GetEvent(n)
            h[key].Fill(tree.Nus1, tree.Nus2)
            if key == 'DATA' : print(tree.Nus1, tree.Nus2)
        if key == 'DATA': 
            h[key].SetMarkerColor(ROOT.kBlack)
            h[key].SetMarkerStyle(22)
        elif key == 'PMU':
            h[key].SetMarkerColor(ROOT.kRed)
            h[key].SetMarkerStyle(21)
        else:
            h[key].SetMarkerColor(ROOT.kBlue)
            h[key].SetMarkerStyle(20)
    global c
    c = ROOT.TCanvas("c", "c2", 800, 600)
    for _h in h.values():
        _h.Draw("SAMES")
    c.Draw()

def ScifiHit2D(plane=args.sfplane):
    tag = 'DATA'
    file = args.inputFiles[0]
    geofile = geofiles[tag]
    import rootUtils as ut
    import SndlhcGeo
    import numpy as np
    geo = SndlhcGeo.GeoInterface(geofile)
    scifiDet = ROOT.gROOT.GetListOfGlobals().FindObject('Scifi')
    muFilterDet = ROOT.gROOT.GetListOfGlobals().FindObject('MuFilter')

    isMC = False
    treeName = 'rawConv'

    ch = ROOT.TChain(treeName)
    ch.Add(file)

    if ch.GetEntries() == 0 :
        treeName = "cbmsim"
        isMC = True
        del ch
        ch = ROOT.TChain(treeName)
        ch.Add(file)
    
    obj     = {}
    h       = {}
    WEIGHT  = 1
    nbins   = 500
    

    nevents = ch.GetEntries()
    print('N. of events:', nevents, 'Tag is', tag)

    foutName = tag+'TRID'+str(args.trid)+'-Scifi2dHits.root'
    fout = ROOT.TFile.Open(outdir+'/'+foutName, 'recreate')
    track_conv_pos, track_conv_angles = GetTrackPos('/eos/experiment/sndlhc/emulsionData/2022/emureco_Napoli/RUN1/b000121/b000121.100.0.0.trk.root', trid=args.trid)
    print('Muon track converted positon', track_conv_pos.X(), track_conv_pos.Y(), track_conv_pos.Z())
    h['trackPoints_master'] = ROOT.TGraphErrors()
    h['trackPoints_master'].SetName('trackPoints_master')
    h['trackPoints_master'].AddPoint(track_conv_pos.X(), track_conv_pos.Y())

    vLeft, vRight = ROOT.TVector3(), ROOT.TVector3()
    for i_event, event in enumerate(ch):
        scifiDet.InitEvent(event.EventHeader)
        muFilterDet.InitEvent(event.EventHeader)
        event_no = event.EventHeader.GetEventNumber()
        run_no = event.EventHeader.GetRunId()
        #event_no = i_event

        ut.bookHist(h, 'r'+str(run_no)+'ev'+str(event_no)+'_Scifi2D_p'+str(plane), 'Scifi 2d Hit Distribution plane '+str(plane), nbins,-50 ,0, nbins, 10, 60)
        ut.bookHist(h, 'r'+str(run_no)+'ev'+str(event_no)+'_Scifi_X_p'+str(plane), 'Scifi Hit X Distribution plane '+str(plane),nbins,-50 ,0)
        ut.bookHist(h, 'r'+str(run_no)+'ev'+str(event_no)+'_Scifi_Y_p'+str(plane), 'Scifi Hit Y Distribution plane '+str(plane),nbins, 10, 60)
        
        xbinwidth = h['r'+str(run_no)+'ev'+str(event_no)+'_Scifi2D_p'+str(plane)].GetXaxis().GetBinWidth(1)
        ybinwidth = h['r'+str(run_no)+'ev'+str(event_no)+'_Scifi2D_p'+str(plane)].GetYaxis().GetBinWidth(1)
        #variables
        Nsf     = 0
        nsf_statID = {1:0, 2:0, 3:0, 4:0, 5:0}
        nsf_statID_bug = {1:0, 2:0, 3:0, 4:0, 5:0}
        nus_statID = {1:0, 2:0, 3:0, 4:0, 5:0}
        nds_statID = {1:0, 2:0, 3:0, 4:0}
        Scifi_HitCollectionX = {1:[], 2:[], 3:[], 4:[], 5:[]}
        Scifi_HitCollectionY = {1:[], 2:[], 3:[], 4:[], 5:[]}

        if not isMC:
            avg_sf_x, avg_sf_y = getAvgScifiPos(event, scifiDet)
            rangePerStation = getTimeCorrectedRange(event, scifiDet)

        for aHit in event.Digi_ScifiHits:
            if not aHit.isValid(): continue
            station = aHit.GetStation()
            detID = aHit.GetDetectorID()
            scifiDet.GetSiPMPosition(detID, vLeft, vRight)
            nsf_statID_bug[station]+=1
            if station != plane: continue
            
            if not isMC:
                L = None
                if aHit.isVertical(): L = vRight.Y()-avg_sf_y[station]
                else: L = avg_sf_x[station]-vLeft.X()
                hit_time = scifiDet.GetCorrectedTime(detID, aHit.GetTime()*TDC2ns, L)
                if not isInTimeRange(hit_time, rangePerStation[station][0], rangePerStation[station][1]): continue

            if aHit.isVertical():
                Scifi_HitCollectionX[station].append(vLeft.X())
                h['r'+str(run_no)+'ev'+str(event_no)+'_Scifi_X_p'+str(plane)].Fill(vLeft.X())
                for bin in np.arange(0, vRight.Y()-vLeft.Y(), xbinwidth):
                    h['r'+str(run_no)+'ev'+str(event_no)+'_Scifi2D_p'+str(plane)].Fill(vLeft.X(), vRight.Y()-bin)
            else:
                Scifi_HitCollectionY[station].append(vRight.Y())
                h['r'+str(run_no)+'ev'+str(event_no)+'_Scifi_Y_p'+str(plane)].Fill(vRight.Y())
                for bin in np.arange(0, vRight.X()-vLeft.X(), ybinwidth):
                    h['r'+str(run_no)+'ev'+str(event_no)+'_Scifi2D_p'+str(plane)].Fill(vLeft.X()+bin, vRight.Y())
    
    fout.cd()
    for _h in h.values():
        _h.Write()
    fout.Write()
    fout.Close()
    if args.auto: return outdir+'/'+foutName

def fitScifiHits(histlist, evno):
    if 'X' not in histlist.keys() or 'Y' not in histlist.keys(): raise Exception('Please provide the dictionary in the right format')
    print('Fit event', evno, '-----------')

    if histlist['X'].GetEntries() ==0: 
        print('ev', evno,'Fit data empty for X proj!')
        return None, None
    Xfit = histlist['X'].Fit("gaus", "S", "", -35, -15)
    if not Xfit.Get():
        print('XFit not converging/failed,', evno)
        return None, None
    #mean_Xfit, meanerror_Xfit, sigma_Xfit, sigmaerror_Xfit = None, None, None, None
    mean_Xfit =  histlist['X'].GetListOfFunctions().FindObject("gaus").GetParameter(1)
    meanerror_Xfit =  histlist['X'].GetListOfFunctions().FindObject("gaus").GetParError(1)
    sigma_Xfit =  histlist['X'].GetListOfFunctions().FindObject("gaus").GetParameter(2)
    sigmaerror_Xfit =  histlist['X'].GetListOfFunctions().FindObject("gaus").GetParError(2)
    
    #histlist['X'].GetListOfFunctions().FindObject("gaus").Delete()

    if histlist['Y'].GetEntries() ==0: 
        print('ev', evno,'Fit data empty for Y proj!')
        return None, None
    Yfit = histlist['Y'].Fit("gaus", "S", "", 20, 35)
    if not Yfit.Get():
        print('YFit not converging/failed,', evno)
        return None, None
    #mean_Yfit, meanerror_Yfit, sigma_Yfit, sigmaerror_Yfit = None, None, None, None
    mean_Yfit =  histlist['Y'].GetListOfFunctions().FindObject("gaus").GetParameter(1)
    meanerror_Yfit =  histlist['Y'].GetListOfFunctions().FindObject("gaus").GetParError(1)
    sigma_Yfit =  histlist['Y'].GetListOfFunctions().FindObject("gaus").GetParameter(2)
    sigmaerror_Yfit =  histlist['Y'].GetListOfFunctions().FindObject("gaus").GetParError(2)

    #histlist['Y'].GetListOfFunctions().FindObject("gaus").Delete()

    values = {'mean': [mean_Xfit, mean_Yfit], 'sigma': [sigma_Xfit, sigma_Yfit]}
    errors = {'mean': [meanerror_Xfit, meanerror_Yfit], 'sigma': [sigmaerror_Xfit, sigmaerror_Yfit]}
    print('End fit event', evno, '-----------')
    print(' ')
    return values, errors

def GetScifiFits():
    f = ROOT.TFile.Open(args.inputFiles[0])
    keylist = f.GetListOfKeys()
    evlist = []
    ev_to_run = {}
    for key in keylist:
        name = key.GetName()
        ev = name[7:name.find('_')]
        run = name[1:5]
        ev_to_run[ev] = run
        evlist.append(ev)
    evlist = list(set(evlist))
    print('Read ', len(evlist), 'events')
    FitValues = {}
    FitErros = {}
    failed_evts = list()
    for ev in evlist:
        run = ev_to_run[ev]
        hdict = {}
        hX = None
        hY = None
        hX = f.Get('r'+str(run)+'ev'+str(ev)+'_Scifi_X_p2')
        #hX.SetDirectory(ROOT.gROOT)
        hY = f.Get('r'+str(run)+'ev'+str(ev)+'_Scifi_Y_p2')
        #hY.SetDirectory(ROOT.gROOT)
        if hX.GetEntries() < 10 or hY.GetEntries() < 10:
            failed_evts.append([run, ev])
            continue
        hdict = {'X':hX, 'Y':hY}
        values, errors = fitScifiHits(hdict, ev)
        if values is not None and errors is not None:
            FitValues[ev] = values
            FitErros[ev] = errors
        else:
            failed_evts.append([run, ev])
        
    print('Failed events', failed_evts)
    for ev in FitValues.keys():
        graph_mean_sigma.AddPointError(FitValues[ev]['mean'][0], FitValues[ev]['mean'][1], FitValues[ev]['sigma'][0], FitValues[ev]['sigma'][1])
    meanx = array('d', [FitValues[ev]['mean'][0] for ev in FitValues.keys()])
    meany = array('d', [FitValues[ev]['mean'][1] for ev in FitValues.keys()])
    sigmax = array('d', [FitValues[ev]['sigma'][0] for ev in FitValues.keys()])
    sigmay = array('d', [FitValues[ev]['sigma'][1] for ev in FitValues.keys()])
    zeros = array('d', [0]*len(evlist))
    #graph_mean_sigma = ROOT.TGraphErrors(len(evlist), meanx, meany, sigmax, sigmay)
    graph_mean_sigma = ROOT.TGraphErrors(len(evlist), meanx, meany, zeros, zeros)
    graph_mean_sigma.SetMarkerColor(ROOT.kRed)
    graph_mean_sigma.GetXaxis().SetTitle('Mean X from fit')
    graph_mean_sigma.GetYaxis().SetTitle('Mean Y from fit')
    graph_mean_sigma.SetName('graph_mean_sigma')
    global c1
    c1 = ROOT.TCanvas("c1", "c1", 800, 600)
    graph_mean_sigma.DrawClone("AP*")
    track_graph.Draw("P*")
    c1.Draw()
    tfile = ROOT.TFile.Open(args.inputFiles[1])
    track_graph = tfile.Get('trackPoints_master').Clone('trackPoints_master')
    f.Close()
    tfile.Close()

def gaussian(x, amplitude, mean, stddev):
    return amplitude * np.exp(-((x - mean) ** 2) / (2 * stddev ** 2))

def negative_log_likelihood(amplitude, mean, stddev, data):
    return -np.sum(np.log(gaussian(data, amplitude, mean, stddev)))

def negative_log_likelihood_closure(data):
    def nll(amplitude, mean, stddev):
        return negative_log_likelihood(amplitude, mean, stddev, data)
    return nll


def UnbinnedFit(tfilename, plane=args.sfplane):
    """
	Usage: python -i MuMatch_processEvent.py -f datacutfile datascifi2dhits --trid TRID
	"""
    if args.auto: ROOT.gROOT.SetBatch(True)
    tag = 'DATA'
    file = args.inputFiles[0]
    geofile = geofiles[tag]
    import rootUtils as ut
    import SndlhcGeo
    import numpy as np   
    import matplotlib.pyplot as plt
    from iminuit import Minuit, cost
    geo = SndlhcGeo.GeoInterface(geofile)
    scifiDet = ROOT.gROOT.GetListOfGlobals().FindObject('Scifi')
    muFilterDet = ROOT.gROOT.GetListOfGlobals().FindObject('MuFilter')

    isMC = False
    treeName = 'rawConv'

    ch = ROOT.TChain(treeName)
    ch.Add(file)
    f = ch.GetFile()

    if ch.GetEntries() == 0 :
        treeName = "cbmsim"
        isMC = True
        del ch
        ch = ROOT.TChain(treeName)
        ch.Add(file)


    outfile = ROOT.TFile.Open(args.outdir+'/DATATRID{0}-selected_events.root'.format(args.trid), "RECREATE")
    output_tree = ch.CloneTree(0)
    # Copy branch list
    branch_list = f.Get("BranchList")
    branch_list_copy = branch_list.Clone()
    branch_list_copy.Write("BranchList", 1)
    
    h       = {}
    WEIGHT  = 1

    nevents = ch.GetEntries()
    print('N. of events:', nevents, 'Tag is', tag)

    fitted_meansX_list = list()
    fitted_meansY_list = list()
    fitted_stdX_list = list()
    fitted_stdY_list = list()
    track_conv_pos, track_conv_angles = GetTrackPos('/eos/experiment/sndlhc/emulsionData/2022/emureco_Napoli/RUN1/b000121/b000121.100.0.0.trk.root', trid=args.trid)
    area_dim = 1 #cm
    fine_cut_evts = 0
    fine_cut_passed = list()

    vLeft, vRight = ROOT.TVector3(), ROOT.TVector3()
    for i_event, event in enumerate(ch):
        #if i_event > 20: break
        scifiDet.InitEvent(event.EventHeader)
        muFilterDet.InitEvent(event.EventHeader)
        event_no = event.EventHeader.GetEventNumber()
        run_no = event.EventHeader.GetRunId()

        #variables
        Nsf     = 0
        nsf_statID = {1:0, 2:0, 3:0, 4:0, 5:0}
        nsf_statID_bug = {1:0, 2:0, 3:0, 4:0, 5:0}
        nus_statID = {1:0, 2:0, 3:0, 4:0, 5:0}
        nds_statID = {1:0, 2:0, 3:0, 4:0}
        Scifi_HitCollectionX = {1:[], 2:[], 3:[], 4:[], 5:[]}
        Scifi_HitCollectionY = {1:[], 2:[], 3:[], 4:[], 5:[]}

        #### TIME CORRECTION
        if not isMC:
            avg_sf_x, avg_sf_y = getAvgScifiPos(event, scifiDet)
            wavg_sf_x, wavg_sf_y = getWAvgScifiPos(event, scifiDet)
            rangePerStation = getTimeCorrectedRange(event, scifiDet)

        ret, value = ScifiAvgPos(event, scifiDet, plane, area_dim, track_conv_pos)
        if not ret: continue

        for aHit in event.Digi_ScifiHits:
            if not aHit.isValid(): continue
            station = aHit.GetStation()
            detID = aHit.GetDetectorID()
            scifiDet.GetSiPMPosition(detID, vLeft, vRight)
            nsf_statID_bug[station]+=1
            Nsf+=1
            if station != plane: continue
            
            if not isMC:
                L = None
                if aHit.isVertical(): L = vRight.Y()-avg_sf_y[station]
                else: L = avg_sf_x[station]-vLeft.X()
                hit_time = scifiDet.GetCorrectedTime(detID, aHit.GetTime()*TDC2ns, L)
                if not isInTimeRange(hit_time, rangePerStation[station][0], rangePerStation[station][1]): continue

            if aHit.isVertical():
                Scifi_HitCollectionX[station].append(vLeft.X())
            else:
                Scifi_HitCollectionY[station].append(vRight.Y())

        #Nsf_corr, Nsf_bug, nsf_statID_corr = CorrectScifi(event=event, scifiDet=scifiDet)

        xpositions = np.array([pos for pos in Scifi_HitCollectionX[plane] if pos > track_conv_pos.X()-10 and pos < track_conv_pos.X()+10])
        ypositions = np.array([pos for pos in Scifi_HitCollectionY[plane] if pos > track_conv_pos.Y()-10 and pos < track_conv_pos.Y()+10])

        if len(xpositions) == 0 or len(ypositions) == 0:
            #print('R', run_no, 'Ev', event_no, 'empty data!')
            continue


        fitted_meansX_list.append(np.mean(xpositions))
        fitted_meansY_list.append(np.mean(ypositions))
        fitted_stdX_list.append(np.std(xpositions))
        fitted_stdY_list.append(np.std(ypositions))
        #if abs(np.mean(xpositions)+25) < 0.5 and abs(np.mean(ypositions)-25) < 0.5 and (np.std(xpositions)>1 or np.std(ypositions)>1) and nsf_statID_bug[plane] > 100 and nsf_statID_bug[plane]/Nsf < 0.8:
        if abs(wavg_sf_x[plane]-track_conv_pos.X()) < 0.5 and abs(wavg_sf_y[plane]-track_conv_pos.Y()) < 0.5 and (np.std(xpositions)>1 or np.std(ypositions)>1) and nsf_statID_bug[plane] > 100 and nsf_statID_bug[plane]/Nsf < 0.8:
            print('R', run_no, 'Ev', event_no, 'Nsf', Nsf, 'Nsf2', nsf_statID_bug[plane])
            print('meanX', np.mean(xpositions), 'stdX', np.std(xpositions))
            print('meanY', np.mean(ypositions), 'stdY', np.std(ypositions))
            print('WmeanX', wavg_sf_x[plane])
            print('WmeanY', wavg_sf_y[plane])
            fine_cut_evts+=1
            fine_cut_passed.append([run_no, event_no])
            output_tree.Fill()
            
    print(fine_cut_evts, 'events passed the fine cuts')
    meanX_arr = array('d', fitted_meansX_list)
    meanY_arr = array('d', fitted_meansY_list)
    stdX_arr = array('d', fitted_stdX_list)
    stdY_arr = array('d', fitted_stdY_list)
    zeros = array('d', [0]*len(meanX_arr))
    graph_mean_sigma = ROOT.TGraphErrors(len(meanX_arr), meanX_arr, meanY_arr, stdX_arr, stdY_arr)
    graph_mean_sigma.SetMarkerColor(ROOT.kRed)
    graph_mean_sigma.GetXaxis().SetTitle('Mean X from fit')
    graph_mean_sigma.GetYaxis().SetTitle('Mean Y from fit')
    graph_mean_sigma.SetName('graph_mean_sigma')
    global c1
    c1 = ROOT.TCanvas("c1", "c1", 800, 600)
    graph_mean_sigma.DrawClone("AP*")
    tfile = ROOT.TFile.Open(tfilename)
    track_graph = tfile.Get('trackPoints_master').Clone('trackPoints_master')
    track_graph.Draw("P*")
    c1.Draw()
    c1.SaveAs(args.outdir+'/mean_graph_errbars.root', 'root')
    graph_mean_sigma = ROOT.TGraphErrors(len(meanX_arr), meanX_arr, meanY_arr, zeros, zeros)
    graph_mean_sigma.SetMarkerColor(ROOT.kRed)
    graph_mean_sigma.GetXaxis().SetTitle('Mean X from fit')
    graph_mean_sigma.GetYaxis().SetTitle('Mean Y from fit')
    graph_mean_sigma.SetName('graph_mean_sigma')
    global c2
    c2 = ROOT.TCanvas("c2", "c2", 800, 600)
    graph_mean_sigma.DrawClone("AP*")
    track_graph.Draw("P*")
    c2.Draw()
    c2.SaveAs(args.outdir+'/mean_graph_noerrbars.root', 'root')
    tfile.Close()
    outfile.Write()
    outfile.Close()
    print('Selected events in ', args.outdir+'/DATATRID{0}-selected_events.root'.format(args.trid))
    if args.auto: return fine_cut_passed

def Draw2DScifiWtrack(run, ev):
    ROOT.gROOT.SetBatch(True)
    histlist = load_hists('DATA-Scifi2dHits.root')
    tfile = ROOT.TFile.Open('trackPoints_master.root')
    tgraph = tfile.Get("trackPoints_master").Clone("trackPoints_master")
    global c1
    c1 = ROOT.TCanvas("c", "c", 800, 600)
    _h = histlist['r'+str(run)+'ev'+str(ev)+'_Scifi2D_p2']
    histlist['r'+str(run)+'ev'+str(ev)+'_Scifi2D_p2'].Draw("COLZ")
    tgraph.Draw("P*")
    _h.GetXaxis().SetRangeUser(-29, -19)
    _h.GetYaxis().SetRangeUser(12, 32)
    c1.Draw()
    c1.SaveAs(str(run)+'-event_'+str(ev)+'_Scifi2d_zoom.png', 'png')

def drawLineHisto(run, ev):
    histlist = load_hists('DATA-Scifi2dHits.root')
    track_conv_pos, track_conv_angles = GetTrackPos('/afs/cern.ch/work/d/dannc/public/MuonMatching/files/linked_tracks.root', trid=476240)
    print(track_conv_pos.X(), track_conv_pos.Y())
    global c1, c2
    c1 = ROOT.TCanvas("c", "c", 800, 600)
    _hX = histlist['r'+str(run)+'ev'+str(ev)+'_Scifi_X_p2']
    xline = ROOT.TLine(track_conv_pos.X(), 0, track_conv_pos.X(), _hX.GetMaximum())
    xline.SetLineColor(ROOT.kRed)
    _hX.Draw()
    xline.Draw('SAME')
    c1.DrawClone()
    c2 = ROOT.TCanvas("c2", "c2", 800, 600)
    _hY = histlist['r'+str(run)+'ev'+str(ev)+'_Scifi_Y_p2']
    yline = ROOT.TLine(track_conv_pos.Y(), 0, track_conv_pos.Y(), _hY.GetMaximum())
    yline.SetLineColor(ROOT.kRed)
    _hY.DrawClone()
    yline.Draw('SAME')
    c2.Draw()

def drawLine2dHisto(run, ev, meanx, meany):
    histlist = load_hists(args.outdir+'/DATATRID{0}-Scifi2dHits.root'.format(args.trid))
    tfile = ROOT.TFile.Open(args.outdir+'/DATATRID{0}-Scifi2dHits.root'.format(args.trid))
    tgraph = tfile.Get("trackPoints_master").Clone("trackPoints_master")
    global c1
    tpointx, tpointy = tgraph.GetPointX(0), tgraph.GetPointY(0)
    c1 = ROOT.TCanvas("c", "c", 800, 600)
    _h = histlist['r'+str(run)+'ev'+str(ev)+'_Scifi2D_p2']
    histlist['r'+str(run)+'ev'+str(ev)+'_Scifi2D_p2'].Draw("COLZ")
    tgraph.Draw("P*")
    minx, maxx = tpointx-5, tpointx+5
    miny, maxy = tpointy-13, tpointy+13
    xline = ROOT.TLine(meanx, miny, meanx, maxy)
    xline.SetLineColor(ROOT.kRed)
    xline.SetLineWidth(2)
    xline.DrawClone()
    yline = ROOT.TLine(minx, meany, maxx, meany)
    yline.SetLineColor(ROOT.kRed)
    yline.SetLineWidth(2)
    yline.DrawClone()
    c1.Update()
    _h.GetXaxis().SetRangeUser(minx, maxx)
    _h.GetYaxis().SetRangeUser(miny, maxy)
    return c1

def GetTrackExtrap(event, z_scifi):
    if len(event.Reco_MuonTracks) < 1:
        return False
    track = event.Reco_MuonTracks.At(0)

    track_start = track.getStart()
    track_stop = track.getStop()

    slope_X = (track_stop.X() - track_start.X())/(track_stop.Z() - track_start.Z())
    slope_Y = (track_stop.Y() - track_start.Y())/(track_stop.Z() - track_start.Z())

    track_first_scifi_extrap = ROOT.TVector3(track_start.X() + slope_X*(z_scifi - track_start.Z()), track_start.Y() + slope_Y*(z_scifi - track_start.Z()), z_scifi)
    return track_first_scifi_extrap

def GetTrackParams(event):
    if len(event.Reco_MuonTracks) < 1:
        return False
    track = event.Reco_MuonTracks.At(0)

    track_start = track.getStart()
    track_stop = track.getStop()

    slope_X = (track_stop.X() - track_start.X())/(track_stop.Z() - track_start.Z())
    slope_Y = (track_stop.Y() - track_start.Y())/(track_stop.Z() - track_start.Z())

    params = {'start': track_start, 'stop':track_stop, 'TX':slope_X, 'TY':slope_Y}
    return params

def GetTrack2dHisto(run_ev_pair, plane=args.sfplane):
    ROOT.gROOT.SetBatch(True)
    tag = 'DATA'
    file = args.inputFiles[0]
    geofile = geofiles[tag]
    import rootUtils as ut
    import SndlhcGeo
    geo = SndlhcGeo.GeoInterface(geofile)
    scifiDet = ROOT.gROOT.GetListOfGlobals().FindObject('Scifi')
    muFilterDet = ROOT.gROOT.GetListOfGlobals().FindObject('MuFilter')

    isMC = False
    treeName = 'rawConv'

    ch = ROOT.TChain(treeName)
    ch.Add(file)

    if not args.trackFile: 
        try:
            trackfile = outdir+'/muEmMatching_TRID'+str(args.trid)+'_runs4575_4854_full__muonReco.root'
            os.path.exists(trackfile)
        except:
            raise Exception('No track file provided!')
    else:
        trackfile = args.trackFile
    ch_tracks = ROOT.TChain(treeName)
    ch_tracks.Add(trackfile)

    ch.AddFriend(ch_tracks)
    nevents = ch.GetEntries()
    print('N. of events:', nevents, 'track events', ch_tracks.GetEntries(), 'Tag is', tag)
    Scifiplane_path = '/cave_1/Detector_0/volTarget_1/ScifiVolume{0}_{0}000000/'.format(plane)
    scifi_or, scifi_dim = getOriginAndDims(Scifiplane_path)
    z_scifi = scifi_or['Z']
    evts = [ev[1] for ev in run_ev_pair]
    runs = [r[0] for r in run_ev_pair]
    for event in ch:
        scifiDet.InitEvent(event.EventHeader)
        muFilterDet.InitEvent(event.EventHeader)
        event_no = event.EventHeader.GetEventNumber()
        run_no = event.EventHeader.GetRunId()
        #if [run_no, event_no] not in run_ev_pair: continue
        if [run_no, event_no] in run_ev_pair:
            #if run_no != run and event_no != ievent: continue 
            track_first_scifi_extrap = GetTrackExtrap(event, z_scifi)
            if not track_first_scifi_extrap: 
                print('### WARNING ###: Track not found for pair', run_no, event_no)
                continue
            c = drawLine2dHisto(run_no, event_no, track_first_scifi_extrap.X(), track_first_scifi_extrap.Y())
            c.SaveAs(args.outdir+'/r{0}ev{1}_Scifi_2D_p{2}_withHT_trackpos.png'.format(run_no, event_no, plane), 'png')

def DrawBaricenters(trids=[]):
    tag = 'DATA'
    geofile = geofiles[tag]
    import rootUtils as ut
    import SndlhcGeo
    import numpy as np   
    import matplotlib.pyplot as plt
    from iminuit import Minuit, cost
    geo = SndlhcGeo.GeoInterface(geofile)
    scifiDet = ROOT.gROOT.GetListOfGlobals().FindObject('Scifi')
    muFilterDet = ROOT.gROOT.GetListOfGlobals().FindObject('MuFilter')
    colorlist = ([ROOT.kAzure-4, ROOT.kRed, ROOT.kGreen+1, ROOT.kViolet, ROOT.kMagenta-9, ROOT.kTeal-6, ROOT.kAzure+6, ROOT.kOrange, ROOT.kGreen-1])
    h = {}
    outfile = ROOT.TFile.Open(args.outdir+'/baricenter_graphs_selected_events.root', "RECREATE")
    h['emulsion_tracks'] = ROOT.TGraph()
    h['emulsion_tracks'].SetName('emulsion_tracks')
    h['emulsion_tracks'].SetMarkerColor(ROOT.kBlack)
    h['emulsion_tracks'].GetXaxis().SetTitle('X[cm]')
    h['emulsion_tracks'].GetYaxis().SetTitle('Y[cm]')
    global mycanvas
    mycanvas = ROOT.TCanvas("c1", "c1", 800, 600)
    mycanvas2 = ROOT.TCanvas("c2", "c2", 800, 600)
    mycanvas3 = ROOT.TCanvas("c3", "c3", 800, 600)
    for itrid, trid in enumerate(trids):
        if itrid > len(colorlist): raise Exception('No more colors available!')
        h['selected_eventsTRID'+str(trid)] = ROOT.TGraph()
        h['selected_eventsTRID'+str(trid)].SetName('selected_eventsTRID'+str(trid))
        h['selected_eventsTRID'+str(trid)].SetMarkerColor(colorlist[itrid])
        treeName = 'rawConv'
        selected_events_file = '/eos/user/d/dannc/MuonEmMatching/matchingTRID{0}/DATATRID{0}-selected_events.root'.format(trid)
        ch = ROOT.TChain(treeName)
        ch.Add(selected_events_file)
        vLeft, vRight = ROOT.TVector3(), ROOT.TVector3()
        for i_event, event in enumerate(ch):
            #if i_event > 20: break
            scifiDet.InitEvent(event.EventHeader)
            muFilterDet.InitEvent(event.EventHeader)
            event_no = event.EventHeader.GetEventNumber()
            run_no = event.EventHeader.GetRunId()
            wavg_sf_x, wavg_sf_y = getWAvgScifiPos(event, scifiDet)
            h['selected_eventsTRID'+str(trid)].SetPoint(h['selected_eventsTRID'+str(trid)].GetN(), wavg_sf_x[args.sfplane], wavg_sf_y[args.sfplane])
            h['selected_eventsTRID'+str(trid)].GetXaxis().SetRangeUser(-27, 7)
            h['selected_eventsTRID'+str(trid)].GetXaxis().SetTitle('X[cm]')
            h['selected_eventsTRID'+str(trid)].GetYaxis().SetRangeUser(15, 35)
            h['selected_eventsTRID'+str(trid)].GetYaxis().SetTitle('Y[cm]')
        outfile.cd()
        h['selected_eventsTRID'+str(trid)].Write()
        residuals_file = ROOT.TFile.Open('/eos/user/d/dannc/MuonEmMatching/matchingTRID{0}/DATATRID{0}-residuals_selected_events.root'.format(trid))
        h['trid{0}_residualTX'.format(trid)] = residuals_file.Get('trid{0}_residualTX'.format(trid)).Clone()
        h['trid{0}_residualTX'.format(trid)].SetLineColor(colorlist[itrid])
        h['trid{0}_residualTY'.format(trid)] = residuals_file.Get('trid{0}_residualTY'.format(trid)).Clone()
        h['trid{0}_residualTY'.format(trid)].SetLineColor(colorlist[itrid])
        if itrid == 0:
            mycanvas.cd()
            h['selected_eventsTRID'+str(trid)].Draw("AP*")
            mycanvas2.cd()
            h['trid{0}_residualTX'.format(trid)].Draw()
            mycanvas3.cd()
            h['trid{0}_residualTY'.format(trid)].Draw()
        else:
            mycanvas.cd()
            h['selected_eventsTRID'+str(trid)].Draw("P*")
            mycanvas2.cd()
            h['trid{0}_residualTX'.format(trid)].Draw("SAMES")
            mycanvas3.cd()
            h['trid{0}_residualTY'.format(trid)].Draw("SAMES")
        track_conv_pos, track_conv_angles = GetTrackPos('/eos/experiment/sndlhc/emulsionData/2022/emureco_Napoli/RUN1/b000121/b000121.100.0.0.trk.root', trid=trid)
        h['emulsion_tracks'].SetPoint(h['emulsion_tracks'].GetN(), track_conv_pos.X(), track_conv_pos.Y())
        del ch
    outfile.cd()
    h['emulsion_tracks'].Write()
    mycanvas.cd()
    h['emulsion_tracks'].Draw("P*")
    mycanvas.Draw()
    mycanvas2.Draw()
    mycanvas3.Draw()
    outfile.Write()
    outfile.Close()

def GetResiduals(run_ev_pair, plane=args.sfplane):
    ROOT.gROOT.SetBatch(True)
    tag = 'DATA'
    file = args.inputFiles[0]
    geofile = geofiles[tag]
    import rootUtils as ut
    import SndlhcGeo
    geo = SndlhcGeo.GeoInterface(geofile)
    scifiDet = ROOT.gROOT.GetListOfGlobals().FindObject('Scifi')
    muFilterDet = ROOT.gROOT.GetListOfGlobals().FindObject('MuFilter')

    isMC = False
    treeName = 'rawConv'

    ch = ROOT.TChain(treeName)
    ch.Add(file)

    if not args.trackFile: 
        try:
            trackfile = outdir+'/muEmMatching_TRID'+str(args.trid)+'_runs4575_4854_full__muonReco.root'
            os.path.exists(trackfile)
        except:
            raise Exception('No track file provided!')
    else:
        trackfile = args.trackFile
    ch_tracks = ROOT.TChain(treeName)
    ch_tracks.Add(trackfile)
    ch.AddFriend(ch_tracks)
    nevents = ch.GetEntries()
    print('N. of events:', nevents, 'track events', ch_tracks.GetEntries(), 'Tag is', tag)
    Scifiplane_path = '/cave_1/Detector_0/volTarget_1/ScifiVolume{0}_{0}000000/'.format(plane)
    scifi_or, scifi_dim = getOriginAndDims(Scifiplane_path)
    z_scifi = scifi_or['Z']
    evts = [ev[1] for ev in run_ev_pair]
    runs = [r[0] for r in run_ev_pair]
    track_conv_pos, track_conv_angles = GetTrackPos('/eos/experiment/sndlhc/emulsionData/2022/emureco_Napoli/RUN1/b000121/b000121.100.0.0.trk.root', trid=args.trid)
    h = {}
    outfile = ROOT.TFile.Open(args.outdir+'/DATATRID{0}-residuals_selected_events.root'.format(args.trid), "RECREATE")
    ut.bookHist(h, 'trid{0}_residualTX'.format(str(args.trid)), 'Residuals TX for trid{0}'.format(str(args.trid)), 200, -0.02, 0.02)
    ut.bookHist(h, 'trid{0}_residualTY'.format(str(args.trid)), 'Residuals TY for trid{0}'.format(str(args.trid)), 200, -0.02, 0.02)

    for event in ch:
        scifiDet.InitEvent(event.EventHeader)
        muFilterDet.InitEvent(event.EventHeader)
        event_no = event.EventHeader.GetEventNumber()
        run_no = event.EventHeader.GetRunId()
        #if [run_no, event_no] not in run_ev_pair: continue
        if [run_no, event_no] in run_ev_pair:
            #if run_no != run and event_no != ievent: continue 
            track_params = GetTrackParams(event)
            if not track_params: 
                print('### WARNING ###: Track not found for pair', run_no, event_no)
                continue
            h['trid{0}_residualTX'.format(str(args.trid))].Fill(track_params['TX']-track_conv_angles.X())
            h['trid{0}_residualTY'.format(str(args.trid))].Fill(track_params['TY']-track_conv_angles.Y())
    outfile.cd()
    print('Outfile with residuals written in '+args.outdir+'/DATATRID{0}-residuals_selected_events.root'.format(args.trid))
    for _h in h.values():
        _h.Write()
    outfile.Write()
    outfile.Close()


if args.auto:
    tfname = ScifiHit2D(args.sfplane)
    run_ev_pair = UnbinnedFit(tfilename=tfname)
    print('##### RUN EV PAIR', run_ev_pair)
    GetTrack2dHisto(run_ev_pair)
    GetResiduals(run_ev_pair)
    # Add 2dEventDisplay of run_ev_pair
