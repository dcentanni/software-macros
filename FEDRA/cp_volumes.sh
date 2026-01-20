#!/bin/bash
xmin=200000
ymin=4500
cell=10000
SIMFOLDER=/eos/experiment/sndlhc/users/dancc/FEDRA/muon_regenRUN1/cell_reco/

for CELL in $(seq 0 323); do
  i=$((CELL % 18))
  j=$((CELL / 18))
  xpos=$((xmin + (i * cell) + cell/2))
  ypos=$((ymin + (j * cell) + cell/2))
  xcell=$(((i + 1)*10))
  ycell=$(((j + 1)*10))

  folder=cell_${xcell}_${ycell}
  cd $folder/b000021/
  
  cp ${SIMFOLDER}/edipoda.sh .
  cp ${SIMFOLDER}/vertex_edi.rootrc .
  
  cd ../../
done
