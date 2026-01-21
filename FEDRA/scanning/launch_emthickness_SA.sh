#!/bin/bash
#source ~/fedraload_root_new.sh
RED=$'\033[0;31m' #Red coloring
NC=$'\033[0m' #No coloring
MIC=1
BRICK=11
RUN=5
WALL=$((BRICK / 10))
BID=$((BRICK % 10))
THEPATH=""
TOPLATE=$1
FROMPLATE=$2
RESCAN=$3
PLOTPATH=$(printf "/eos/user/s/snd2cern/emu_reco_plots/RUN%d" "$RUN")
NEW_PLOTPATH="/eos/user/e/emuplot/emuprogress/scanning/"
if [[ " 1 3 5 9 11 " =~ " $RUN " ]]; then
    kRun=1.5
elif [[ " 2 4 8 10 " =~ " $RUN " ]]; then
    kRun=4
fi


if [ "$MIC" == "1" ]; then
    THEPATH="/eos/experiment/sndlhc/emulsionData/Santiago/mic1/RUN${RUN}/RUN${RUN}_W${WALL}_B${BID}"
    #cp quality.rootrc quality.rootrc
else
    THEPATH="/eos/experiment/sndlhc/emulsionData/Santiago/mic${MIC}/RUN${RUN}/RUN${RUN}_W${WALL}_B${BID}"
    #cp quality.rootrc quality.rootrc
fi

prof_destpath=$(printf "%s/b%06d/profile/" "$PLOTPATH" "$BRICK")
if [ ! -d "$prof_destpath" ]; then
    mkdir -p "$prof_destpath"
fi
thick_path=$(printf "%s/b%06d/thickness/" "$PLOTPATH" "$BRICK")
if [ ! -d "$thick_path" ]; then
    mkdir -p "$thick_path"
fi
for (( i=FROMPLATE; i<=TOPLATE; i++ )); do
    if [ "$RESCAN" == "0" ]; then
        file=$(printf "%s/P%d/tracks.raw.root" "$THEPATH" "$i")
        destpath=$(printf "%s/b%06d/thickness/thickness_plate_%i" "$PLOTPATH" "$BRICK" "$i")
	new_destpath=$(printf "%s/RUN%i_W%i_B%i_P%03d" "$NEW_PLOTPATH" "$RUN" "$WALL" "$BID" "$i")
        if [ ! -f "$file" ]; then
          echo "${RED}++${NC} Skipping: $file does not exist ${RED}++${NC}"
          continue
        fi
    elif [ "$RESCAN" == "1" ]; then
        file=$(printf "%s/P%d_rescan/tracks.raw.root" "$THEPATH" "$i")
        destpath=$(printf "%s/b%06d/thickness/thickness_plate_%i_rescan" "$PLOTPATH" "$BRICK" "$i")
	new_destpath=$(printf "%s/RUN%i_W%i_B%i_P%03d_rescan" "$NEW_PLOTPATH" "$RUN" "$WALL" "$BID" "$i")
        if [ ! -f "$file" ]; then
          echo "${RED}++${NC} Skipping: $file does not exist, trying to find the _rescan1 ${RED}++${NC}"
	  file=$(printf "%s/P%d_rescan%d/tracks.raw.root" "$THEPATH" "$i" "$RESCAN")
	  destpath=$(printf "%s/b%06d/thickness/thickness_plate_%i_rescan%d" "$PLOTPATH" "$BRICK" "$i" "$RESCAN")
	  new_destpath=$(printf "%s/RUN%i_W%i_B%i_P%03d_rescan" "$NEW_PLOTPATH" "$RUN" "$WALL" "$BID" "$i")
	  if [ ! -f "$file" ]; then
	    echo "${RED}++${NC} Skipping: $file does not exist ${RED}++${NC}"
	    continue
	  fi
        fi
    else
        file=$(printf "%s/P%d_rescan%d/tracks.raw.root" "$THEPATH" "$i" "$RESCAN")
        destpath=$(printf "%s/b%06d/thickness/thickness_plate_%i_rescan%d" "$PLOTPATH" "$BRICK" "$i" "$RESCAN")
	new_destpath=$(printf "%s/RUN%i_W%i_B%i_P%d_rescan%d" "$NEW_PLOTPATH" "$RUN" "$WALL" "$BID" "$i" "$RESCAN")
        if [ ! -f "$file" ]; then
          echo "${RED}++${NC} Skipping: $file does not exist ${RED}++${NC}"
          continue
        fi
    fi
    #echo "File is ${file}"
    #echo "And destpath is ${destpath}"
    if [ -f "${prof_destpath}/$(basename "${destpath}").prof.png" ]; then
	    #echo "Profile of plate ${i} exists showing profile and thickness"
	    echo "Profile of plate ${i} exists, skipping"
	    #eog "${prof_destpath}/$(basename "${destpath}").prof.png" &
	    #eog "${destpath}.png" &
    else
    	emthickness -input=${file} -out=${destpath} -v=1 -r=${kRun}
    	#eog "${destpath}.png" &
    	mv ${thick_path}/*.prof.png ${prof_destpath}
    	#eog "${prof_destpath}/$(basename "${destpath}").prof.png" &
    fi
    #ln -s -f "${destpath}.png" "${new_destpath}.png"
    #ln -s -f "${destpath}.json" "${new_destpath}.json"
done
