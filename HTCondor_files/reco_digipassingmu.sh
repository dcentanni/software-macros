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

# Run usual passing muon simulation
INPUTFILE=/eos/experiment/sndlhc/MonteCarlo/FLUKA/muons_up/version1/unit30_Nm.root
OUTPUTDIR=/eos/user/d/dannc/digipassingmu_CB
for i in 75 76 77 78 79 82 84 86 87 88 90 91 92
do
STARTEVENT=$((i*100))
LSB_JOBINDEX=$((i+1))
echo "Starting script, from event" $STARTEVENT
/cvmfs/sndlhc.cern.ch/SNDLHC-2022/March10/sw/slc7_x86-64/Python/v3.6.8-local1/bin/python3 $SNDLHC_mymaster/sndsw/shipLHC/run_simSND.py --Ntuple --eMin 1.0 -n $NEVENTS -i $STARTEVENT -f $INPUTFILE -o $OUTPUTDIR/$LSB_JOBINDEX
#Run digitization
SIMFILE=$OUTPUTDIR/$LSB_JOBINDEX/sndLHC.Ntuple-TGeant4.root
GEOFILE=$OUTPUTDIR/$LSB_JOBINDEX/geofile_full.Ntuple-TGeant4.root
if [ -f "$SIMFILE" ] && [ -f "$GEOFILE" ]; 
then
	echo "Running digitization for $SIMFILE using geofile:$GEOFILE."
	/cvmfs/sndlhc.cern.ch/SNDLHC-2022/March10/sw/slc7_x86-64/Python/v3.6.8-local1/bin/python3 $SNDLHC_mymaster/sndsw/shipLHC/run_digiSND.py -n $NEVENTS -g $GEOFILE -f $SIMFILE
else 	
	echo "WARNING, files not found."
	return
fi
done
