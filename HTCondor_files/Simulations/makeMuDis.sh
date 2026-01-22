#!/bin/bash
ProcId=$2
ClusterId=$1
inputname=$3
NEVENTS=14400
STEP=$((ProcId/100))
RECURSIVE=$((ProcId-STEP*100))
STARTEVENT=$((RECURSIVE*NEVENTS))
LSB_JOBINDEX=$((RECURSIVE+1))


SNDLHC_mymaster=/afs/cern.ch/user/d/dannc/

# Set up SND environment
SNDBUILD_DIR=/afs/cern.ch/user/d/dannc/sw
source /cvmfs/sndlhc.cern.ch/SNDLHC-2023/Jan22/setUp.sh
eval `alienv load -w $SNDBUILD_DIR --no-refresh sndsw/latest`

echo "Starting script, from event number $STARTEVENT"
INPUTFILES=/eos/user/d/dannc/muonDis_sim/Pythia6/latelateFLUKA/$inputname.root
echo "From file $INPUTFILES"
OUTPUTDIR=/eos/experiment/sndlhc/users/dancc/MuonDIS/ecut1.0_z_2.85_3.55m_allprocs_latelateFLUKA/$inputname/

export EOSSHIP=root://eosuser.cern.ch/

# Run detector simulation
#python $SNDLHC_mymaster/sndsw/shipLHC/run_simSND.py --MuDIS -f $INPUTFILES -i $STARTEVENT -n $NEVENTS -o ./ --eMin 1.0
python /afs/cern.ch/user/d/dannc/sndsw/shipLHC/run_simSND.py --MuDIS -f $INPUTFILES -i $STARTEVENT -n $NEVENTS -o ./ --eMin 1.0
# Run digitization
python $SNDLHC_mymaster/sndsw/shipLHC/run_digiSND.py -g ./geofile_full.muonDIS-TGeant4-$inputname.root -f ./sndLHC.muonDIS-TGeant4-${inputname}.root -n ${NEVENTS} -cpp 

#Copy output file
echo "Writing in ${OUTPUTDIR}/${LSB_JOBINDEX}"
mkdir -p ${OUTPUTDIR}/${LSB_JOBINDEX}/
xrdcp -f ./*.root ${OUTPUTDIR}/${LSB_JOBINDEX}/
rm -rf ./*.root
