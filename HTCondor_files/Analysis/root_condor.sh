#!/bin/bash

ProcId=$1
ClusterId=$2

sleep $ProcId

SNDLHC_mymaster=/afs/cern.ch/user/d/dannc/
export ALIBUILD_WORK_DIR=$SNDLHC_mymaster/sw #for alienv

echo "SETUP"
source /cvmfs/sndlhc.cern.ch/latest/setUp.sh
eval `alienv load sndsw/latest`
 
/cvmfs/sndlhc.cern.ch/SNDLHC-2022/March10/sw/slc7_x86-64/ROOT/v6-26-00-local1/bin/root -l <<EOC
.L /afs/cern.ch/work/d/dannc/public/SND_sim/muonrate.cpp
DoChain($ClusterId)
.q
EOC

#/cvmfs/sndlhc.cern.ch/SNDLHC-2022/March10/sw/slc7_x86-64/ROOT/v6-26-00-local1/bin/root -l <<EOC
#.L /afs/cern.ch/work/d/dannc/public/SND_sim/emulsion_mudensity.cpp
#DoDensity($ClusterId)
#.q
#EOC
