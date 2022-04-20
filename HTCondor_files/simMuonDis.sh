
#!/bin/bash
ProcId=$2
ClusterId=$1
NEVENTS=1000
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
INPUTFILES=/eos/experiment/sndlhc/MonteCarlo/FLUKA/muons_up/version1/unit30_Nm.root #for negative muons_up
echo "From file "
echo $INPUTFILES

OUTPUTDIR=/afs/cern.ch/work/d/dannc/public/MuonBackground/muonDis_sim

/cvmfs/sndlhc.cern.ch/SNDLHC-2021/June/15/sw/slc7_x86-64/Python/v3.6.8-local1/bin/python3 $SNDLHC_mymaster/sndsw/shipLHC/run_simSND.py --Ntuple -f $INPUTFILES -i $STARTEVENT -n $NEVENTS -o $OUTPUTDIR/$Cl$

#unused options : --FollowMuon --FastMuon -D for storing trajectories


