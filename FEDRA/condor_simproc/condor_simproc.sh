#!/bin/bash

export EOSSHIP=root://eospublic.cern.ch/

BRICKID=21
BRICKFOLDER=b000021
CELL=$1


echo "Set up SND environment"
SNDBUILD_DIR=/afs/cern.ch/work/d/dannc/public/MuDIS_sim/
source /cvmfs/sndlhc.cern.ch/SNDLHC-2024/June25/setUp.sh
source ${SNDBUILD_DIR}/sndsw_muDIS.sh
echo "Loading FEDRA"
source /afs/cern.ch/user/d/dannc/setup_fedrarelease.sh

root -l -q /afs/cern.ch/work/d/dannc/public/MuDIS_sim/scripts/create_couplecells.C\(${CELL}\)
echo "Done ${CELL}"
