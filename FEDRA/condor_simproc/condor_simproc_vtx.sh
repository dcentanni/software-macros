#!/bin/bash

export EOSSHIP=root://eospublic.cern.ch/

BRICKID=21
BRICKFOLDER=b000021
CELL=$1
CELLFOLDER=$2
xcell=$((CELL % 18 + 1))
ycell=$((CELL / 18 + 1))
EXP_PRE=$3
EXP_DIR=$EXP_PRE/cell_reco/$CELLFOLDER/$BRICKFOLDER


echo "Set up SND environment"
#SNDBUILD_DIR=/afs/cern.ch/work/d/dannc/public/MuDIS_sim/
source /cvmfs/sndlhc.cern.ch/SNDLHC-2023/Aug30/setUp.sh
#export ALIBUILD_WORK_DIR=/afs/cern.ch/work/f/falicant/public/SNDBUILD/sw/
SNDBUILD_DIR=/afs/cern.ch/work/f/falicant/public/SNDBUILD/sw/
eval `alienv load -w $SNDBUILD_DIR --no-refresh sndsw/latest`
#source /cvmfs/sndlhc.cern.ch/SNDLHC-2024/June25/setUp.sh
#source ${SNDBUILD_DIR}/sndsw_muDIS.sh
echo "Loading FEDRA"
#source /afs/cern.ch/user/d/dannc/setup_fedrarelease.sh
source /afs/cern.ch/work/f/falicant/public/fedra/setup_new.sh

MAIN_DIR=$PWD
cd $MAIN_DIR
MY_DIR=${CELL}/$BRICKFOLDER
mkdir -p $MY_DIR
cd $MY_DIR
ln -s $EXP_DIR/vertex_disc.rootrc ./vertex.rootrc
ln -s $EXP_DIR/vertex_edi.rootrc .
ln -s $EXP_DIR/edipoda.sh ./
ln -s $EXP_DIR/$BRICKFOLDER.0.0.0.set.root ./$BRICKFOLDER.0.0.0.set.root
ln -s $EXP_DIR/$BRICKFOLDER.0.$xcell.$ycell.trk.root ./$BRICKFOLDER.0.0.0.trk.root
ln -s -f $EXP_DIR/$BRICKFOLDER.0.$xcell.$ycell.vtx.discimp.root ./$BRICKFOLDER.0.0.0.vtx.root

mv vertex_edi.rootrc vertex.rootrc
echo "find track $BRICKID.0.0.0"
source edipoda.sh $BRICKID

mv $BRICKFOLDER.0.0.0.vtx.refit.root $MAIN_DIR/$BRICKFOLDER.0.$xcell.$ycell.vtx.refit.root
