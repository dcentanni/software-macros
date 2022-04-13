#!/bin/bash                                                                                                                       
ProcId=$2
ClusterId=$1
NEVENTS=100
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

#INPUTFILE=/afs/cern.ch/work/d/dannc/public/MuonBackground/unit30_Nm_z5000_1cm2.root                                              

INPUTFILE=/afs/cern.ch/work/d/dannc/public/MuonBackground/unit30_Nm_z290.736831_WALL1.1.root
OUTPUTDIR=/eos/user/d/dannc/emulsionactive
EVT_OFFSET=111
for i in 1 2 4 6 8 15 16 22 31 40 54 64 107 132 135 137 140 142 160 176 191 209 247 293 294 324 342 347 380 381 439 440 474 475 521 523 534 541 542 552 553 572 573 574 617 636 653 657 668 672 676 677 691 769 835 842 907 909 910 929 971
do
STARTEVENT=$((i*100+EVT_OFFSET*100))
LSB_JOBINDEX=$((i+1+EVT_OFFSET))
echo "Starting script, from event" $STARTEVENT
/cvmfs/sndlhc.cern.ch/SNDLHC-2021/June/15/sw/slc7_x86-64/Python/v3.6.8-local1/bin/python3 $SNDLHC_mymaster/sndsw/shipLHC/run_simSND.py --Ntuple --eMin 1.0 -n $NEVENTS -i $STARTEVENT -f $INPUTFILE -o $OUTPUTDIR/$LSB_JOBINDEX
done
