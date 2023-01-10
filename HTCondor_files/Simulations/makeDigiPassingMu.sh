#!/bin/bash

OUTPUTDIR=$2
INFILE=$1

SNDLHC_mymaster=/afs/cern.ch/user/d/dannc/

# Set up SND environment
SNDBUILD_DIR=/afs/cern.ch/user/d/dannc/sw
source /cvmfs/sndlhc.cern.ch/SNDLHC-2022/June10/setUp.sh
eval `alienv load -w $SNDBUILD_DIR --no-refresh sndsw/latest`

echo "Starting digitization of file:"
echo "From file $INFILE"

export EOSSHIP=root://eosuser.cern.ch/



# Run digitization
python $SNDLHC_mymaster/sndsw/shipLHC/run_digiSND.py -g $OUTPUTDIR/geofile_full.Ntuple-TGeant4.root -f $INFILE -n 10000000 

#Copy output file
xrdcp -f ./sndLHC.Ntuple-* $OUTPUTDIR/
rm -rf ./*.root