#!/bin/bash

ClusterId=$1
ProcId=$2
#DIR=$3
RUN=$3
FILENAME=$4

# Set up SND environment
SNDBUILD_DIR=/afs/cern.ch/user/d/dannc/SNDBUILD3/sw
source /cvmfs/sndlhc.cern.ch/SNDLHC-2023/Jan22/setUp.sh
eval `alienv load -w $SNDBUILD_DIR --no-refresh sndsw/latest`

Trackfile=${FILENAME/stage1_parallel/tracked_parallel}
stage2file=${FILENAME//stage1/stage2}

DIR=/eos/experiment/sndlhc/users/dancc/MuonDIS/DISfilter/DATA/
echo "Running stage 2 from file: ${FILENAME}"
python /afs/cern.ch/user/d/dannc/SNDBUILD3/sndsw/analysis/muonDISFilterGoldenSample_stage2.py -f ${DIR}/stage1_parallel/DATA-MuonDISFilter-stage1-run${RUN}.${ProcId}.root -t ${DIR}/tracked_parallel/DATA-MuonDISFilter-stage1-run${RUN}.${ProcId}__muonReco.root -g /eos/experiment/sndlhc/convertedData/physics/2023/geofile_sndlhc_TI18_V1_2023.root -o ${DIR}/stage2_parallel/DATA-MuonDISFilter-stage2-run${RUN}.${ProcId}.root
