#!/bin/bash                                                                                                                       
ProcId=$2
ClusterId=$1
NEVENTS=10000
STARTEVENT=$((ProcId*NEVENTS))
LSB_JOBINDEX=$((ProcId+1))
echo $LSB_JOBINDEX

sleep $ProcId

SNDLHC_mymaster=/afs/cern.ch/user/d/dannc/
export ALIBUILD_WORK_DIR=$SNDLHC_mymaster/sw #for alienv                                                                          

echo "SETUP"
source /cvmfs/sndlhc.cern.ch/latest/setUp.sh
eval `alienv load sndsw/latest`

echo "Starting script of failed jobs recovery"

INPUTFILES=/eos/experiment/sndlhc/MonteCarlo/FLUKA/muons_up/scoring_2.5/muons_150urad_1e7pr.root
OUTPUTDIR=/eos/user/d/dannc/passingmu_sim/FLUKA_muons_159urad_1e7pr/

FAILEDCLUSID=$3
FAILEDPROCID=$4
STARTEVENT=$((FAILEDPROCID*NEVENTS))
LSB_JOBINDEX=$((FAILEDPROCID+1))
echo "Starting script, from event" $STARTEVENT
/cvmfs/sndlhc.cern.ch/SNDLHC-2022/March10/sw/slc7_x86-64/Python/v3.6.8-local1/bin/python3 $SNDLHC_mymaster/sndsw/shipLHC/run_simSND.py --Ntuple -f $INPUTFILES -i $STARTEVENT -n $NEVENTS -o $OUTPUTDIR/$FAILEDCLUSID/$LSB_JOBINDEX
