#!/bin/bash

ClusterId=$1
ProcId=$2
RUN=$3
FILENAME=$4

OUTDIR=/eos/experiment/sndlhc/users/dancc/MuonDIS/DISfilter/DATA/


# Set up SND environment
SNDBUILD_DIR=/afs/cern.ch/user/d/dannc/SNDBUILD3/sw
source /cvmfs/sndlhc.cern.ch/SNDLHC-2023/Jan22/setUp.sh
eval `alienv load -w $SNDBUILD_DIR --no-refresh sndsw/latest`


echo "Running tracking from file: ${FILENAME}"
python /afs/cern.ch/user/d/dannc/SNDBUILD3/sndsw/shipLHC/run_muonRecoSND.py -f ${OUTDIR}/stage1_parallel/DATA-MuonDISFilter-stage1-run${RUN}.${ProcId}.root  -g /eos/experiment/sndlhc/convertedData/physics/2023/geofile_sndlhc_TI18_V1_2023.root -s $OUTDIR/tracked_parallel/ -c passing_mu_DS -hf linearSlopeIntercept -o -sc 1 

