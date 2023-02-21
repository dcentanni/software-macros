#!/bin/bash

RED=$'\033[0;31m' #Red coloring                                                                                                                                                  
NC=$'\033[0m' #No coloring
filename=vertextree.root
neutrinofile=$1
brickIDs=(11 12 13 14 21 22 23 24 31 32 33 34 41 42 43 44 51 52 53 54)

for ibrick in $(seq 0 19)
	do
		cd b0000${brickIDs[ibrick]}
	 	if [ ! -f "$filename" ]
	 		then  
	 			echo "${RED}++$filename doesn't exist in: $(pwd)! Skipping++${NC}"
	 			cd .. 
	 			continue
		fi
		if [[ "$neutrinofile" == "1" ]]
			then
		    	echo "+++ Analysing neutrino file in $(pwd) +++"
		    	root -l -q /home/simsndlhc/macros-snd/FEDRA/vtx_analysis.C\(${brickIDs[ibrick]},1,0\)
		    	cd ..
		    else
		    	echo "+++ Analysing bkg file in $(pwd) +++"
		    	root -l -q /home/simsndlhc/macros-snd/FEDRA/vtx_analysis.C\(${brickIDs[ibrick]},0,0\)
		    	cd ..
		fi
done
echo "++ Now merging all histos.. ++"
hadd -f hvtx.allbricks.root b0000*/hvtx*
root -l -q ~/macros-snd/FEDRA/doNormHistos.C
echo "++ Now merging TMVA input variables ++"
if [[ "$neutrinofile" == "1" ]]
	then
		hadd -f OUTvar_sig.root b0000*/b0000*.OUTvar_sig.root
	else
		hadd -f OUTvar_bkg.root b0000*/b0000*.OUTvar_bkg.root
fi
