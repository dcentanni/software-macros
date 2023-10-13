#!/bin/bash

ClusterId=$1
ProcId=$2
RUN=$3

OUTDIR=/eos/experiment/sndlhc/users/dancc/MuonDIS/DISfilter/DATA/


# Set up SND environment
SNDBUILD_DIR=/afs/cern.ch/user/d/dannc/SNDBUILD3/sw
source /cvmfs/sndlhc.cern.ch/SNDLHC-2023/Jan22/setUp.sh
eval `alienv load -w $SNDBUILD_DIR --no-refresh sndsw/latest`

hadd -f $OUTDIR/stage1/DATA-MuonDISFilter-stage1-run${RUN}.root $OUTDIR/stage1_parallel/DATA-MuonDISFilter-stage1-run${RUN}.*
hadd -f $OUTDIR/stage1/DATA-MuonDISFilter-run${RUN}__muonReco.root $OUTDIR/tracked_parallel/DATA-MuonDISFilter-stage1-run${RUN}.*
hadd -f $OUTDIR/stage2/2023/DATA-MuonDISFilter-stage2-run${RUN}.root $OUTDIR/stage2_parallel/DATA-MuonDISFilter-stage2-run${RUN}.*
#hadd $OUTDIR/stage3/2023/DATA-MuonDISFilter-stage3-run${RUN}.root $OUTDIR/stage3_parallel/DATA-MuonDISFilter-stage3-run${RUN}.*

#mv $OUTDIR/DATA-MuonDISFilter-run${RUN}.* $OUTDIR/TOBEDELETED/

#python /afs/cern.ch/work/d/dannc/public/MuonBackground/muonDis_sim/condor_DISfilter/DIS_jobPartitioning.py -f $OUTDIR/stage1/DATA-MuonDISFilter-run${RUN}_stage1.root > /afs/cern.ch/work/d/dannc/public/MuonBackground/muonDis_sim/condor_DISfilter/run_00${RUN}_dagfiles/njobs_run${RUN}
