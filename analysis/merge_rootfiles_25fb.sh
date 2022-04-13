ClusterId=$1
echo "Moving to outputdir"
cd /afs/cern.ch/work/d/dannc/public/histo_saves/
echo "Merging root files"
hadd $ClusterId.histos_N1_20_dig_total_25fb.root $ClusterId.histos_N1_20_dig_ev0to10000_25fb.root $ClusterId.histos_N1_20_dig_ev10000to20000_25fb.root $ClusterId.histos_N1_20_dig_ev20000to30000_25fb.root $ClusterId.histos_N1_20_dig_ev30000to40000_25fb.root $ClusterId.histos_N1_20_dig_ev40000to50000_25fb.root $ClusterId.histos_N1_20_dig_ev50000to60000_25fb.root $ClusterId.histos_N1_20_dig_ev60000to70000_25fb.root $ClusterId.histos_N1_20_dig_ev70000to80000_25fb.root $ClusterId.histos_N1_20_dig_ev80000to90000_25fb.root $ClusterId.histos_N1_20_dig_ev90000to94120_25fb.root
echo "Merge complete!"
echo "Copying to eos dir"
cp $ClusterId.histos_N1_20_dig_total.root /eos/user/d/dannc/SND_sim/histo_saves/
echo "Copy complete!"



