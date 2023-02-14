#!/bin/bash

BASE_OUT_DIR=$1
NEVENTS=$2
#GSIMPLE_FLUX=/eos/experiment/sndlhc/MonteCarlo/FLUKA/neutrino_up_13TeV/all13TeVK0_gsimple.root
GSIMPLE_FLUX=/afs/cern.ch/work/d/dannc/public/Neutrinosim/GSIMPLE/HL-LHC_neutrinos_TI18_20e6pr_gsimple.root
TARGET=$3
SEED=$4
TUNE=SNDG18_02a_01_000
GEOFILE=/eos/user/d/dannc/AdvSND/geofiles/AdvSND.geofile.110223.gdml
CLUSTERID=$5

echo "RUNNING " $BASE_OUT_DIR $NEVENTS $GSIMPLE_FLUX $TARGET $SEED

# Check if this solves job crashing problem. Typically run 100 jobs, so at most wait 15 minutes before starting.
#sleep $(( SEED*18 ))s

# Set up SND environment
ADVSNDBUILD_DIR=/afs/cern.ch/user/d/dannc/SNDBUILD2/
source /cvmfs/sndlhc.cern.ch/SNDLHC-2022/July14/setUp.sh
eval `alienv load -w $ADVSNDBUILD_DIR/sw --no-refresh sndsw/latest`

export EOSSHIP=root://eosuser.cern.ch/

# Run genie:
gevgen_fnal -f "${GSIMPLE_FLUX},,-14,14" -g $GEOFILE -t ${TARGET}  -L "cm" -D "g_cm3" -n $NEVENTS -o "sndlhc_${TARGET}_${NEVENTS}_ADV${TUNE}" --tune ${TUNE} --cross-sections /eos/home-d/dannc/AdvSND/neutrino_sim/SPLINES/genie_splines_GENIE_v32_ADV${TUNE}_2.xml --message-thresholds $GENIE/config/Messenger_laconic.xml --seed ${SEED} -z -2

# Convert file to GST
gntpc -i "sndlhc_${TARGET}_${NEVENTS}_ADV${TUNE}.0.ghep.root" -f gst -c

# Add axiliary variables to GST file
addAuxiliaryToGST "sndlhc_${TARGET}_${NEVENTS}_ADV${TUNE}.0.ghep.root" "sndlhc_${TARGET}_${NEVENTS}_ADV${TUNE}.0.gst.root"

# Run detector simulation
python $ADVSNDBUILD_DIR/sndsw/shipLHC/run_simSND.py --AdvSND --Genie 4 -f "./sndlhc_${TARGET}_${NEVENTS}_ADV${TUNE}.0.gst.root" -o ./ -n ${NEVENTS}


# Run digitization
#python $ADVSNDBUILD_DIR/sndsw/shipLHC/run_digiSND.py -g ./geofile_full.Genie-TGeant4.root -f ./sndLHC.Genie-TGeant4.root -cpp -n ${NEVENTS}

# Copy output
mkdir -p ${BASE_OUT_DIR}/${TARGET}/${CLUSTERID}/${SEED}/
xrdcp -f ./*.root ${BASE_OUT_DIR}/${TARGET}/${CLUSTERID}/${SEED}/
xrdcp -f ./*.status ${BASE_OUT_DIR}/${TARGET}/${CLUSTERID}/${SEED}/
rm -rf ./*.root ./*.status
