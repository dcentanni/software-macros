import ROOT

from argparse import ArgumentParser
parser = ArgumentParser()
parser.add_argument("-f", "--inputFile", dest="inFile", help=".root geometry file", required=True)
options = parser.parse_args()

f = ROOT.TFile(options.inFile)
geo  = f.Get("FAIRGeom")
tmp = options.inFile.split('/')
outFile = tmp[len(tmp)-1].replace('.root', '.gdml')
outAll = '/'.join(tmp[:-1])+'/'+outFile
geo.Export(outAll)