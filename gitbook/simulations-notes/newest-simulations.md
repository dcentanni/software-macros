# Newest 𝜈 simulations

This section will deal with the simulation of all flavour neutrino interactions within the SND@LHC software environment.

This recipe will require at a first step a `.gsimple` root file containing informations about incoming neutrinos from FLUKA simulations (_FLUKA to gsimple part to be written_) and a geometry file in `GDML` format converted from `.root` file.

{% hint style="info" %}
`.gsimple` neutrino files can be found in `/eos/experiment/sndlhc/MonteCarlo/FLUKA/neutrino_up_13TeV/`
{% endhint %}

## Convert .root geometry file to .gdml file

The first step is to convert the geometry file containing all of the volumes involved in the simulation to the gdml format. This can be achieved in python with [this](https://github.com/dcentanni/software-macros/blob/main/AdvSND-macros/makeGDML.py) script or alternatively in C++ with:

```cpp
TFile * f = new TFile("<geofile>.root")
TGeoManager * geo = (TGeoManager*) f->Get("FAIRGeom")
geo->Export("<geofile>.gdml")
```

## Create .ghep file with GENIE

Once the `.gdml` geometry file has been obtained, GENIE can be used in order to generate the a `.ghep` file which will be needed by `sndsw` in order to propagate neutrino interactions. So one can run the following command from GENIE:

```bash
gevgen_fnal -f "${GSIMPLE_FLUX},,-12,12,-14,14,-16,16" 
            -g $GEOFILE 
            -t ${TARGET}  
            -L "cm" -D "g_cm3" 
            -n $NEVENTS # or alternatively -e $INTLUMI
            -o ${OUTFILE} 
            --tune ${TUNE} 
            --cross-sections ${SPLINESFILE}.xml 
            --message-thresholds $GENIE/config/Messenger_laconic.xml 
            --seed ${SEED}
```

In particular this will issue a `.ghep` file including `${NEVENTS}` within the `${TARGET}` volume using the `${SPLINEFILE}` with the `${TUNE}` specified

A more detailed description of the arguments accepted by `gevgen_fnal` can be found here:

{% embed url="https://internal.dunescience.org/doxygen/gFNALExptEvGen_8cxx_source.html" %}
Source file from GENIE
{% endembed %}

