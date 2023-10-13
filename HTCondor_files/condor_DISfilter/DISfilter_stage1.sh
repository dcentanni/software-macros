#!/bin/bash

ClusterId=$1
ProcId=$2
FILENAME=$3
RUN=$4

OUTDIR=/eos/experiment/sndlhc/users/dancc/MuonDIS/DISfilter/DATA/


# Set up SND environment
SNDBUILD_DIR=/afs/cern.ch/user/d/dannc/SNDBUILD3/sw
source /cvmfs/sndlhc.cern.ch/SNDLHC-2023/Jan22/setUp.sh
eval `alienv load -w $SNDBUILD_DIR --no-refresh sndsw/latest`

muonDISFilterGoldenSample $FILENAME $OUTDIR/stage1_parallel/DATA-MuonDISFilter-stage1-run${RUN}.${ProcId}.root 0
