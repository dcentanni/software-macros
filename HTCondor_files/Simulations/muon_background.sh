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

echo "Starting script, from event number "
echo $STARTEVENT 
#INPUTFILES=/eos/experiment/sndlhc/MonteCarlo/FLUKA/muons_up/scoring_2.5/muons_150urad_1e7pr.root
#NEW FLUKA FILE nentries = 260258
INPUTFILES=/afs/cern.ch/work/d/dannc/public/MuonBackground/muons_up/muons_150urad_1e7pr_E30.root #new fluka file without muons E<=30
#NEW FLUKA SKIMMED FILE nentries = 250772
echo "From file "
echo $INPUTFILES

OUTPUTDIR=/eos/user/d/dannc/passingmu_sim/

if [[ "$ProcId" -eq 25 ]]
then
	$NEVENTS=772
fi
/cvmfs/sndlhc.cern.ch/SNDLHC-2022/March10/sw/slc7_x86-64/Python/v3.6.8-local1/bin/python3 $SNDLHC_mymaster/sndsw/shipLHC/run_simSND.py --Ntuple -f $INPUTFILES -i $STARTEVENT -n $NEVENTS -o $OUTPUTDIR/$ClusterId/$LSB_JOBINDEX

#unused options : --FollowMuon --FastMuon -D for storing trajectories
