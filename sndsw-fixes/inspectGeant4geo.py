import sys
import ROOT
from rootpyPickler import Unpickler
#import shipRoot_conf
#shipRoot_conf.configure()

fname = 'geofile_full.10.0.Pythia8-TGeant4.root'
if len(sys.argv) > 1:
    fname = sys.argv[1]

fgeo = ROOT.TFile(fname)
sGeo = fgeo.FAIRGeom
import shipLHC_conf
run = ROOT.FairRunSim()
upkl = Unpickler(fgeo)
snd_geo = upkl.load('ShipGeo')
modules = shipLHC_conf.configure(run, snd_geo)
run.SetUserConfig('g4Config.C')
run.SetName('TGeant4')
run.SetOutputFile(ROOT.TMemFile('output', 'recreate'))
run.Init()
run.Run(0)
import geomGeant4
geomGeant4.printVMCFields()
#geomGeant4.printWeightsandFields() not working for now