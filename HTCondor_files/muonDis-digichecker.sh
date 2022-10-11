#!/bin/bash
RED=$'\033[0;31m' #Red coloring                                                                                                                                                  
NC=$'\033[0m' #No coloring
ABS_path=$(pwd)
ClusID=$1
faildir=/afs/cern.ch/work/d/dannc/public/HTC_failedjobs
COUNTER=0

for dir1 in muonDis_2{01..10}
do
	for i in {1..46}
	do
		cd $dir1/$i
		SIMFILE="sndLHC.muonDIS-TGeant4-"$dir1"_dig.root"
		if [ ! -f "$SIMFILE" ]
			then  
			echo "${RED}++ $SIMFILE doesn't exist in: $(pwd)!++${NC}"
			let COUNTER++
			if [ "$ClusID" ]
			then
				echo $((i-1)) $dir1 >> $faildir/fail.$ClusID.dat
				
			fi
		fi
	cd $ABS_path
	done
done
for dir2 in muonDis_5{01..10}
do
	for i in {1..46}
	do
		cd $dir2/$i
		SIMFILE="sndLHC.muonDIS-TGeant4-"$dir2"_dig.root"
		if [ ! -f "$SIMFILE" ]
			then  
			echo "${RED}++ $SIMFILE doesn't exist in: $(pwd)!++${NC}"
			let COUNTER++
			if [ "$ClusID" ]
			then
				echo $((i-1)) $dir2 >> $faildir/fail.$ClusID.dat
			fi
		fi
	cd $ABS_path
	done
done
echo "WARN: There are ${RED}$COUNTER${NC} failed jobs"
