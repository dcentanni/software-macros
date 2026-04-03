import ROOT
import rootUtils as ut
import sys

brickID = int(sys.argv[1])

fin = ROOT.TFile.Open("/eos/experiment/sndlhc/users/dancc/PassingMu/ALL_lhc_ir1_coll_2023_exp001_fort_inEmu/sndLHC.Ntuple-TGeant4.root")
tree = fin.Get("cbmsim")

fout = ROOT.TFile.Open(f"/eos/home-d/dannc/AccurateSim/muons_at_brick{brickID}", "RECREATE")

flukafile = ROOT.TFile.Open("/eos/experiment/sndlhc/MonteCarlo/FLUKA/muons_down/2025/scoring_at449m/ALL_lhc_ir1_coll_2023_exp001_fort.root")
fluka_tree = flukafile.Get("nt")
output_tree = fluka_tree.CloneTree(0)
h = {}
ut.bookHist(h, f"Energy_at_brick{brickID}", f"Energy_at_brick{brickID}; E_{{#mu}} [GeV]; weight_sum", 5000, 0, 5000)
ut.bookHist(h, f"Energy_at_brick{brickID}_unweighted", f"Energy_at_brick{brickID}; E_{{#mu}} [GeV]; weight_sum", 5000, 0, 5000)

events_at_brick = []
for ievent, event in enumerate(tree):
  found_mu = False
  for point in event.EmulsionDetPoint:
    if int(point.GetDetectorID()/1000) == brickID and point.GetTrackID() == 0:
      found_mu = True
      #events_at_veto.append(ievent)
      rc = fluka_tree.GetEntry(ievent)
      output_tree.Fill()
      energy = event.MCTrack[point.GetTrackID()].GetEnergy()
      h[f"Energy_at_brick{brickID}"].Fill(energy, event.MCTrack[0].GetWeight())
      h[f"Energy_at_brick{brickID}_unweighted"].Fill(energy)
      break
  if found_mu: continue



ROOT.gROOT.SetBatch(True)
canv = ROOT.TCanvas()
h[f"Energy_at_brick{brickID}"].DrawClone("HIST")
canv.Draw()
canv.Print(f"/eos/home-d/dannc/AccurateSim/muon_energy_at_brick{brickID}.png", "png")
fout.cd()
for _h in h.values():
  _h.Write()
output_tree.Write()
fout.Write()
fout.Close()
fin.Close()