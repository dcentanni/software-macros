#!/bin/bash
RED=$'\033[0;31m' #Red coloring                                                                                                                                                  
NC=$'\033[0m' #No coloring

mother_dir=$(pwd)

for i in {1..46}
do
	cd $mother_dir/$i
	SIMFILE=$(ls sndLHC.muonDIS-TGeant4-*.root)
	GEOFILE=$(ls geofile_full.muonDIS-TGeant4-*.root)
	PARFILE=$(ls ship.params.muonDIS-TGeant4-*.root)
	if [ ! -f "$SIMFILE" ]
		then  
		echo "${RED}++ SIMFILE doesn't exist in: $(pwd)!++${NC}"
	fi
	if [ ! -f "$GEOFILE" ]
                then
                echo "${RED}++ GEOFILE doesn't exist in: $(pwd)!++${NC}"
        fi
	if [ ! -f "$PARFILE" ]
                then
                echo "${RED}++ PARFILE doesn't exist in: $(pwd)!++${NC}"
        fi
	cd $mother_dir
done
