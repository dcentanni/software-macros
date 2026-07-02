# 𝜈 and 𝜇 mixed simulation

This section explains how to a mixed simulation with signal and background is performed in `sndsw` and FEDRA.

The starting point is to have two simulations, one for signal (**neutrino**) and one for background (**passing muons**).

For the latter, we pick up a particular type of muon background simulation: muon background simulation with different densities, currently $$10^3, \,10^4, \,10^5\, \mu/cm^2$$ densities are available. Further simulations can be done through the script `make_newFLUKA.C` located [here](https://github.com/dcentanni/software-macros/blob/04712e320e1d29a4aafc6da715ab31bb667dfde4/analysis/make_newFLUKA.C).

> **NOTE**: be aware that there is a maximum number of muons that can be re-simulated according to the number of entries of the original FLUKA file.

The script that allows to provide the mixed simulation is `fromsndsw2FEDRA_muonduplication.C`, located [here](https://github.com/antonioiuliano2/macros-snd/blob/c3d46dcf505dbadd5308f6bbbcca5ec93d254db3/FEDRA/fromsndsw2FEDRA_muonduplication.C).

This script allows to mix a maximum number of neutrinos `nnuevents = 100` with a certain number of muons according to a given density, `nmuonsxnu = 100`.

So according to the density, for every neutrino interaction occurring in the SND@LHC emulsion target, `nmuonsxnu` muons are placed around it, given its x-y position.

> **NOTE**: for each background muon an eventID multiplier is associated, thus neutrino eventID will start from 0 whereas the background muon ones will start from `evID_multiplier = 1e+3`.

Once the muon positioning is done, a conversion to FEDRA of the simulated tracks is performed.
