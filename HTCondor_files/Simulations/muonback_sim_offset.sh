#!/bin/bash
ProcId=$2
ClusterId=$1
NEVENTS=100
EVT_OFFSET=111
STARTEVENT=$((ProcId*NEVENTS+EVT_OFFSET*100))
LSB_JOBINDEX=$((ProcId+1+EVT_OFFSET))
echo $LSB_JOBINDEX

sleep $ProcId

SNDLHC_mymaster=/afs/cern.ch/user/d/dannc/
export ALIBUILD_WORK_DIR=$SNDLHC_mymaster/sw #for alienv

echo "SETUP"
source /cvmfs/sndlhc.cern.ch/latest/setUp.sh
eval `alienv load sndsw/latest`

echo "Starting script, from event number "
echo $STARTEVENT

#INPUTFILE=/afs/cern.ch/work/d/dannc/public/MuonBackground/unit30_Nm_z5000_1cm2.root
INPUTFILE=/afs/cern.ch/work/d/dannc/public/MuonBackground/unit30_Nm_z290.736831_WALL1.1.root #455665 ENTRIES
OUTPUTDIR=/eos/user/d/dannc/emulsionactive
/cvmfs/sndlhc.cern.ch/SNDLHC-2021/June/15/sw/slc7_x86-64/Python/v3.6.8-local1/bin/python3 $SNDLHC_mymaster/sndsw/shipLHC/run_simSND.py --Ntuple --eMin 1.0 -n $NEVENTS -i $STARTEVENT -f $INPUTFILE -o $OUTPUTDIR/$LSB_JOBINDEX

#SINGLE JOBS
#/cvmfs/sndlhc.cern.ch/SNDLHC-2021/June/15/sw/slc7_x86-64/Python/v3.6.8-local1/bin/python3 $SNDLHC_mymaster/sndsw/shipLHC/run_simSND.py --Ntuple --eMin 1.0 -n $NEVENTS -i 5900 -f $INPUTFILE -o $OUTPUTDIR/60
