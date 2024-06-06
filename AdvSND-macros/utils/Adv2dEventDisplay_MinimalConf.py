import sys
from array import array

import ROOT
import rootUtils as ut
import os
import time
from datetime import date

#import SNDLHCstyle as snd

start_time = time.time()
today = date.today().strftime('%d%m%y')
"""
2-D Event display for AdvSND experiment

Usage: it has been tested by providing input file, geofile and event number,
it should still work in case of importing from external script and launching
the function EventDisplay which does all the job.

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
  ROOT.gStyle.SetPadTopMargin(0.05)
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
  ROOT.gStyle.SetTitleYOffset(0.7)
  

  # For the axis labels:
  
  ROOT.gStyle.SetLabelColor(1, "XYZ")
  ROOT.gStyle.SetLabelFont(42, "XYZ")
  ROOT.gStyle.SetLabelOffset(0.009, "XYZ")
  ROOT.gStyle.SetLabelSize(0.06, "XYZ")
  

  # For the axis:

  ROOT.gStyle.SetAxisColor(1, "XYZ")
  ROOT.gStyle.SetStripDecimals(True)
  ROOT.gStyle.SetTickLength(0.02, "XYZ")
  ROOT.gStyle.SetNdivisions(510, "XYZ")
  ROOT.gStyle.SetPadTickX(1)  # To get tick marks on the opposite side of the frame
  ROOT.gStyle.SetPadTickY(1)
  

  # Change for log plots:
  #ROOT.gStyle.SetOptLogx(0)
  #ROOT.gStyle.SetOptLogy(0)
  #ROOT.gStyle.SetOptLogz(0)

  #Legend options:
  ROOT.gStyle.SetLegendBorderSize(0)
  ROOT.gStyle.SetLegendTextSize(0.022)

  # Postscript options:
  #ROOT.gStyle.SetPaperSize(20.,26.)
  #ROOT.gStyle.SetHatchesLineWidth(5)
  #ROOT.gStyle.SetHatchesSpacing(0.05)

def isVertical(station):
    if not station%2: return True # Even station number is VERTICAL
    else: return False # Odd station number is HORIZONTAL

def writeSND(pad,
  text_factor=0.9,
  text_offset=0.01,
  extratext=None,
  text_in=True,
  rfrac=0.,
  maintext='SND@LHC'):

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
  return

def checkGeoVersion(geo):
    vol_list = geo.GetListOfVolumes()
    pylist = list()
    for i in range(vol_list.GetEntries()):
        vol = vol_list.At(i)
        pylist.append(vol.GetName())
    if 'volDownstreamMagnet' in pylist: return 1
    else: return 2
def GetIronCoreLines():
    nodes = ['volAdvMuFilter_0/volDownstreamMagnet_0/volDownVertCoil1_0', 'volAdvMuFilter_0/volDownstreamMagnet_0/volDownVertCoil2_0']
    IC_lines = {'X': {}, 'Y': {}}
    proj = {'X':0, 'Y':1}
    for node_ in nodes:
        node = '/cave_1/Detector_0/'+node_
        nav.cd(node)
        for p in proj:
            N = nav.GetCurrentNode()
            S = N.GetVolume().GetShape()
            dx,dy,dz = S.GetDX(),S.GetDY(),S.GetDZ()
            ox,oy,oz = S.GetOrigin()[0],S.GetOrigin()[1],S.GetOrigin()[2]
            P = {}
            M = {}
            if p=='X':
                P['LeftBottom'] = array('d',[-dx+ox,oy,-dz+oz])
                P['LeftTop'] = array('d',[dx+ox,oy,-dz+oz])
                P['RightBottom'] = array('d',[-dx+ox,oy,dz+oz])
                P['RightTop'] = array('d',[dx+ox,oy,dz+oz])
            elif p=='Y':
                P['LeftBottom'] = array('d',[ox,-dy+oy,-dz+oz])
                P['LeftTop'] = array('d',[ox,dy+oy,-dz+oz])
                P['RightBottom'] = array('d',[ox,-dy+oy,dz+oz])
                P['RightTop'] = array('d',[ox,dy+oy,dz+oz])
            else: continue
            for C in P:
                M[C] = array('d',[0,0,0])
                nav.LocalToMaster(P[C],M[C])
            if node_ == 'volAdvMuFilter_0/volDownstreamMagnet_0/volDownVertCoil1_0':
                IC_lines[p]['LeftBottom'] = M['RightBottom']
                IC_lines[p]['LeftTop'] = M['RightTop']
            if node_ == 'volAdvMuFilter_0/volDownstreamMagnet_0/volDownVertCoil2_0':
                IC_lines[p]['RightBottom'] = M['LeftBottom']
                IC_lines[p]['RightTop'] = M['LeftTop']
    return IC_lines



from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument("-f", "--inputFile", dest="inputFile", help="input file",default="",required=False)
parser.add_argument("-o", "--outPath", dest="outPath", help="output path",default=".",required=False)
parser.add_argument("-g", "--geoFile", dest="geoFile", help="geofile", required=False)
parser.add_argument("-n", "--event", dest="eventno", help="event number", type=int, required=False)
parser.add_argument("--save", dest="savefile", required=False, action='store_true', default=False)
options = parser.parse_args()

h={}
muon = {}
A,B = ROOT.TVector3(),ROOT.TVector3()
init_style()

try:
    n = options.eventno
    geo = ROOT.gGeoManager.Import(options.geoFile)
    nav = ROOT.gGeoManager.GetCurrentNavigator()
except: pass

colTargetWall = ROOT.kRed
canvxmin, canvxmax  = -80, 80.
canvymin, canvymax  = -100.,100.
canvzmnin, canvzmax =  -250.374635,450.

eventTree = None
if options.inputFile:
    f=ROOT.TFile.Open(options.inputFile)
    eventTree = f.cbmsim

outpath = options.outPath

def drawDetectors(nav=None):
    nodes = {}
    geoVer = checkGeoVersion(geo)
    print('Geometry version detected: ', geoVer)
    """for i in range(100):
        nodes['volAdvTarget_1/volTargetWall_{}'.format(i)] = ROOT.kRed
        nodes['volAdvTarget_1/TrackingStation_{}'.format(i)] = ROOT.kGray-2"""
    nodes['volAdvTarget_1'] = ROOT.kGray+1
    for i in range(22):
        nodes['volAdvMuFilter_0/volFeWall_{}'.format(i)] = ROOT.kGreen -2
        if i > 20: continue
        for j in range(20):
            if geoVer == 1:
                nodes['volAdvMuFilter_0/volMuonSysDet_{}_{}/volBar_{}'.format(i, i, i*100+j)] = ROOT.kGray
            elif geoVer == 2:
                nodes['volAdvMuFilter_0/volMuonSysDet_{}'.format(i)] = ROOT.kGray
    for i in range(2):
        nodes['volAdvMuFilter_0/volVertCoil_{}'.format(i)] = ROOT.kOrange+1
        nodes['volAdvMuFilter_0/volCoil_{}'.format(i)] = ROOT.kOrange+1
    if geoVer != 2:
        nodes['volAdvMuFilter_0/volMagTracker1_10000'] = ROOT.kGray   
        nodes['volAdvMuFilter_0/volMagTracker2_10001'] = ROOT.kGray  
        nodes['volAdvMuFilter_0/volDownMagTracker_10002'] = ROOT.kGray
        nodes['volAdvMuFilter_0/volDownstreamMagnet_0/volDownVertCoil1_0'] = ROOT.kOrange+1
        nodes['volAdvMuFilter_0/volDownstreamMagnet_0/volDownVertCoil2_0'] = ROOT.kOrange+1
        nodes['volAdvMuFilter_0/volDownstreamMagnet_0/volIronYoke_0'] = ROOT.kGreen-2
        nodes['volAdvMuFilter_0/volDownstreamMagnet_0/volDownCoil_20000'] = ROOT.kOrange+1
        nodes['volAdvMuFilter_0/volDownstreamMagnet_0/volIronCore_0'] = ROOT.kGreen+3
        IC_lines = GetIronCoreLines()

    passNodes = {'Block', 'Wall', 'Coil', 'Yoke', 'Tracker', 'Core', 'Target'}
    #passNodes = {}
    proj = {'X':0, 'Y':1}
    for node_ in nodes:
        node = '/cave_1/Detector_0/'+node_
        for p in proj:
            if node+p in h and any(passNode in node for passNode in passNodes):
                X = h[node+p]
                c = proj[p]
                h['simpleDisplay'].cd(c+1)
                X.Draw('f&&same')
                X.Draw('same')
            else:
                try: nav.cd(node)
                except: continue
                N = nav.GetCurrentNode()
                S = N.GetVolume().GetShape()
                dx,dy,dz = S.GetDX(),S.GetDY(),S.GetDZ()
                ox,oy,oz = S.GetOrigin()[0],S.GetOrigin()[1],S.GetOrigin()[2]
                P = {}
                M = {}
                if p=='X':
                    P['LeftBottom'] = array('d',[-dx+ox,oy,-dz+oz])
                    P['LeftTop'] = array('d',[dx+ox,oy,-dz+oz])
                    P['RightBottom'] = array('d',[-dx+ox,oy,dz+oz])
                    P['RightTop'] = array('d',[dx+ox,oy,dz+oz])
                elif p=='Y':
                    P['LeftBottom'] = array('d',[ox,-dy+oy,-dz+oz])
                    P['LeftTop'] = array('d',[ox,dy+oy,-dz+oz])
                    P['RightBottom'] = array('d',[ox,-dy+oy,dz+oz])
                    P['RightTop'] = array('d',[ox,dy+oy,dz+oz])
                else: continue
                for C in P:
                    M[C] = array('d',[0,0,0])
                    nav.LocalToMaster(P[C],M[C])
                h[node+p] = ROOT.TPolyLine()
                X = h[node+p]
                c = proj[p]
                if node == '/cave_1/Detector_0/volAdvMuFilter_0/volDownstreamMagnet_0/volIronCore_0':
                    X.SetPoint(0,M['LeftBottom'][2],IC_lines[p]['LeftBottom'][c])
                    X.SetPoint(1,M['LeftTop'][2],IC_lines[p]['LeftTop'][c])
                    X.SetPoint(2,M['RightTop'][2],IC_lines[p]['RightTop'][c])
                    X.SetPoint(3,M['RightBottom'][2],IC_lines[p]['RightBottom'][c])
                    X.SetPoint(4,M['LeftBottom'][2],IC_lines[p]['LeftBottom'][c])
                elif node == '/cave_1/Detector_0/volAdvMuFilter_0/volDownstreamMagnet_0/volDownCoil_20000' and p == 'Y':
                    X.SetPoint(0,M['LeftBottom'][2],IC_lines[p]['LeftBottom'][c]-7.)
                    X.SetPoint(1,M['LeftTop'][2],IC_lines[p]['LeftTop'][c]+7.)
                    X.SetPoint(2,M['RightTop'][2],IC_lines[p]['RightTop'][c]+7.)
                    X.SetPoint(3,M['RightBottom'][2],IC_lines[p]['RightBottom'][c]-7.)
                    X.SetPoint(4,M['LeftBottom'][2],IC_lines[p]['LeftBottom'][c]-7.)
                else:
                    X.SetPoint(0,M['LeftBottom'][2],M['LeftBottom'][c])
                    X.SetPoint(1,M['LeftTop'][2],M['LeftTop'][c])
                    X.SetPoint(2,M['RightTop'][2],M['RightTop'][c])
                    X.SetPoint(3,M['RightBottom'][2],M['RightBottom'][c])
                    X.SetPoint(4,M['LeftBottom'][2],M['LeftBottom'][c])
                X.SetLineColor(nodes[node_])
                X.SetLineWidth(1)
                h['simpleDisplay'].cd(c+1)
                if any(passNode in node for passNode in passNodes):
                    if p == 'X' and 'Coil' in node_: 
                        X.Draw('same')
                        continue
                    X.SetFillColorAlpha(nodes[node_], 0.5)
                    X.Draw('f&&same')
                else:X.Draw('same')

def drawInfo(pad, 
            k, 
            event,
            extratext=None):

    text_offset=0.05
    padText = ROOT.TPad("info","info",0.13,0.02,0.6,0.3)
    padText.SetFillStyle(4000)
    padText.Draw()
    padText.cd()
    t = pad.GetTopMargin()
    SNDTextSize = 0.15
    SNDTextVerticalOffset = text_offset
    
    latex = ROOT.TLatex()
    latex.SetNDC()
    latex.SetTextAngle(0)
    latex.SetTextColor(ROOT.kBlack)
    latex.SetTextFont(61)
    latex.SetTextAlign(11)
    latex.SetTextSize(SNDTextSize)
    latex.SetText(0,0,'AdvSND')
    latex.DrawLatex(0, 1-t-SNDTextVerticalOffset-1.2*SNDTextSize, 'AdvSND')
    extraTextSize = SNDTextSize*0.8
    latex.SetTextFont(52)
    latex.SetTextSize(extraTextSize)
    latex.SetTextAlign(11)
    latex.DrawLatex(0, 1-t-SNDTextVerticalOffset-2.2*SNDTextSize, extratext)
    latex.SetTextFont(42)
    latex.SetTextSize(extraTextSize*0.9)
    N = event
    latex.DrawLatex(0, 1-t-SNDTextVerticalOffset-3.2*SNDTextSize, 'Event: '+str(N))
    pad.cd(k)

def EventDisplay(n=0, save=False, eventTree=eventTree, nav=nav, followmuon=False):
    if 'simpleDisplay' not in h: ut.bookCanvas(h,key='simpleDisplay',title='simple event display',nx=1200,ny=int(0.70*1200),cx=1,cy=2)
    h['simpleDisplay'].cd(1)
    zStart = -236.374635
    geoVer = checkGeoVersion(geo)
    if geoVer == 2: 
        canvzmax = 200
        canvymin, canvymax = -80., 80
    if 'xz' in h: 
        h.pop('xz').Delete()
        h.pop('yz').Delete()
    else:
        h['xmin'],h['xmax'] = canvxmin, canvxmax
        h['ymin'],h['ymax'] = canvymin, canvymax
        h['zmin'],h['zmax'] = canvzmnin, canvzmax
        for d in ['xmin','xmax','ymin','ymax','zmin','zmax']: h['c'+d]=h[d]
    ut.bookHist(h,'xz','; z [cm]; x [cm]',500,h['czmin'],h['czmax'],100,h['cxmin'],h['cxmax'])
    ut.bookHist(h,'yz','; z [cm]; y [cm]',500,h['czmin'],h['czmax'],100,h['cymin'],h['cymax'])
    proj = {1:'xz',2:'yz'}
    h['xz'].SetStats(0)
    h['yz'].SetStats(0)

    event = eventTree
    rc = event.GetEvent(n)
    branches = []
    nMCTracks = len(event.MCTrack)
    if event.FindBranch("AdvTargetPoint"): branches.append(event.AdvTargetPoint)
    if event.FindBranch("AdvMuFilterPoint"): branches.append(event.AdvMuFilterPoint)
    # add support for possible MagnetPoint class
    empty = True
    for x in branches:
        if len(x)>0:
            if empty: print("event -> %i"%n)
            empty = False
    if empty: 
        #raise Exception('Warning branch empty!')
        print('Branch empty')
    h['hitCollectionX'] = {'AdvTarget': [0, ROOT.TGraphErrors()], 'AdvMuFilter': [0, ROOT.TGraphErrors()]}
    h['hitCollectionY'] = {'AdvTarget': [0, ROOT.TGraphErrors()], 'AdvMuFilter': [0, ROOT.TGraphErrors()]}
    if followmuon:
        muon['hitCollectionX'] = {'AdvTarget': [0, ROOT.TGraphErrors()], 'AdvMuFilter': [0, ROOT.TGraphErrors()]}
        muon['hitCollectionY'] = {'AdvTarget': [0, ROOT.TGraphErrors()], 'AdvMuFilter': [0, ROOT.TGraphErrors()]}
    systems = {1: 'AdvTarget', 2: 'AdvMuFilter'}
    for collection in ['hitCollectionX', 'hitCollectionY']:
        for c in h[collection]:
            rc=h[collection][c][1].SetName(c)
            rc=h[collection][c][1].Set(0)
            rc=h[collection][c][1].SetMarkerColor(ROOT.kBlack)
            if followmuon:
                rc=muon[collection][c][1].SetName(c)
                rc=muon[collection][c][1].Set(0)
                rc=muon[collection][c][1].SetMarkerColor(ROOT.kBlue)
    for p in proj:
        rc = h['simpleDisplay'].cd(p)
        h[proj[p]].Draw('b')
    
    drawDetectors(nav=nav)
    for B in branches:
        trkMem = -1000
        statMem = -1000
        for b in B:
            isMuon = False
            z = b.GetZ()
            pdgcode = b.PdgCode()
            trkID = b.GetTrackID()
            if trkID > nMCTracks: continue
            if trkID < 0: continue
            if ROOT.TMath.Abs(pdgcode) == 13 and (trkID == 1 or trkID == 0 or event.MCTrack[trkID].GetMotherId() == 1): isMuon = True
            if b.GetName() =='AdvTargetPoint': system = 1
            else: system = 2
            """if system == 2: station = int(b.GetDetectorID()/100)
            else: station = b.GetDetectorID()
            if station == statMem and trkID == trkMem: continue"""
            station = b.GetDetectorID()
            #if trkID == 0 and ROOT.TMath.Abs(pdgcode) == 13: outpath = '/eos/home-d/dannc/AdvSND/plots/EvDisplays/PassingMu/'+str(today)+'/'
            #else: outpath = '/eos/home-d/dannc/AdvSND/plots/EvDisplays/Neutrino/'+str(today)+'/'    TO BE FIXED
            for collection in ['hitCollectionX', 'hitCollectionY']:
                if collection == 'hitCollectionX': coord = b.GetX()
                else: coord = b.GetY()
                c = h[collection][systems[system]]
                if not isMuon:
                    rc = c[1].SetPoint(c[0], z, coord)
                c[0]+=1
                if followmuon and isMuon:
                    muc = muon[collection][systems[system]]
                    rc = muc[1].SetPoint(muc[0], z, coord)
                    muc[0]+=1
            trkMem = trkID
            statMem = station
    k = 1
    for collection in ['hitCollectionX', 'hitCollectionY']:
        h['simpleDisplay'].cd(k)
        drawInfo(h['simpleDisplay'], k=k, event=n, extratext='Simulation')
        k+=1
        for c in h[collection]:
            if h[collection][c][1].GetN()<1: continue
            h[collection][c][1].SetMarkerStyle(21)
            h[collection][c][1].SetMarkerSize(0.5)
            rc=h[collection][c][1].Draw('sameP')
            h['display:'+c]=h[collection][c][1]
        if followmuon:
            for muc in muon[collection]:
                if  muon[collection][muc][1].GetN()<1: continue
                muon[collection][muc][1].SetMarkerStyle(21)
                muon[collection][muc][1].SetMarkerSize(0.5)
                murc=muon[collection][muc][1].Draw('sameP')
                muon['display:'+c]=muon[collection][muc][1]
    h['simpleDisplay'].Update()
    if save:
        if not os.path.exists(outpath): os.makedirs(outpath)
        h['simpleDisplay'].SaveAs(outpath+'AdvSNDEventDisplay-event_{:04d}'.format(n)+'.png', 'png') 

if options.eventno and options.inputFile:
    EventDisplay(n=options.eventno, eventTree=eventTree, nav=nav, followmuon=True, save=options.savefile)

# Things to do:
#   - add support for old layout

def checkDetectors():
    ut.bookCanvas(h,key='simpleDisplay',title='simple event display',nx=1200,ny=1600,cx=1,cy=2)
    h['simpleDisplay'].cd(1)
    if checkGeoVersion(geo) == 2: 
        canvzmax = 200
        canvymin, canvymax = -80., 80
    if 'xz' in h: 
        h.pop('xz').Delete()
        h.pop('yz').Delete()
    else:
        h['xmin'],h['xmax'] = canvxmin, canvxmax
        h['ymin'],h['ymax'] = canvymin, canvymax
        h['zmin'],h['zmax'] = canvzmnin, canvzmax
        for d in ['xmin','xmax','ymin','ymax','zmin','zmax']: h['c'+d]=h[d]
    ut.bookHist(h,'xz','; z [cm]; x [cm]',500,h['czmin'],h['czmax'],100,h['cxmin'],h['cxmax'])
    ut.bookHist(h,'yz','; z [cm]; y [cm]',500,h['czmin'],h['czmax'],100,h['cymin'],h['cymax'])
    proj = {1:'xz',2:'yz'}
    h['xz'].SetStats(0)
    h['yz'].SetStats(0)
    for p in proj:
        rc = h['simpleDisplay'].cd(p)
        h[proj[p]].Draw('b')
    drawDetectors(nav=nav)