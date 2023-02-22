import ROOT
import rootUtils as ut
from array import array
import sys
sys.path.append('/eos/user/d/dannc/Utils')
import SNDLHCstyle as snd
from datetime import date
import time
import os
start_time = time.time()
today = date.today().strftime('%d%m%y')
"""
2-D Event display for AdvSND experiment

Usage: it has been tested by providing input file, geofile and event number,
it should still work in case of importing from external script and launching
the function EventDisplay which does all the job.

"""
def checkGeoVersion(geo):
    vol_list = geo.GetListOfVolumes()
    pylist = list()
    for i in range(vol_list.GetEntries()):
        vol = vol_list.At(i)
        pylist.append(vol.GetName())
    if 'SensorModule' in pylist: return 2
    elif 'volMFWall' in pylist: return 0
    else: return 1

from argparse import ArgumentParser
parser = ArgumentParser()
parser.add_argument("-f", "--inputFile", dest="inputFile", help="input file",default="",required=False)
parser.add_argument("-o", "--outPath", dest="outPath", help="output path",default="",required=False)
parser.add_argument("-g", "--geoFile", dest="geoFile", help="geofile", required=False)
parser.add_argument("-n", "--event", dest="eventno", help="event number", type=int, required=False)
parser.add_argument("--save", dest="savefile", required=False, action='store_true', default=False)
options = parser.parse_args()

h={}
muon = {}
A,B = ROOT.TVector3(),ROOT.TVector3()
snd.init_style()

try:
    n = options.eventno
    geo = ROOT.gGeoManager.Import(options.geoFile)
    nav = ROOT.gGeoManager.GetCurrentNavigator()
except: pass

if geo:
    version = checkGeoVersion(geo=geo)
    print('Found geometry version: ', version)

if version == 2: colTargetWall = ROOT.kRed

else: colTargetWall = ROOT.kYellow

canvxmin, canvxmax = -100, 100.
if version > 1: canvxmin, canvxmax = -100, 40.
    
if options.inputFile:
    f=ROOT.TFile.Open(options.inputFile)
    eventTree = f.cbmsim

outpath = options.outPath

def drawDetectors(nav=None):
    nodes = {}
    if version != 0:
        for i in range(42):
            nodes['volAdvMuFilter_0/volFeWall_{}'.format(i)] = ROOT.kGreen-2
            if i<21:
                nodes['volAdvMuFilter_0/volMuonSysDet_{}'.format(i)] = ROOT.kGray-2
        for i in range(3):
            nodes['volAdvMuFilter_0/volMagTracker_{}'.format(1000+i)] = ROOT.kGray+1
        for i in range(2):
            nodes['volAdvMuFilter_0/volCoil_{}'.format(i)] = ROOT.kOrange+1
            nodes['volAdvMuFilter_0/volShortCoil_{}'.format(i)] = ROOT.kOrange+1
        for i in range(40):
            if version == 1 and i<5: 
                nodes['volAdvTarget_1/volTTracker_{}'.format(i)] = ROOT.kGray+1
                nodes['volAdvTarget_1/volTargetWall_{}'.format(i)] = ROOT.kYellow
            if version == 2 : 
                nodes['volAdvTarget_1/TrackingStation_{}'.format(i)] = ROOT.kGray+1
                nodes['volAdvTarget_1/volTargetWall_{}'.format(i)] = ROOT.kRed

    else:
        for i in range(5):
            nodes['volAdvTarget_1/volTargetWall_{}'.format(i)] = ROOT.kYellow
            nodes['volAdvTarget_1/volTTracker_{}'.format(i)] = ROOT.kGray+1
        for i in range(22):
            nodes['volAdvMuFilter_1/volMFWall_{}'.format(i)] = ROOT.kGreen-2
            if i<21:
                nodes['volAdvMuFilter_1/volMFPlane_{}'.format(i)] = ROOT.kGray+1
        for i in range(4):
            nodes['Magnet_0/volTrackPlane_{}'.format(i)] = ROOT.kGray+1
        nodes['Magnet_0/volCoil_0'] = ROOT.kOrange+1
        nodes['Magnet_0/volCoil_1'] = ROOT.kOrange+1
        nodes['Magnet_0/volFeYoke_0'] = ROOT.kGray+1
    
    passNodes = {'Block', 'Wall', 'Coil'}
    proj = {'X':0, 'Y':1}
    for node_ in nodes:
        node = '/cave_1/Detector_0/'+node_
        for p in proj:
            if node+p in h and any(passNode in node for passNode in passNodes):
                X = h[node+p]
                c = proj[p]
                h['simpleDisplay'].cd(c+1)
                #X.Draw('f&&same')
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
    if 'simpleDisplay' not in h: ut.bookCanvas(h,key='simpleDisplay',title='simple event display',nx=1200,ny=1600,cx=1,cy=2)
    h['simpleDisplay'].cd(1)
    zStart = -171.681619
    if 'xz' in h: 
        h.pop('xz').Delete()
        h.pop('yz').Delete()
    else:
        h['xmin'],h['xmax'] = canvxmin, canvxmax
        h['ymin'],h['ymax'] = -40.,103.
        h['zmin'],h['zmax'] = zStart,500.
        for d in ['xmin','xmax','ymin','ymax','zmin','zmax']: h['c'+d]=h[d]
    ut.bookHist(h,'xz','; z [cm]; x [cm]',500,h['czmin'],h['czmax'],100,h['cxmin'],h['cxmax'])
    ut.bookHist(h,'yz','; z [cm]; y [cm]',500,h['czmin'],h['czmax'],100,h['cymin'],h['cymax'])
    proj = {1:'xz',2:'yz'}
    h['xz'].SetStats(0)
    h['yz'].SetStats(0)

    event = eventTree
    rc = event.GetEvent(n)
    branches = []
    if event.FindBranch("AdvTargetPoint"): branches.append(event.AdvTargetPoint)
    if event.FindBranch("AdvMuFilterPoint"): branches.append(event.AdvMuFilterPoint)
    # add support for possible MagnetPoint class
    empty = True
    for x in branches:
        if x.GetEntries()>0:
            if empty: print("event -> %i"%n)
            empty = False
    if empty: raise Exception('Warning branch empty!')
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
            if trkID < 0: continue
            if ROOT.TMath.Abs(pdgcode) == 13 and (trkID == 1 or trkID == 0 or event.MCTrack[trkID].GetMotherId() == 1): isMuon = True
            if b.GetName() =='AdvTargetPoint': system = 1
            else: system = 2
            if system == 1 and version == 2: station = ROOT.floor(b.GetDetectorID()/10000)
            else: station = b.GetDetectorID()
            if station == statMem and trkID == trkMem: continue
            #if trkID == 0 and ROOT.TMath.Abs(pdgcode) == 13: outpath = '/eos/home-d/dannc/AdvSND/plots/EvDisplays/PassingMu/'+str(today)+'/'
            #else: outpath = '/eos/home-d/dannc/AdvSND/plots/EvDisplays/Neutrino/'+str(today)+'/'    TO BE FIXED
            for collection in ['hitCollectionX', 'hitCollectionY']:
                if collection == 'hitCollectionX': coord = b.GetX()
                else: coord = b.GetY()
                c = h[collection][systems[system]]
                if not isMuon: rc = c[1].SetPoint(c[0], z, coord)
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
    zStart = -171.681619
    if 'xz' in h: 
        h.pop('xz').Delete()
        h.pop('yz').Delete()
    else:
        h['xmin'],h['xmax'] = canvxmin, canvxmax
        h['ymin'],h['ymax'] = -40.,103.
        h['zmin'],h['zmax'] = zStart,500.
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