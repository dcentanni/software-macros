import ROOT
import rootUtils as ut
import numpy as np
import sys

def adaptive_rebin(h, hu):
  edges  = np.array([h.GetBinLowEdge(i) for i in range(1, h.GetNbinsX()+2)])
  counts = np.array([h.GetBinContent(i) for i in range(1, h.GetNbinsX()+1)])
  cum = np.cumsum(counts)
  total = cum[-1]
  min_weight_per_bin = max(total / 100, float(sys.argv[2]) if len(sys.argv)>2 else 0.1)
  min_entries_per_bin = float(sys.argv[3]) if len(sys.argv)>3 else 3
  print(f"Total weight: {total}, total entries: {hu.GetEntries()}")
  print(f"Minimum weight per bin: {min_weight_per_bin}")
  print(f"Minimum entries per bin: {min_entries_per_bin}")
  new_edges = [edges[0]]
  accum = 0
  accum_entries = 0
  for i, c in enumerate(counts):
      accum += c
      accum_entries += hu.GetBinContent(i+1)
      if accum >= min_weight_per_bin and i < len(counts) - 1 and accum_entries >= min_entries_per_bin:
          new_edges.append(edges[i + 1])
          accum = 0
          accum_entries = 0
  #print(f"New edges {new_edges}")
  if new_edges[-1] != edges[-1]:
      new_edges.append(edges[-1])
  print(f"Created {len(new_edges) - 1} bins")
  # Create new histogram
  hnew = ROOT.TH1F(f"{h.GetName()}_adaptivebinning", f"{h.GetTitle()}", len(new_edges) - 1, np.array(new_edges, dtype='float64'))
  hunweight = ROOT.TH1F(f"{h.GetName()}_adaptivebinning_unweighted", f"{h.GetTitle()}", len(new_edges) - 1, np.array(new_edges, dtype='float64'))
  for i in range(1, h.GetNbinsX() + 1):
      x = h.GetBinCenter(i)
      c = h.GetBinContent(i)
      if c != 0:
          hnew.Fill(x, c)

  for i in range(1, hu.GetNbinsX() + 1):
      x = hu.GetBinCenter(i)
      c = hu.GetBinContent(i)
      if c != 0:
          hunweight.Fill(x, c)

  with open("adaptive_histogram.txt", "w") as fout:
      for i in range(1, hnew.GetNbinsX() + 1):
          low  = hnew.GetBinLowEdge(i)
          high = hnew.GetBinLowEdge(i + 1)
          cont = hnew.GetBinContent(i)
          nentries = hunweight.GetBinContent(i)
          fout.write(f"{low:.6g}\t{high:.6g}\t{cont:.6g}\t{nentries:.6g}\n")
  return hnew, hunweight


#fin = ROOT.TFile.Open("/eos/experiment/sndlhc/MonteCarlo/MuonBackground/muons_down/scoring_1.8_Bfield_4xstat/sndLHC.Ntuple-TGeant4-160urad_magfield_2022TCL6_muons_rock_2e8pr.root")
fin = ROOT.TFile.Open(sys.argv[1])
tree = fin.Get("nt")
h = {}
ut.bookHist(h, "Energy", "Energy_at_veto; E_{#mu} [GeV]; weight_sum", 50000, 0, 5000)
ut.bookHist(h, "Energy_unweighted", "Energy_at_veto; E_{#mu} [GeV]; weight_sum", 50000, 0, 5000)
fout = ROOT.TFile.Open(f"{sys.argv[1].split('.')[0]}_adaptivebinning.root","RECREATE")

events_at_veto = []
nentries = tree.GetEntries()
for i in range(nentries):
    tree.GetEntry(i)
    h['Energy'].Fill(tree.E, tree.w)
    h['Energy_unweighted'].Fill(tree.E)


h['adaptive'], h['unweighted'] = adaptive_rebin(h["Energy"], h["Energy_unweighted"])

ROOT.gROOT.SetBatch(True)
canv = ROOT.TCanvas()
h["adaptive"].DrawClone("HIST")
canv.Draw()
canv.Print("adaptive.png", "png")
fout.cd()
for _h in h.values():
  _h.Write()
fout.Write()
fout.Close()
fin.Close()

