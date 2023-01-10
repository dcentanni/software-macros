import ROOT
from argparse import ArgumentParser

from datetime import date
today = date.today().strftime('%d%m%y')

parser = ArgumentParser()
parser.add_argument("-f", "--inputFile", dest="inFile", help=".root geometry file", required=True)
options = parser.parse_args()

outgeo = "/eos/user/d/dannc/AdvSND/neutrino_sim/GEOFILES/"

f = ROOT.TFile(options.inFile)
geo  = f.Get("FAIRGeom")
tmp = options.inFile.split('/')
outFile = tmp[len(tmp)-1].replace('.root', '.gdml')
outAll = '/'.join(tmp[:-1])+'/'+outFile
geo.Export(outAll)
geo.Export(outgeo+'AdvSNDGeometry.'+today+'.gdml)
