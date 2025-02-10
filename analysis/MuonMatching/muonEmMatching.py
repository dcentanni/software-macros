import os
# Code snippet from Simona. This should go somewhere where it can be used by several different pieces of code (monitoring, analysis, etc)
import pickle

import numpy as np
import ROOT
import rootUtils as ut
import SndlhcGeo
from array import array

def isInTimeRange(hit_time, time_low, time_up):
    if hit_time > time_low and hit_time <= time_up: return True
    else: return False

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

def GetAvgScifiPos(DigiScifiHits):
    n_sf_hits_x = [0]*5
    n_sf_hits_y = [0]*5
    avg_sf_x = [0.]*5
    avg_sf_y = [0.]*5
    a, b = ROOT.TVector3(), ROOT.TVector3()
    for hit in DigiScifiHits :
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

def getScifiHitCollections(DigiScifiHits):
    Scifi_HitCollectionX = {1:[], 2:[], 3:[], 4:[], 5:[]}
    Scifi_HitCollectionY = {1:[], 2:[], 3:[], 4:[], 5:[]}
    vLeft, vRight = ROOT.TVector3(), ROOT.TVector3()
    for aHit in DigiScifiHits:
        if not aHit.isValid(): continue
        station = aHit.GetStation()
        detID = aHit.GetDetectorID()
        scifiDet.GetSiPMPosition(detID, vLeft, vRight)
        if aHit.isVertical():
            Scifi_HitCollectionX[station].append(vLeft.X())
        else:
            Scifi_HitCollectionY[station].append(vRight.Y())
    return Scifi_HitCollectionX, Scifi_HitCollectionY

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

def CorrectScifi(event):
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
  return Nsf_corr, Nsf, nsf_statID_corr, nsf_statID

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

def GetVetoBar(detID):
    
    plane = int((detID/1000)%10)
    bar = int((detID%10000)%1000)
    return plane, bar

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

import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-f", dest = "inputFile", required = False)
parser.add_argument("-o", dest = "outputFile", required = False)
parser.add_argument("-g", dest = "geoFile", required = False)
parser.add_argument("-r", dest = "run", required = False)
parser.add_argument("-d", dest = "dir", default='./', required = False)
parser.add_argument("--trid", dest = "trid", required = False)
args = parser.parse_args()

geofiles    = {'2022': '/afs/cern.ch/work/d/dannc/public/MuonMatching/files/geofile_sndlhc_TI18_2022_NagoyaEmu.root',
               '2023': '/eos/experiment/sndlhc/convertedData/physics/2023/geofile_sndlhc_TI18_V3_2023.root'}

# Set up TTrees
treeName = "rawConv"
TDC2ns = 1E9/160.316E6
ch = ROOT.TChain(treeName)
ch.Add(args.inputFile)

if ch.GetEntries() == 0 :
    print("Chain is empty. Exitting")
    exit(-1)

if not args.geoFile:
	rindex = args.inputFile.find('run')
	run = args.inputFile[rindex+6:rindex+10]
	year=''
	if int(run) < 5562: year='2022'
	else: year='2023'
	geoFile = geofiles[year]
	print('Input geoFile not provided, using', geoFile)
else:
    geoFile = args.geoFile

if not args.trid:
    trid = 476240
else:
    trid = args.trid

snd_geo = SndlhcGeo.GeoInterface(geoFile)
scifiDet = ROOT.gROOT.GetListOfGlobals().FindObject('Scifi')
muFilterDet = ROOT.gROOT.GetListOfGlobals().FindObject('MuFilter')

scifi2Vert_geopath = '/cave_1/Detector_0/volTarget_1/ScifiVolume2_2000000/ScifiVertPlaneVol2_2000000'
scifi2Hor_geopath = '/cave_1/Detector_0/volTarget_1/ScifiVolume2_2000000/ScifiVertPlaneVol2_2000000'

scifi2Vert_or, scifi2Vert_dim = getOriginAndDims(scifi2Vert_geopath)
scifi2Hor_or, scifi2Hor_dim = getOriginAndDims(scifi2Hor_geopath)

#track_conv_pos, track_conv_angles = GetTrackPos('/afs/cern.ch/work/d/dannc/public/MuonMatching/files/linked_tracks.root', trid=trid)
track_conv_pos, track_conv_angles = GetTrackPos('/eos/experiment/sndlhc/emulsionData/2022/emureco_Napoli/RUN1/b000121/b000121.100.0.0.trk.root', trid=trid)

print('Primary track found in', track_conv_pos.X(), track_conv_pos.Y(), track_conv_pos.Z())

isMC = False

# Set up cuts
cuts = []
################################################################################
# Single Veto bar per plane fired
################################################################################
def VetoFired(event):
    VetoBarFired    = {0: list(), 1: list()}
    ret = False
    value = -1
    for aHit in event.Digi_MuFilterHits:
        if aHit.GetSystem()!=1: continue
        plane, bar = GetVetoBar(aHit.GetDetectorID())
        VetoBarFired[plane].append(bar)
        ret = True
        value = len(VetoBarFired[plane])
        return ret, value
    return ret, value
cuts.append(["Ask for at least 1 Veto Hit", VetoFired, "VetoFired", 3, -0.5, 2.5])
################################################################################
# Single Cluster in Scifi 1
################################################################################
uptoiplane = 1
def SingleScifiCluster(event):
    NsfClPl_H       =  {1:0, 2:0, 3:0, 4:0, 5:0}
    NsfClPl_V       =  {1:0, 2:0, 3:0, 4:0, 5:0}
    Nsfcl= 0
    DATA_scifiCluster = scifiCluster(event.Digi_ScifiHits, scifiDet)
    for aCl in DATA_scifiCluster:
        detID = aCl.GetFirst()
        Nsfcl+=1
        station = int(detID/1e+6)
        if int(detID/100000)%10 == 1: 
            NsfClPl_V[int(detID/1e+6)]+=1
        else:
            NsfClPl_H[int(detID/1e+6)]+=1
    ret = True
    value = Nsfcl
    for key in NsfClPl_H.keys():
        if key > uptoiplane: continue
        if NsfClPl_H[key] > 1 or NsfClPl_V[key] > 1:
            ret = False
    return ret, value
cuts.append(["Single H/V Cluster in first {0} Scifi planes".format(uptoiplane), SingleScifiCluster, "SingleSFClusters", 20, 0, 20])
################################################################################
# Scifi 1 avg position in a X cm area around the muon track
################################################################################
scifiplane=1
area_dim = 1 #cm
def ScifiAvgPos(event):
    avg_sf_x, avg_sf_y = getWAvgScifiPos(event, scifiDet)
    #print(avg_sf_x[scifiplane], avg_sf_y[scifiplane])
    ret = False
    value = avg_sf_x[scifiplane]
    if ROOT.TMath.Abs(avg_sf_x[scifiplane]-track_conv_pos.X())< area_dim/2. and ROOT.TMath.Abs(avg_sf_y[scifiplane]-track_conv_pos.Y()) < area_dim/2.:
        #print('scifi hit', avg_sf_x[scifiplane], avg_sf_y[scifiplane], 'track pos', track_conv_pos.X(), track_conv_pos.Y())
        ret = True
    else: return False, 0
    return ret, value
cuts.append(["Scifi {0} QDC weighted avg position in a {1}x{1} cm2 area around mu track".format(scifiplane, area_dim), ScifiAvgPos, "ScifiWAvgPosMuon", 300, -30, 0])
################################################################################
# Ask for shower developing
################################################################################
clusIncrease_plane = 2
def ScifiClusIncrease(event):
    NsfClPl_H       =  {1:0, 2:0, 3:0, 4:0, 5:0}
    NsfClPl_V       =  {1:0, 2:0, 3:0, 4:0, 5:0}
    NsfClPl         = {1:0, 2:0, 3:0, 4:0, 5:0}
    Nsfcl= 0
    DATA_scifiCluster = scifiCluster(event.Digi_ScifiHits, scifiDet)
    for aCl in DATA_scifiCluster:
        detID = aCl.GetFirst()
        Nsfcl+=1
        station = int(detID/1e+6)
        NsfClPl[int(detID/1e+6)]+=1
        if int(detID/100000)%10 == 1: 
            NsfClPl_V[int(detID/1e+6)]+=1
        else:
            NsfClPl_H[int(detID/1e+6)]+=1
    ret = False
    value = NsfClPl[clusIncrease_plane]-NsfClPl[clusIncrease_plane-1]
    if NsfClPl[clusIncrease_plane] >= NsfClPl[clusIncrease_plane-1]:
        ret = True
    return ret, value
cuts.append(["Scifi {0} clusters > SciFi {1} clusters".format(clusIncrease_plane, clusIncrease_plane-1), ScifiClusIncrease, "ScifiClusIncrease", 201, -100.5,100.5])
#############################################################################
# MildShower asking 
#############################################################################
frac_thresh = 0.6
def MildShower(event):
    n_hits_corr, n_hits, nsf_statID_corr, nsf_statID = CorrectScifi(event)
    nsf_hits = {}
    nsf = None
    if not isMC:
        nsf_hits = nsf_statID_corr
        nsf = n_hits_corr
    else:
        nsf_hits = nsf_statID
        nsf = n_hits
    if not nsf: return False, 0
    ScifiFrac = {1:None, 2:None, 3:None, 4:None, 5:None}
    for detID in range(1,6):
        ScifiFrac[detID]=float(nsf_hits[detID]/nsf)
    ret = False
    value = ScifiFrac[2]
    if ScifiFrac[2] > frac_thresh: ret = True
    return ret, value
cuts.append(["ScifiFraction plane2 > than {0}".format(frac_thresh), MildShower, 'scififrac_thr', 500, 0.4, 1])
################################################################################
# Highest QDC in Scifi plane
################################################################################
max_qdc_sfplane = 2
def MaxScifiQDCplane(event):
    this_qdc = 0
    ret = False
    qdc_station = {1:0, 2:0, 3:0, 4:0, 5:0}
    for digi in event.Digi_ScifiHits:
        if not digi.isValid(): continue
        detID = digi.GetDetectorID()
        station = digi.GetStation()
        ns = max(1, digi.GetnSides())
        for side in range(ns):
            for m in range(digi.GetnSiPMs()):
                qdc = digi.GetSignal(m+side*digi.GetnSiPMs())
                if not qdc < 0 :
                    qdc_station[station] += qdc
    qdclist = list()
    for stat, _qdc in qdc_station.items():
        qdclist.append([stat, _qdc])
    maxpair = max(qdclist,key=lambda item:item[1])
    max_stat = maxpair[0]
    value = maxpair[1]
    if max_stat == max_qdc_sfplane:
        ret = True
    return ret, value
cuts.append(["Maximum Scifi QDC in plane {0}".format(max_qdc_sfplane), MaxScifiQDCplane, "MaxScifiQDCplane", 101, -1, 1000])
################################################################################
# Highest Scifi hit density in plane
################################################################################
max_dens_sfplane = 2
def MaxScifiDensplane(event):
    ret = False
    Scifi_HitCollectionX, Scifi_HitCollectionY = getScifiHitCollections(event.Digi_ScifiHits)
    Scifi_MeanDensities = list()
    for key in range(1,6):
        Scifi_MeanDensities.append([key, (getScifiHitDensity(Scifi_HitCollectionX[key])+getScifiHitDensity(Scifi_HitCollectionY[key]))/2])
    maxpair = max(Scifi_MeanDensities,key=lambda item:item[1])
    max_stat = maxpair[0]
    value = maxpair[1]
    if max_stat == max_dens_sfplane:
        ret = True
    return ret, value
cuts.append(["Maximum Scifi density in plane {0}".format(max_dens_sfplane), MaxScifiDensplane, "MaxScifiDensplane", 100, 0, 100])
################################################################################
# At least 80 SciFi hits in SF2
################################################################################
min_scifi_hits_cut = 80
def min_scifi_hits(event) :
    n_hits = 0
    n_hits_corr = 0
    ret = False
    n_hits_corr, n_hits, nsf_statID_corr, nsf_statID = CorrectScifi(event)
    if isMC:
        if nsf_statID[2] > min_scifi_hits_cut: ret = True
        return ret, nsf_statID[2]
    else:
        if nsf_statID_corr[2] > min_scifi_hits_cut: ret = True
        return ret, nsf_statID_corr[2]
cuts.append(["More than {0} SciFi hits  in Scifi 2(CORRECTED)".format(min_scifi_hits_cut), min_scifi_hits, "scifi_nhits", 100, 0, 3000])
################################################################################
# Less than 15 SciFi hits in SF4-5
################################################################################
min_scifi_hits_cut_last = 15
def min_scifi_hits_last(event) :
    n_hits = 0
    n_hits_corr = 0
    ret = False
    n_hits_corr, n_hits, nsf_statID_corr, nsf_statID = CorrectScifi(event)
    if isMC:
        if nsf_statID[4] <  min_scifi_hits_cut_last and nsf_statID[5] < min_scifi_hits_cut_last: ret = True
        return ret, (nsf_statID[4]+nsf_statID[5])
    else:
        if nsf_statID_corr[4] <  min_scifi_hits_cut_last and nsf_statID_corr[5] < min_scifi_hits_cut_last: ret = True
        return ret, (nsf_statID_corr[4]+nsf_statID_corr[5])
cuts.append(["Less than {0} SciFi hits  in Scifi 4 and 5(CORRECTED)".format(min_scifi_hits_cut_last), min_scifi_hits_last, "scifi_nhits_last", 100, 0, 3000])
################################################################################
# Min QDC
################################################################################
min_QDC_data = 600
min_QDC_MC = 700
def min_US_QDC(event) :
    US_QDC = 0
    ret = False
    for hit in event.Digi_MuFilterHits :
        if hit.GetSystem() != 2 :
            continue
        if not hit.isValid() :
            continue
        for key, value in hit.GetAllSignals() :
            US_QDC += value
            if isMC and (US_QDC > min_QDC_MC) :
                ret = True
            if (not isMC) and (US_QDC > min_QDC_data) :
                ret = True
    if isMC :
        return ret, US_QDC - 100
    else :
        return ret, US_QDC
#cuts.append(["US QDC larger than {0} ({1}) for data (MC)".format(min_QDC_data, min_QDC_MC), min_US_QDC, "US_QDC", 100, 0, 4000])
################################################################################
# Event deltacut
################################################################################
delta_e = -1
delta_t = 100
def EventDeltaCut(event):
    current_entry = ch.GetReadEntry()
    current_time = event.EventHeader.GetEventTime()
    ch.GetEntry(current_entry+delta_e)
    sign = (delta_e > 0) - (delta_e < 0)
    ret = False
    if -sign*(current_time-event.EventHeader.GetEventTime()) <= delta_t: ret = True
    value = ROOT.TMath.Abs(current_time-event.EventHeader.GetEventTime())
    ch.GetEntry(current_entry)
    return ret, value
#cuts.append(["{0} event more than {1} clock cycles away".format(delta_e, delta_t), EventDeltaCut, "EventDeltat_minus1_{1}".format(delta_e, delta_t), 1000, -1, 1000])

#### Ask for a avg scifi position weighted on the single qdc of the digi hit

################################################################################
# END CUT DEFINITONS
################################################################################
obj = {}
h = {}

ch.GetEntry(0)
f = ch.GetFile()

# Set up output file
if not args.outputFile and args.run:
    fin = args.inputFile
    output_file = ROOT.TFile(args.dir+'/TRID'+str(trid)+'_muEmMatching_run'+str(args.run)+fin[len(fin)-10:len(fin)], "RECREATE")
else:
    output_file = ROOT.TFile(args.dir+'/'+args.outputFile, "RECREATE")
output_tree = ch.CloneTree(0)
# Copy branch list
branch_list = f.Get("BranchList")
branch_list_copy = branch_list.Clone()
branch_list_copy.Write("BranchList", 1)

n_cuts = len(cuts)
ut.bookHist(h, "cutFlow", "Cut flow;;Number of events passing cut", n_cuts+1, 0, n_cuts+1)
for i in range(2, h["cutFlow"].GetNbinsX()+1):
    h["cutFlow"].GetXaxis().SetBinLabel(i, cuts[i-2][0])

# Cut-by-cut histograms
cut_by_cut_var_histos = []
for i_cut in range(-1, len(cuts)) :
    this_cut_by_cut_var_histos = []
    for this_cut_name, cut_function, short_name, nbins, range_start, range_end in cuts :
        print("Initializing", short_name, nbins, range_start, range_end)
        this_cut_by_cut_var_histos.append(ROOT.TH1D("_"+str(i_cut+1)+"_"+short_name+"_0",
                                                    short_name,
                                                    nbins, range_start, range_end))
    cut_by_cut_var_histos.append(this_cut_by_cut_var_histos)

i_pass = 0
passes_cut = [False]*len(cuts)
cut_var = [0.]*len(cuts)
for ievent, event in enumerate(ch):
    if not ievent%100000: print('Sanity check', ievent)
    n_cuts_passed = 0
    accept_event = True
    scifiDet.InitEvent(event.EventHeader)
    muFilterDet.InitEvent(event.EventHeader)
    h['cutFlow'].Fill(0.)
    for i_cut, cut in enumerate(cuts) :
        this_cut_passed, this_cut_var = cut[1](event)
        passes_cut[i_cut] = this_cut_passed
        if accept_event and this_cut_passed :
            h['cutFlow'].Fill(1+i_cut)
        else:
            accept_event = False
    if accept_event :
        output_tree.Fill()
        # you can do more here
    for seq_cut in range(-1, len(passes_cut)) :
        if seq_cut >= 0 :
            if not passes_cut[seq_cut] :
                break
#        for i_hist in range(len(cut_by_cut_var_histos[seq_cut+1])) :
        for i_cut_var, this_cut_var in enumerate(cut_var) :
            cut_by_cut_var_histos[seq_cut+1][i_cut_var].Fill(this_cut_var)
            
print(h['cutFlow'].GetBinContent(h['cutFlow'].GetNbinsX()), 'events passed the cuts')
for _h in h.values():
    _h.Write()
for _h in cut_by_cut_var_histos:
    _h[0].Write()
output_file.Write()
output_file.Close()

########################################################
# DISCARDED CUTS
########################################################

################################################################################
# Single Veto bar per plane fired
################################################################################
def SingleVetoBarsCut(event):
    ## add veto bars cut
    VetoBarFired    = {0: list(), 1: list()}
    for aHit in event.Digi_MuFilterHits:
        if aHit.GetSystem()!=1: continue
        plane, bar = GetVetoBar(aHit.GetDetectorID())
        VetoBarFired[plane].append(bar)
    ret = False
    value = 1
    if len(VetoBarFired[0]) == len(VetoBarFired[1]) == 1:
        if VetoBarFired[0][0] == 1 or VetoBarFired[1][0] == 1:
            ret = True
            value = len(VetoBarFired[0])+len(VetoBarFired[1])
    return ret, value
#cuts.append(["Ask for Veto Bars 1", SingleVetoBarsCut, "SingleVetoBars", 3, -0.5, 2.5])
################################################################################
# SciFi2 QDC value
################################################################################
scifi_qdcthresh = 100
def ScifiQDCthresh(event):
    this_qdc = 0
    ret = False
    for digi in event.Digi_ScifiHits:
        if not digi.isValid(): continue
        detID = digi.GetDetectorID()
        if not digi.GetStation() == scifiplane: continue
        ns = max(1, digi.GetnSides())
        for side in range(ns):
            for m in range(digi.GetnSiPMs()):
                qdc = digi.GetSignal(m+side*digi.GetnSiPMs())
                if not qdc < 0 :
                    this_qdc += qdc
    if this_qdc > scifi_qdcthresh: ret = True
    value = this_qdc
    return ret, value
#cuts.append(["Scifi{0} QDC value > {1}".format(scifiplane, scifi_qdcthresh), ScifiQDCthresh, "ScifiQDCthresh", 20*16, 0, 200*16])
################################################################################
# SciFi2 avg position in Brick 1
################################################################################
scifiplane=1
def ScifiAvgPosBrick(event):
    avg_sf_x, avg_sf_y = getAvgScifiPos(event, scifiDet)
    #print(avg_sf_x[scifiplane], avg_sf_y[scifiplane])
    ret = False
    if avg_sf_y[scifiplane] < scifi2Vert_or['Y'] and avg_sf_x[scifiplane] > scifi2Hor_or['X']: ret = True
    value = avg_sf_x[scifiplane]
    return ret, value
#cuts.append(["Scifi{0} avg position located in Brick1".format(scifiplane), ScifiAvgPosBrick, "ScifiAvgPosBrick", 500, -50, 0])
################################################################################
# Shower forming
################################################################################
scifiplane = 2
delta_threshold = 3.
def FollowShower(event):
    nsf_stat = {1:0, 2:0, 3:0, 4:0, 5:0}
    nsf_stat_corr = {1:0, 2:0, 3:0, 4:0, 5:0}
    nsf_statID = {1:0, 2:0, 3:0, 4:0, 5:0}
    Nsf_corr, Nsf, nsf_stat_corr, nsf_stat = CorrectScifi(event)
    if Nsf == 0 or Nsf_corr == 0: return False, 0
    nsf_statID=nsf_stat_corr
    FirstSFHit = -1
    deltahits = {2:0, 3:0, 4:0, 5:0}
    FirstSFHit = next((i for i, x in enumerate(nsf_statID.values()) if x), None)+1
    for detID in range(1, 6):
        if detID > FirstSFHit and nsf_statID[detID-1] and detID > 1:
            deltahits[detID] = float((nsf_statID[detID]-nsf_statID[detID-1])/nsf_statID[detID-1])
    ret = False
    if deltahits[scifiplane] > delta_threshold: ret = True
    return ret, deltahits[scifiplane]
#cuts.append(["Scifi hit variation > {0} from scifi{1} to scifi{2}".format(delta_threshold, scifiplane-1, scifiplane), FollowShower, "FollowShower", 180, -3, 15])
################################################################################
# SciFi QDC variation
################################################################################
scifi_deltaqdc = 3.
first_sf_plane = 1
def ScifiQDCVariation(event):
    this_qdc = 0
    ret = False
    qdc_station = {1:0, 2:0, 3:0, 4:0, 5:0}
    delta_qdc = {2:0, 3:0, 4:0, 5:0}
    for digi in event.Digi_ScifiHits:
        if not digi.isValid(): continue
        detID = digi.GetDetectorID()
        station = digi.GetStation()
        ns = max(1, digi.GetnSides())
        for side in range(ns):
            for m in range(digi.GetnSiPMs()):
                qdc = digi.GetSignal(m+side*digi.GetnSiPMs())
                if not qdc < 0 :
                    qdc_station[station] += qdc
    for stat in delta_qdc.keys():
        if qdc_station[stat-1] == 0: return False, 0
        delta_qdc[stat] = float((qdc_station[stat]-qdc_station[stat-1])/qdc_station[stat-1])
    #print(qdc_station[first_sf_plane], qdc_station[first_sf_plane+1], delta_qdc[first_sf_plane+1])
    if delta_qdc[first_sf_plane+1] > scifi_deltaqdc: ret = True
    value = delta_qdc[first_sf_plane+1]
    return ret, value
#cuts.append(["Scifi QDC variation > {0} from scifi{1} to scifi{2}".format(scifi_deltaqdc, first_sf_plane, first_sf_plane+1), ScifiQDCVariation, "ScifiQDCVariation", 180, -3, 15])
################################################################################
# At least 80 SciFi hits
################################################################################
min_scifi_hits_cut = 80
def min_scifi_hits(event) :
    n_hits = 0
    n_hits_corr = 0
    ret = False
    n_hits_corr, n_hits, nsf_statID_corr, nsf_statID = CorrectScifi(event)
    if isMC:
        if n_hits > min_scifi_hits_cut: ret = True
        return ret, n_hits
    else:
        if n_hits_corr > min_scifi_hits_cut: ret = True
        return ret, n_hits_corr
#cuts.append(["More than {0} SciFi hits (CORRECTED)".format(min_scifi_hits_cut), min_scifi_hits, "scifi_nhits", 100, 0, 3000])
