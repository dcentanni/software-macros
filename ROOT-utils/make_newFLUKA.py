import ROOT
from array import array

SND_Z = 326.2 #cm
SND_Z_FLUKA = 483.262*100.0 #cm

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

def GetBrick1cm2(BrickID):
    ROOT.gGeoManager.Import(options.geoFile)
    Wall = int(BrickID/10)-1
    Brick = BrickID%10
    Row = 0
    BrickDict = {1:1, 2: 0, 3: 1, 4:0}
    if Brick > 2: 
        Row = 1
    BrickPath = '/cave_1/Detector_0/volTarget_1/Wall_'+str(Wall)+'/Row_'+str(Row)+'/Brick_'+str(BrickDict[Brick])
    Ranges = {'X': list(), 'Y': list()}
    Br_Or, Br_Dim = getOriginAndDims(BrickPath)
    for proj in Ranges.keys():
        Ranges[proj] = [Br_Or[proj]-0.5, Br_Or[proj]+0.5]
    print('Generating in', Ranges)
    return Ranges


def muonPreTransport():
    variables = ""
    tmp = options.inputFile.split('/')
    infname = tmp[len(tmp)-1]
    foutName = options.outDir+'/'+infname.replace('.root','_z'+str(options.z)+'.root')
    fout  = ROOT.TFile(foutName,'recreate')
    for n in range(nt.GetListOfLeaves().GetEntries()):  
          variables+=nt.GetListOfLeaves()[n].GetName()
          if n < nt.GetListOfLeaves().GetEntries()-1: variables+=":"
    sTree =  ROOT.TNtupleD("nt","muon",variables)
    z_FLUKA = options.z - SND_Z
    for n in range(nt.GetEntries()):
        rc = nt.GetEvent(n)
        E = nt.E - 27.
        if E>0:
            column = []
            lam = ((z_FLUKA+SND_Z_FLUKA)-nt.z)/nt.pz
            for n in range(nt.GetListOfLeaves().GetEntries()):
                val = nt.GetListOfLeaves()[n].GetValue()
                if nt.GetListOfLeaves()[n].GetName()=='E':  val = E
                if nt.GetListOfLeaves()[n].GetName()=='x':  val = nt.x+lam*nt.px
                if nt.GetListOfLeaves()[n].GetName()=='y':  val = nt.y+lam*nt.py
                if nt.GetListOfLeaves()[n].GetName()=='z':  val = z_FLUKA+SND_Z_FLUKA
                column.append(val)
            theTuple  = array('d',column)
            rc = sTree.Fill(theTuple)
    sTree.AutoSave()
    fout.Close()
    return foutName

def GenRandXY(foutName, BrickID):
    variables = ""
    fin = ROOT.TFile.Open(foutName)
    _foutname = foutName.replace('.root', '_BRICK'+str(BrickID)+'.root')
    fout = ROOT.TFile(_foutname, "RECREATE")
    _nt = fin.nt
    ROOT.gRandom.SetSeed(2)
    for n in range(_nt.GetListOfLeaves().GetEntries()):  
          variables+=_nt.GetListOfLeaves()[n].GetName()
          if n < _nt.GetListOfLeaves().GetEntries()-1: variables+=":"
    sTree =  ROOT.TNtupleD("nt","muon",variables)
    Ranges = GetBrick1cm2(BrickID)
    for n in range(_nt.GetEntries()):
        rc = _nt.GetEvent(n)
        column = []
        for n in range(_nt.GetListOfLeaves().GetEntries()):
            val = _nt.GetListOfLeaves()[n].GetValue()
            if _nt.GetListOfLeaves()[n].GetName()=='x':  val = ROOT.gRandom.Uniform(Ranges['X'][0], Ranges['X'][1])
            if _nt.GetListOfLeaves()[n].GetName()=='y':  val = ROOT.gRandom.Uniform(Ranges['Y'][0], Ranges['Y'][1])
            column.append(val)
        theTuple  = array('d',column)
        rc = sTree.Fill(theTuple)
    sTree.AutoSave()
    fout.Close()

from argparse import ArgumentParser
parser = ArgumentParser()
parser.add_argument("-f", "--inputFile", dest="inputFile", help="single input file", required=True)
parser.add_argument("-o", "--outDir", dest="outDir", help="outputdir", required=False, default='.')
parser.add_argument("-g", "--geoFile", dest="geoFile", help="geofile", required=True)
parser.add_argument("-z", dest="z", help="z extrap", type=float, required=True)
parser.add_argument("--brick", dest="brickID", help="Brick ID", type=int, required=False, default=11)
options = parser.parse_args()

inFile = ROOT.TFile.Open(options.inputFile)
nt = inFile.nt


foutname = muonPreTransport()
GenRandXY(foutname, options.brickID)

