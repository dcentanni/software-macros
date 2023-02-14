#!/bin/bash

python $SNDSW_ROOT/shipLHC/makeGeoFile.py -c $SNDSW_ROOT/geometry/AdvSND_geom_config.py -g /eos/user/d/dannc/AdvSND/geofiles/geofile.$(date +'%d%m%y').root
