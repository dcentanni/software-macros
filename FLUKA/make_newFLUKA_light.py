import ROOT
from array import array

def generate_in_bin(lumi, ibin, startevent=0, maxevents=-1):
    import time
    start_time = time.time()
    energy_smear = 5 #GeV
    angle_smear = 1e-3 #rad
    muonMass  = 0.105658
    center_b21 = {'x':-16.953706, 'y': 24.723750000000003, 'z': 307.857703}
    area_size = 19.2 #cm
    ROOT.gRandom.SetSeed(ibin*1234)
    with open(options.inputFile) as f:
        for _ in range(ibin - 1):
            next(f)
        line = next(f)
    parts = line.strip().split()
    e_low = float(parts[0])
    e_up = float(parts[1])
    weight = float(parts[2])
    nfluka_entries = int(float(parts[3]))
    #target_events = int(lumi*norm*weight*1e5*5.1444060) #last factor match up the expected tracks in 324 cm2 of B21 (considering the smearing)
    target_events = int(lumi*norm*weight*1e5*2.5080308*1.2) #last factor match up the expected tracks in 324 cm2 of B21 (considering the smearing)
    remaining_events = target_events - nfluka_entries
    if maxevents < 0: maxevents = remaining_events
    if remaining_events < 0: raise Exception(f"Bin {ibin} already has {nfluka_entries} events, which is more than the target {target_events} events!")
    #fluka_input = "/eos/experiment/sndlhc/users/dancc/FLUKA_regenspectrum_12cmB21/FLUKA_muons_at_B21_12cm.root"
    #fluka_input = "/eos/experiment/sndlhc/users/dancc/FLUKA_regenspectrum_12cmB21/FLUKA_muons_transpVeto_12cmB21.root"
    fluka_input = "/eos/experiment/sndlhc/users/dancc/FLUKA_regenspectrum_18cmB21/FLUKA_muons_transpVeto_fullB21.root"
    print(f"Expected events in bin {ibin}: {target_events} (FLUKA: {nfluka_entries}, to generate: {remaining_events})")
    print(f"Generating {maxevents} muons in energy bin {ibin}: {e_low} - {e_up} GeV")
    fin = ROOT.TFile.Open(fluka_input)
    _nt = fin.nt
    nentries = _nt.GetEntries()
    
    variables = ""
    for n in range(_nt.GetListOfLeaves().GetEntries()):  
        variables+=_nt.GetListOfLeaves()[n].GetName()
        if n < _nt.GetListOfLeaves().GetEntries()-1: variables+=":"

    #_foutname = f'{options.outdir}/FLUKA_muons_at_B21_12cm_{int(e_low)}_{int(e_up)}GeV_start{startevent}_max{startevent+maxevents}.root'
    _foutname = f'{options.outdir}/FLUKA_muons_transpVeto_fullB21-{int(e_low)}_{int(e_up)}GeV_start{startevent}_max{startevent+maxevents}.root'
    fout = ROOT.TFile(_foutname, "RECREATE")
    sTree =  ROOT.TNtupleD("nt","muon",variables)

    indices = []
    for i in range(nentries):
        nc = _nt.GetEvent(i)
        energy = _nt.E
        if e_low <= energy < e_up:
            indices.append(i)
    if len(indices) == 0:
        print(f"No events found in bin {ibin} ({e_low}-{e_up} GeV)")
        return

    start_idx = startevent
    end_idx = min(startevent + maxevents, target_events) if maxevents > 0 else target_events

    import itertools
    event_indices = itertools.cycle(indices)

    # Skip entries up to start index
    for _ in range(start_idx):
        next(event_indices)

    for i in range(start_idx, end_idx):
        idx = next(event_indices)
        _nt.GetEntry(idx)
        column = []
        if i%100000==0: print(f"Processing event {i}, FLUKA entry {idx}")
        #print(f"Processing FLUKA entry {idx} for output event {i}")
        if i < nfluka_entries:
            column = [ _nt.GetListOfLeaves()[n].GetValue() for n in range(_nt.GetListOfLeaves().GetEntries()) ]
        else:
            if e_low < 0.1: e_low = muonMass + 0.1
            E_smear = ROOT.gRandom.Uniform(e_low, e_up)
            p =  ROOT.TMath.Sqrt(_nt.px*_nt.px+_nt.py*_nt.py+_nt.pz*_nt.pz)
            Peloss = ROOT.TMath.Sqrt(E_smear*E_smear - muonMass*muonMass)
            scale = Peloss/p
            px = _nt.px*scale
            py = _nt.py*scale
            pz = _nt.pz*scale
            #px_smear = ROOT.gRandom.Uniform(-_nt.pz*angle_smear, +_nt.pz*angle_smear)
            #py_smear = ROOT.gRandom.Uniform(-_nt.pz*angle_smear, +_nt.pz*angle_smear) #aggiusta pz di conseguenza
            px_smear = ROOT.gRandom.Gaus(0, pz*angle_smear)
            py_smear = ROOT.gRandom.Gaus(0, pz*angle_smear)
            new_p2 = (px+px_smear)**2 + (py+py_smear)**2 + (pz)**2
            new_E2 = new_p2+muonMass**2 #muon mass
            E_diff = ROOT.TMath.Sqrt(new_E2) - E_smear
            #print(f"(FLUKA entry {idx})  Original E: {_nt.E:.5f} GeV, smeared E: {E_smear:.5f} GeV, new E with angle smear: {new_E2**0.5:.5f} (dE={E_diff:.5f} GeV), px: {px+px_smear:.5f}, py: {py+py_smear:.5f}, pz: {pz:.5f}, p: {new_p2**0.5:.5f} GeV")
            #Energy_smeared = _nt.E + E_diff
            Energy_smeared = E_smear + E_diff
            #if Energy_smeared < 0 or new_p2 < muonMass**2: print(f"\t Warning: negative smeared energy {Energy_smeared:.5f} GeV or invalid kinematics in event {i} (FLUKA entry {idx})")
            if Energy_smeared < 0 or new_p2 < muonMass**2: raise Exception(f"\t Warning: negative smeared energy {Energy_smeared:.5f} GeV or invalid kinematics in event {i} (FLUKA entry {idx})")

            for n in range(_nt.GetListOfLeaves().GetEntries()):
                val = _nt.GetListOfLeaves()[n].GetValue()
                if _nt.GetListOfLeaves()[n].GetName() == 'E':
                    val = Energy_smeared
                if _nt.GetListOfLeaves()[n].GetName() == 'px':
                    val = val + px_smear
                if _nt.GetListOfLeaves()[n].GetName() == 'py':
                    val = val + py_smear
                if _nt.GetListOfLeaves()[n].GetName() == 'pz':
                    val = pz
                if _nt.GetListOfLeaves()[n].GetName() == 'x':
                    #val = val + ROOT.gRandom.Uniform(-3, 3)
                    val = ROOT.gRandom.Uniform(center_b21['x'] - area_size/2, center_b21['x'] + area_size/2)
                if _nt.GetListOfLeaves()[n].GetName() == 'y':
                    #val = val + ROOT.gRandom.Uniform(-3, 3)
                    val = ROOT.gRandom.Uniform(center_b21['y'] - area_size/2, center_b21['y'] + area_size/2)
                column.append(val)
        theTuple = array('d', column)
        sTree.Fill(theTuple)

    fout.cd()
    sTree.Write()
    print(f"Output file {fout.GetName()} created with {sTree.GetEntries()} entries")
    fout.Write()
    fout.Close()
    fin.Close()
    print('Elapsed time: '+str((time.time()-start_time)/60.)+' mins')

def regen_muons(lumi, startevent=0, maxevents=-1):
    import time
    start_time = time.time()
    energy_smear = 20 #GeV
    angle_smear = 1e-3 #rad
    muonMass  = 0.105658
    center_b21 = {'x':-16.953706, 'y': 24.723750000000003, 'z': 307.857703}
    area_size = 19.2 #cm
    #fluka_input = "/eos/experiment/sndlhc/users/dancc/FLUKA_regenspectrum_12cmB21/FLUKA_muons_at_B21_12cm.root"
    #fluka_input = "/eos/experiment/sndlhc/users/dancc/FLUKA_regenspectrum_12cmB21/FLUKA_muons_transpVeto_12cmB21.root"
    fluka_input = "/eos/experiment/sndlhc/users/dancc/FLUKA_regenspectrum_18cmB21/FLUKA_muons_transpVeto_fullB21.root"
    print(f"Regenerating muons with energy and angle smearing from file: {fluka_input}")
    fin = ROOT.TFile.Open(fluka_input)
    _nt = fin.nt
    nentries = _nt.GetEntries()
    variables = ""
    for n in range(_nt.GetListOfLeaves().GetEntries()):  
        variables+=_nt.GetListOfLeaves()[n].GetName()
        if n < _nt.GetListOfLeaves().GetEntries()-1: variables+=":"
    #_foutname = f'{options.outdir}/FLUKA_muons_at_B21_12cm_{int(e_low)}_{int(e_up)}GeV_start{startevent}_max{startevent+maxevents}.root'
    _foutname = f'{options.outdir}/FLUKA_muons_transpVeto_fullB21-start{startevent}_max{startevent+maxevents}.root'
    fout = ROOT.TFile(_foutname, "RECREATE")
    sTree =  ROOT.TNtupleD("nt","muon",variables)
    if maxevents < 0: maxevents = nentries - startevent
    if startevent + maxevents > nentries:
        maxevents = nentries - startevent
    for i in range(startevent, startevent+maxevents):
        ROOT.gRandom.SetSeed(i*1234)
        _nt.GetEntry(i)
        weight = _nt.w
        target_events = int(lumi*norm*weight*1e5*2.5080308*1.2) #last factor match up the expected tracks in 324 cm2 of B21 (considering the smearing)
        #print(f"Processing FLUKA entry {i}")
        if _nt.E > 200 and _nt.E < 1750:
            energy_smear = 40
        elif _nt.E >= 1750:
            energy_smear = 80
        print(f"Generating {target_events} events from FLUKA entry {i} with original energy {_nt.E:.5f} GeV and weight {weight:.5e}, applying energy smear of {energy_smear} GeV")
        for j in range(target_events):
            column = []
            if j == 0:
                column = [ _nt.GetListOfLeaves()[n].GetValue() for n in range(_nt.GetListOfLeaves().GetEntries()) ]
                theTuple = array('d', column)
                sTree.Fill(theTuple)
            if j%10000==0: print(f"\t Processing entry {j} for FLUKA entry {i}")
            #E_smear = ROOT.gRandom.Uniform(e_low, e_up)
            E_smear = ROOT.gRandom.Gaus(_nt.E, energy_smear)
            if E_smear < muonMass + 0.1:
                E_smear = muonMass + 0.1
            p =  ROOT.TMath.Sqrt(_nt.px*_nt.px+_nt.py*_nt.py+_nt.pz*_nt.pz)
            Peloss = ROOT.TMath.Sqrt(E_smear*E_smear - muonMass*muonMass)
            scale = Peloss/p
            px = _nt.px*scale
            py = _nt.py*scale
            pz = _nt.pz*scale
            px_smear = ROOT.gRandom.Gaus(0, pz*angle_smear)
            py_smear = ROOT.gRandom.Gaus(0, pz*angle_smear)
            new_p2 = (px+px_smear)**2 + (py+py_smear)**2 + (pz)**2
            new_E2 = new_p2+muonMass**2 #muon mass
            E_diff = ROOT.TMath.Sqrt(new_E2) - E_smear
            #print(f"(FLUKA entry {idx})  Original E: {_nt.E:.5f} GeV, smeared E: {E_smear:.5f} GeV, new E with angle smear: {new_E2**0.5:.5f} (dE={E_diff:.5f} GeV), px: {px+px_smear:.5f}, py: {py+py_smear:.5f}, pz: {pz:.5f}, p: {new_p2**0.5:.5f} GeV")
            Energy_smeared = E_smear + E_diff
            if Energy_smeared < 0 or new_p2 < muonMass**2: raise Exception(f"\t Warning: negative smeared energy {Energy_smeared:.5f} GeV or invalid kinematics in event {i} (FLUKA entry {i})")
            for n in range(_nt.GetListOfLeaves().GetEntries()):
                val = _nt.GetListOfLeaves()[n].GetValue()
                if _nt.GetListOfLeaves()[n].GetName() == 'E':
                    val = Energy_smeared
                if _nt.GetListOfLeaves()[n].GetName() == 'px':
                    val = val + px_smear
                if _nt.GetListOfLeaves()[n].GetName() == 'py':
                    val = val + py_smear
                if _nt.GetListOfLeaves()[n].GetName() == 'pz':
                    val = pz
                if _nt.GetListOfLeaves()[n].GetName() == 'x':
                    #val = val + ROOT.gRandom.Uniform(-3, 3)
                    val = ROOT.gRandom.Uniform(center_b21['x'] - area_size/2, center_b21['x'] + area_size/2)
                if _nt.GetListOfLeaves()[n].GetName() == 'y':
                    #val = val + ROOT.gRandom.Uniform(-3, 3)
                    val = ROOT.gRandom.Uniform(center_b21['y'] - area_size/2, center_b21['y'] + area_size/2)
                column.append(val)
            theTuple = array('d', column)
            sTree.Fill(theTuple)    
    fout.cd()
    sTree.Write()
    print(f"Output file {fout.GetName()} created with {sTree.GetEntries()} entries")
    fin.Close()
    fout.Write()
    fout.Close()
    print('Elapsed time: '+str((time.time()-start_time)/60.)+' mins')
"""
now = datetime.datetime.now()
seed = int(now.timestamp() * 1e6) % (2**31 - 1)  # fit in 32-bit
rnd2 = ROOT.TRandom3(seed)
"""
def check_regen():
    import rootUtils as ut
    original = ROOT.TFile.Open('/eos/experiment/sndlhc/users/dancc/FLUKA_regenspectrum_12cmB21/FLUKA_muons_at_B21_12cm.root')
    regen = ROOT.TFile.Open('/eos/experiment/sndlhc/users/dancc/FLUKA_regenspectrum_12cmB21/FLUKA_muons_at_B21_12cm_total.root')
    oTree = original.nt
    rTree = regen.nt
    nentries = oTree.GetEntries()
    print(f"Original entries: {nentries}, Regenerated entries: {rTree.GetEntries()}")
    h = {}
    ut.bookHist(h, "Energy_at_veto_1fb", "Energy_at_veto; E_{#mu} [GeV]; weight_sum", 5000, 0, 5000)
    ut.bookHist(h, "Energy_at_veto_RUN1", "Energy_at_veto; E_{#mu} [GeV]; weight_sum", 5000, 0, 5000)
    ut.bookHist(h, "Energy_at_veto_unweighted", "Energy_at_veto; E_{#mu} [GeV]; weight_sum", 5000, 0, 5000)
    ut.bookHist(h, "Angle_at_veto_1fb", "Angle_at_veto; TX; TY", 1500, -0.015, 0.015, 1500, -0.015, 0.015)
    ut.bookHist(h, "Angle_at_veto_RUN1", "Angle_at_veto;  TX; TY", 1500, -0.015, 0.015, 1500, -0.015, 0.015)
    ut.bookHist(h, "Angle_at_veto_unweighted", "Angle_at_veto;  TX; TY", 1500, -0.015, 0.015, 1500, -0.015, 0.015)
    ut.bookHist(h, "Position_unweighted", "Position_unweighted;  x[cm]; y[cm]", 200, -100, 100, 200, -100, 100)
    ut.bookHist(h, "Position_RUN1", "Position_RUN1;  x[cm]; y[cm]", 200, -100, 100, 200, -100, 100)

    ut.bookHist(h, "Energy_at_veto_regen", "Energy_at_veto; E_{#mu} [GeV]; weight_sum", 5000, 0, 5000)
    ut.bookHist(h, "Angle_at_veto_regen", "Angle_at_veto; TX; TY", 1500, -0.015, 0.015, 1500, -0.015, 0.015)
    ut.bookHist(h, "Position_regen", "Position_regen;  x[cm]; y[cm]", 200, -100, 100, 200, -100, 100)

    for i in range(nentries):
        oTree.GetEntry(i)
        e = oTree.E
        weight = oTree.w
        h['Energy_at_veto_1fb'].Fill(e, weight*4*1e5)
        h['Energy_at_veto_RUN1'].Fill(e, weight*4*1e5*RUN1_lumi)
        h['Energy_at_veto_unweighted'].Fill(e)
        h['Angle_at_veto_1fb'].Fill(oTree.px/oTree.pz, oTree.py/oTree.pz, weight*4*1e5)
        h['Angle_at_veto_RUN1'].Fill(oTree.px/oTree.pz, oTree.py/oTree.pz, weight*4*1e5*RUN1_lumi)
        h['Angle_at_veto_unweighted'].Fill(oTree.px/oTree.pz, oTree.py/oTree.pz)
        h['Position_unweighted'].Fill(oTree.x, oTree.y)
        h['Position_RUN1'].Fill(oTree.x, oTree.y, weight*4*1e5*RUN1_lumi)

    for j in range(rTree.GetEntries()):
        rTree.GetEntry(j)
        e = rTree.E
        weight = rTree.w
        h["Energy_at_veto_regen"].Fill(e)
        h["Angle_at_veto_regen"].Fill(rTree.px/rTree.pz, rTree.py/rTree.pz)
        h['Position_regen'].Fill(rTree.x, rTree.y)
    
    outfile = ROOT.TFile.Open("/eos/experiment/sndlhc/users/dancc/FLUKA_regenspectrum_12cmB21/checkRegen.root", "RECREATE")
    for _h in h.values():
        _h.Write()
    outfile.Write()
    outfile.Close()
    original.Close()
    regen.Close()

def extract_mu_in_range(center: dict, area_size: float = 19.2):
    import rootUtils as ut
    SND_Z = 48000
    fin = ROOT.TFile.Open(options.inputFile)
    _nt = fin.nt
    nentries = _nt.GetEntries()
    startev = options.startevent
    nevents = options.maxevents
    if nevents < 0:
        nevents = nentries
    lastevents = nentries-startev
    if nevents >= lastevents:
        nevents = lastevents
    outfile = ROOT.TFile.Open(f"{options.outdir}", "RECREATE")
    variables = ""
    for n in range(_nt.GetListOfLeaves().GetEntries()):  
        variables+=_nt.GetListOfLeaves()[n].GetName()
        if n < _nt.GetListOfLeaves().GetEntries()-1: variables+=":"
    output_tree = ROOT.TNtupleD("nt","muon",variables)
    zbrick = center['z']
    h = {}
    ut.bookHist(h, "x_proj", "x_proj; x [cm]; entries", 200, -100, 100)
    ut.bookHist(h, "y_proj", "y_proj; y [cm]; entries", 200, -100, 100)
    for i in range(startev, startev+nevents):
        rc = _nt.GetEvent(i)
        if i%250000==0: print(f"Processing event {i}")
        x = _nt.x
        y = _nt.y
        z = _nt.z - SND_Z
        #project to brick21
        x_proj = x + (zbrick - z)*_nt.px/_nt.pz
        y_proj = y + (zbrick - z)*_nt.py/_nt.pz
        if abs(x_proj - center['x']) < area_size/2 and abs(y_proj - center['y']) < area_size/2:
            column = [ _nt.GetListOfLeaves()[n].GetValue() for n in range(_nt.GetListOfLeaves().GetEntries()) ]
            theTuple = array('d', column)
            outfile.cd()
            rc = output_tree.Fill(theTuple)
            h['x_proj'].Fill(x_proj)
            h['y_proj'].Fill(y_proj)
        #output_tree.AutoSave()
    outfile.cd()
    output_tree.Write()
    for _h in h.values():
        _h.Write()
    outfile.Write()
    outfile.Close()
    fin.Close()

def muonPreTransport(zproj = 278.36): #278.36 is 5 cm upstream of volVeto_1
    SND_Z = 48000.0
    muonMass  = 0.105658
    zproj_fluka = zproj + SND_Z
    import rootUtils as ut
    fin = ROOT.TFile('/eos/experiment/sndlhc/users/dancc/FLUKA_regenspectrum/FLUKA_muons_at_veto.root')
    h = {}
    nt = fin.nt
    fout = ROOT.TFile("FLUKA_muons_transpVeto.root", "RECREATE")
    ut.readHists(h, "/eos/experiment/sndlhc/users/dancc/MuonDIS/meanEloss_file/meanEloss.root")
    eLoss = h['TCeloss'].FindObject('pol3').Clone('eLoss')
    variables = ""
    for n in range(nt.GetListOfLeaves().GetEntries()):  
          variables+=nt.GetListOfLeaves()[n].GetName()
          if n < nt.GetListOfLeaves().GetEntries()-1: variables+=":"
    sTree =  ROOT.TNtuple("nt","muon",variables)
    excl_evts = 0
    for n in range(nt.GetEntries()):
        rc = nt.GetEvent(n)
        E = nt.E - eLoss.Eval(nt.E)
        if E < 0: 
            print(f"Skipping event {n} with negative energy after energy loss correction: {E} GeV")
            continue
        p =  ROOT.TMath.Sqrt(nt.px*nt.px+nt.py*nt.py+nt.pz*nt.pz)
        Peloss = ROOT.TMath.Sqrt(E*E - muonMass*muonMass)
        scale = Peloss/p
        px = nt.px*scale
        py = nt.py*scale
        pz = nt.pz*scale
        #if not isInB21(nt.x, nt.y, nt.z, px/pz, py/pz): continue
        #if not isInScifi1(nt.x, nt.y, nt.z, px/pz, py/pz): 
        #    excl_evts +=1
        #    continue
        column = []
        lam = (zproj_fluka - nt.z)/pz
        #deviate with 2.5mrad flat
        delta_angle = (zproj_fluka - nt.z)*ROOT.gRandom.Uniform(-2.5e-3, +2.5e-3)
        for n in range(nt.GetListOfLeaves().GetEntries()):
            val = nt.GetListOfLeaves()[n].GetValue()
            if nt.GetListOfLeaves()[n].GetName() == 'E': val = E
            if nt.GetListOfLeaves()[n].GetName() == 'x': val = nt.x + px*lam + delta_angle
            if nt.GetListOfLeaves()[n].GetName() == 'y': val = nt.y + py*lam + delta_angle
            if nt.GetListOfLeaves()[n].GetName() == 'z': val = zproj_fluka
            if nt.GetListOfLeaves()[n].GetName() == 'px': val = px
            if nt.GetListOfLeaves()[n].GetName() == 'py': val = py
            if nt.GetListOfLeaves()[n].GetName() == 'pz': val = pz
            column.append(val)
        theTuple = array('d', column)
        rc = sTree.Fill(theTuple)
    sTree.AutoSave()
    #print(f"Excluded events not going through Scifi1: {excl_evts} out of {nt.GetEntries()} ({100*excl_evts/nt.GetEntries():.2f}%)")
    fout.cd()
    sTree.Write()
    fout.Write()
    fout.Close()
            

energy_ranges = '/eos/experiment/sndlhc/users/dancc/FLUKA_regenspectrum_12cmB21/adaptive_histogram.txt'
from argparse import ArgumentParser
parser = ArgumentParser()
parser.add_argument("-f", "--inputFile", dest="inputFile", help="single input file", required=False, default=energy_ranges)
parser.add_argument("-o", "--outdir", dest="outdir", help="Output directory", required=False, default='./')
parser.add_argument("--ibin", type=int, help="Energy bin index", required=False)
parser.add_argument("--startevent", dest="startevent", type=int, default=0, help="First event index for this job")
parser.add_argument("--maxevents", dest="maxevents", type=int, default=-1, help="Number of events to generate in this job")
parser.add_argument("--gen", dest="generate",  action='store_true', default=False)
parser.add_argument("--ht", dest="condor",  action='store_true', default=False)
parser.add_argument("--extr_z", dest="extr_z",  action='store_true', default=False)
parser.add_argument("--mu_regen", dest="mu_regen",  action='store_true', default=False)
options = parser.parse_args()

norm = 8E8/2E8 # it's 4
muonflux_scifi_fb_cm2 = {1: 1.43e4, 2: 1.56e4, 3: 2.13e4, 4: 2.24e4} #https://indico.cern.ch/event/1249325/contributions/5267457/attachments/2597708/4484689/MuonFluxElectronicDet_Feb23.pdf
RUN1_lumi = 9.5 #fb-1 #https://indico.cern.ch/event/1513878/contributions/6378176/attachments/3021979/5332067/2025_02_26_EmulsionTarget_DiCrescenzo.pdf
RUN2_lumi = 20 #fb-1

if options.generate:
    generate_in_bin(
        lumi=RUN1_lumi,
        ibin=options.ibin,
        startevent=options.startevent,
        maxevents=options.maxevents
    )

if options.condor:
    import os
    condor_sub = '/afs/cern.ch/work/d/dannc/public/MuonBackground/makeFLUKAdensity_RUN1_regenspectr_light.sub'
    condor_sh = '/afs/cern.ch/work/d/dannc/public/MuonBackground/makeFLUKAdensity_RUN1_regenspectr_light.sh'
    #energy_ranges = '/eos/experiment/sndlhc/users/dancc/FLUKA_regenspectrum_18cmB21/NEWREGEN/adaptive_histogram.txt'
    #energy_ranges = '/eos/experiment/sndlhc/users/dancc/FLUKA_regenspectrum_18cmB21/adaptive_histogram.txt'
    energy_ranges = '/eos/experiment/sndlhc/users/dancc/FLUKA_regenspectrum_18cmB21/SWAN_BINNING/adaptive_histogram.txt'
    lines = []
    with open(energy_ranges) as f:
        for line in f:
            if line.strip():
                values = line.split()
                lines.append(values)
    maxjobs = 15
    #for ibin in range(1, len(lines)+1):
    for ibin, line in enumerate(lines, start=1):
        e_low = float(line[0])
        e_up = float(line[1])
        weight = float(line[2])
        nfluka_entries = int(float(line[3]))
        #target_events = int(RUN1_lumi*norm*weight*1e5) #lumi in fb-1
        #target_events = int(RUN1_lumi*norm*weight*1e5*2.2864026) #last factor match up the expected tracks in 144 cm2 of B21
        #target_events = int(RUN1_lumi*norm*weight*1e5*5.1444060) #last factor match up the expected tracks in 324 cm2 of B21 (considering the smearing)
        target_events = int(RUN1_lumi*norm*weight*1e5*2.5080308*1.2) #last factor match up the expected tracks in 324 cm2 of B21 (considering the smearing)
        maxevents = int(target_events/maxjobs)+1
        print(f"Submitting bin {ibin}: {e_low}-{e_up} GeV, target events: {target_events}, maxevents per job: {maxevents}")
        os.system(f'condor_submit IBIN="{int(ibin)}" MAXEV="{maxevents}" NJOBS="{maxjobs}" {condor_sub}')
        #os.system(f'source {condor_sh} {energy_ranges} IBIN="{int(ibin)}" MAXEV="{maxevents}" NJOBS="{maxjobs}" {condor_sub}')

if options.inputFile and options.extr_z:
    center_b21 = {'x':-16.953706, 'y': 24.723750000000003, 'z': 307.857703}
    extract_mu_in_range(center_b21)

if options.mu_regen:
    regen_muons(
        lumi=RUN1_lumi,
        startevent=options.startevent,
        maxevents=options.maxevents
    )
