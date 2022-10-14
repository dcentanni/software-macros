#!/bin/bash

ProcId=$1
ClusterId=$2

# Set up SND environment
SNDBUILD_DIR=/afs/cern.ch/user/d/dannc/sw
source /cvmfs/sndlhc.cern.ch/SNDLHC-2022/June10/setUp.sh
eval `alienv load -w $SNDBUILD_DIR --no-refresh sndsw/latest`

python /afs/cern.ch/work/d/dannc/public/SND_sim/digiMuDis-Analysis.py -procID $ProcId -clusID $ClusterId 
