# Muon Deep Inelastic Scattering

This page will present notes on MuonDIS simulations, starting from their production.

The production script is the usual `shipLHC/run_simSND.py` script with the option `--MuDIS` and input files from Pythia6 provided beforehand, so lets talk first about the latter.

## MuonDIS input files

The input files to be provided in the `run_simSND.py` script are generated with a function in `shipLHC/muonDis.py` which simulates muon deep inelastic scattering on protons and neutrons with Pythia6. Such files are located in `/eos/experiment/sndlhc/MonteCarlo/Pythia6/muonDis`. There are many of these files and they are coded as follows:

```
xxxx = run+cycle*100+k
```

Where `k=0, 1000` whether we are considering **positive** muons or **negative** muons respectively, `c = 0 .. 2` for muons on protons or `c = 5 .. 7` for muons on neutrons and eventually `run = 1 .. 10` is for parallel processing.

The file we get has inside a tree (named "`DIS`") containing two `TParticle` objects, `InMuon` and `Particles`, their meaning is straightforward.

> **NOTE**: each InMuon is used 10 times, you can see from the scan of the `DIS` tree, by the command: `DIS->Scan("InMuon->GetPdgCode():InMuon->Energy()")`, there are 10 identical values of energy for each muon entry.

> **NOTE**: if the script receives a number of events greater than the available ones, the script will re-run the simulation from the first event of the input file.

## MuonDIS simulation files

To be written...
