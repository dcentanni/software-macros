#!/bin/bash
#NEVENTS=40000
NEVENTS=155000
ClusterId=$1
ProcId=$2
if [[ "$ProcId" -gt "9" ]]
    then
        ProcId=$((ProcId-10))
fi
STARTEVENT=$((NEVENTS*ProcId))
LSB_JOBINDEX=$((ProcId+1))
LSB_JOBINDEX=$( printf "%02d" $LSB_JOBINDEX )
TARGET=$3
if [[ "$TARGET" == "2" ]]
    then
        NUCLEON='p+'
        RUN=2$LSB_JOBINDEX
elif [[ "$TARGET" == "5" ]]
    then
        NUCLEON='n0'
        RUN=5$LSB_JOBINDEX
else
    echo "No nucleon identified"
    return
fi

# Set up SND environment
SNDBUILD_DIR=/afs/cern.ch/user/d/dannc/sw
source /cvmfs/sndlhc.cern.ch/SNDLHC-2023/Jan22/setUp.sh
eval `alienv load -w $SNDBUILD_DIR --no-refresh sndsw/latest`

echo "Starting script, from event number $STARTEVENT, nucleon is $NUCLEON, run is $RUN"
INPUTFILE=/eos/experiment/sndlhc/MonteCarlo/FLUKA/muons_down/scoring_1.8_Bfield/LHC_-160urad_magfield_2022TCL6_muons_rock_2e8pr.root
echo "From file $INPUTFILE"
OUTPUTDIR=/eos/experiment/sndlhc/users/dancc/MuonDIS/Pythia6/lateFLUKA20/

export EOSSHIP=root://eosuser.cern.ch/

#Run Pythia6 simulation
python /afs/cern.ch/work/d/dannc/public/MuonBackground/makeMuDIS.py -c make -f $INPUTFILE -n $NEVENTS -x 20 -s $STARTEVENT -r $RUN -N $NUCLEON -o $OUTPUTDIR
