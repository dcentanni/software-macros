#!/bin/bash
NEVENTS=10000
PROCID=$1
OLDCLUSID=$2
GSTNAME=sndlhc_+volAdvTarget_10000_ADVSNDG18_02a_01_000.gst.root
GST_FILE=/eos/user/d/dannc/AdvSND/neutrino_sim/GHEP-GST_files/HL-LHC_voAdvTarget/from${OLDCLUSID}/${GSTNAME}
STARTEVENT=$((PROCID*NEVENTS))
LSB_JOBINDEX=$((PROCID+1))
BASE_OUTDIR=/eos/user/d/dannc/AdvSND/neutrino_sim/numu_ADVSNDG18_02a_01_000_HL_LHC/+volAdvTarget

echo "Running neutrino propagation from file $GST_FILE"
echo "N. of events $NEVENTS, starting from $STARTEVENT"

# Set up SND environment
ADVSNDBUILD_DIR=/afs/cern.ch/user/d/dannc/SNDBUILD2/
source /cvmfs/sndlhc.cern.ch/SNDLHC-2022/July14/setUp.sh
eval `alienv load -w $ADVSNDBUILD_DIR/sw --no-refresh sndsw/latest`

export EOSSHIP=root://eosuser.cern.ch/

# Run detector simulation
python $ADVSNDBUILD_DIR/sndsw/shipLHC/run_simSND.py --AdvSND --Genie 4 -f ${GST_FILE} -o ./ -n ${NEVENTS} -i ${STARTEVENT}

# Copy output
mkdir -p ${BASE_OUTDIR}/prop_from${OLDCLUSID}/${LSB_JOBINDEX}/
xrdcp -f ./*.root ${BASE_OUTDIR}/prop_from${OLDCLUSID}/${LSB_JOBINDEX}/
xrdcp -f ./*.status ${BASE_OUTDIR}/prop_from${OLDCLUSID}/${LSB_JOBINDEX}/
rm -rf ./*.root ./*.status
