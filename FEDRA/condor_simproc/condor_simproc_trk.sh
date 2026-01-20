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
for PLATENUMBER in $(seq 1 57); do
    PLATEFOLDER="$(printf "p%0*d" 3 $PLATENUMBER)"
    mkdir -p -v ./$MY_DIR/$PLATEFOLDER
    ln -s $EXP_DIR/$PLATEFOLDER/$BRICKID.$PLATENUMBER.0.0.cp.root ./$MY_DIR/$PLATEFOLDER
done

cd $MY_DIR
ln -s $EXP_DIR/tracking.sh .
ln -s $EXP_DIR/vertexing.sh .
ln -s $EXP_DIR/discard.sh .
ln -s $EXP_DIR/track.rootrc .
ln -s $EXP_DIR/vertex_disc.rootrc ./vertex.rootrc

makescanset -set=21.0.0.0 -from_plate=57 -to_plate=1 -suff=cp.root -dz=-1350 -v=2 -new

echo "tracking $BRICKID.0.0.0"
source tracking.sh $BRICKID

if [[ -e "b000021.0.0.0.trk.root" ]]; then
        echo "File b000021.0.0.0.trk.root created"
else
	echo "Refitted file not created/present in, exiting"
	exit 1
fi

#mv $BRICKFOLDER.0.0.0.set.root $MAIN_DIR/$BRICKFOLDER.0.$xcell.$ycell.set.root
#mv $BRICKFOLDER.0.0.0.trk.root $MAIN_DIR/$BRICKFOLDER.0.$xcell.$ycell.trk.root
cp $BRICKFOLDER.0.0.0.set.root ${EXP_DIR}/$BRICKFOLDER.0.$xcell.$ycell.set.root
cp $BRICKFOLDER.0.0.0.trk.root ${EXP_DIR}/$BRICKFOLDER.0.$xcell.$ycell.trk.root

echo "emvertex $BRICKID.0.0.0"
source vertexing.sh $BRICKID

echo "discard high ip track $BRICKID.0.0.0"
source discard.sh $BRICKID

#mv $BRICKFOLDER.0.0.0.vtx.root $MAIN_DIR/$BRICKFOLDER.0.$xcell.$ycell.vtx.root
#mv $BRICKFOLDER.0.0.0.vtx.discimp.root $MAIN_DIR/$BRICKFOLDER.0.$xcell.$ycell.vtx.discimp.root
cp $BRICKFOLDER.0.0.0.vtx.root ${EXP_DIR}/$BRICKFOLDER.0.$xcell.$ycell.vtx.root
cp $BRICKFOLDER.0.0.0.vtx.discimp.root ${EXP_DIR}/$BRICKFOLDER.0.$xcell.$ycell.vtx.discimp.root
