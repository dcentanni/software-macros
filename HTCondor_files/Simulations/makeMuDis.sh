#!/bin/bash
ProcId=$2
ClusterId=$1
inputname=$3
NEVENTS=10000
STEP=$((ProcId/46))
RECURSIVE=$((ProcId-STEP*46))
STARTEVENT=$((RECURSIVE*NEVENTS))
LSB_JOBINDEX=$((RECURSIVE+1))
echo $LSB_JOBINDEX

SNDLHC_mymaster=/afs/cern.ch/user/d/dannc/

# Set up SND environment
SNDBUILD_DIR=/afs/cern.ch/user/d/dannc/sw
source /cvmfs/sndlhc.cern.ch/SNDLHC-2022/June10/setUp.sh
eval `alienv load -w $SNDBUILD_DIR --no-refresh sndsw/latest`

echo "Starting script, from event number $STARTEVENT"
INPUTFILES=/eos/experiment/sndlhc/MonteCarlo/Pythia6/MuonDIS/$inputname.root
echo "From file $INPUTFILES"

OUTPUTDIR=/eos/user/d/dannc/muonDis_sim/ecut1.0_z-2.2_5.8m_Ioni/$inputname/

# Run detector simulation
python $SNDLHC_mymaster/sndsw/shipLHC/run_simSND.py --MuDIS -f $INPUTFILES -i $STARTEVENT -n $NEVENTS -o $OUTPUTDIR/$LSB_JOBINDEX --eMin 1.0

# Run digitization
python $SNDLHC_mymaster/sndsw/shipLHC/run_digiSND.py -g $OUTPUTDIR/$LSB_JOBINDEX/geofile_full.muonDIS-TGeant4-$inputname.root -f $OUTPUTDIR/$LSB_JOBINDEX/sndLHC.muonDIS-TGeant4-$inputname.root -cpp -n $NEVENTS 