#!/bin/bash

BASE_OUT_DIR=$1
NEVENTS=15500
FLUKA_FILE=/eos/user/d/dannc/MuonBack_sim/FLUKA/LHC_-160urad_magfield_2022TCL6_muons_rock_2e8pr_z289.374023_BRICK11.root
CLUSTERID=$2
PROCID=$3
STARTEVENT=$((PROCID*NEVENTS))
LSB_JOBINDEX=$((PROCID+1))

# Set up SND environment
SNDBUILD_DIR=/afs/cern.ch/user/d/dannc/
source /cvmfs/sndlhc.cern.ch/SNDLHC-2023/Jan22/setUp.sh
eval `alienv load -w $SNDBUILD_DIR/sw --no-refresh sndsw/latest`

export EOSSHIP=root://eosuser.cern.ch/

# Run Ntuple gen
python $SNDBUILD_DIR/sndsw/shipLHC/run_simSND.py --Ntuple -f $FLUKA_FILE -i $STARTEVENT -n $NEVENTS -o ./ --FastMuon --zMax 1000

# Run digitization
python $SNDBUILD_DIR/sndsw/shipLHC/run_digiSND.py -g ./geofile_full.Ntuple-TGeant4.root -f ./sndLHC.Ntuple-TGeant4.root -cpp -n ${NEVENTS}

# Copy output
mkdir -p ${BASE_OUT_DIR}/${CLUSTERID}/${PROCID}/
xrdcp -f ./*.root ${BASE_OUT_DIR}/${CLUSTERID}/${PROCID}/
xrdcp -f ./*.status ${BASE_OUT_DIR}/${CLUSTERID}/${PROCID}/
rm -rf ./*.root ./*.status
