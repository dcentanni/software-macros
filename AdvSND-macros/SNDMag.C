#include "TGeoManager.h"
#include "TGeoBBox.h"
#include "TGeoMaterial.h"
#include "TGeoMedium.h"
#include "TGeoPara.h" 
#include "TMath.h"
#include "TGeoCompositeShape.h"
#include "TGeoArb8.h"
#include "TVector3.h"
#include "TGeoTrd2.h"
#include "TGeoUniformMagField.h"

void SNDMag(){

	// MAGNET STRUCTURE

	Double_t fInMagX = 120; // cm
	Double_t fInMagY = 60; // cm
	Double_t fIronYokeX = 30; // cm
	Double_t fIronYokeY = 25; // cm
	Double_t fCoilX = fInMagX;
	Double_t fCoilY = 23; // cm
	Double_t fOutMagX = fInMagX + 2*fIronYokeX;
	Double_t fOutMagY = fInMagY + 2*(fCoilY+fIronYokeY);
	Double_t fMagZ = 200; // cm

	TGeoBBox *mother = new TGeoBBox("mother", 1000, 1000, 1000);
	TGeoVolume *volMother = new TGeoVolume("volMother", mother, 0);

	// Shapes creation
	TGeoBBox *CoilContainer = new TGeoBBox("CoilContainer", fOutMagX/2., fOutMagY/2., fMagZ/2.);
	TGeoBBox *MagRegion = new TGeoBBox("MagRegion", fInMagX/2., fInMagY/2., fMagZ/2.+0.5);
	TGeoBBox *Coil = new TGeoBBox("Coil", fCoilX/2., fCoilY/2., fMagZ/2.+0.5);

	// Translations
	TGeoTranslation *MagRegionpos = new TGeoTranslation("MagRegionpos", 0, 0, 0);
	TGeoTranslation *CoilUpPos = new TGeoTranslation("CoilUpPos", 0, (fInMagY+fCoilY)/2.-0.001, 0);
	TGeoTranslation *CoilDownPos = new TGeoTranslation("CoilDownPos", 0, -(fInMagY+fCoilY)/2.+0.001, 0);
	CoilUpPos->RegisterYourself();
	CoilDownPos->RegisterYourself();
	MagRegionpos->RegisterYourself();


	// Yoke shape
	TGeoCompositeShape *FeYoke = new TGeoCompositeShape("FeYoke", "CoilContainer-MagRegion-(Coil:CoilUpPos)-(Coil:CoilDownPos)");

	// Volumes
	TGeoVolume *volFeYoke = new TGeoVolume("volFeYoke", FeYoke, 0);
	volFeYoke->SetLineColor(kGray);
	TGeoVolume *volCoil = new TGeoVolume("volCoil", Coil, 0);
	volCoil->SetLineColor(kOrange+1);

	// Positioning
	volMother->AddNode(volFeYoke, 0);
	volMother->AddNode(volCoil, 0, new TGeoTranslation(0, (fInMagY+fCoilY)/2., 0));
	volMother->AddNode(volCoil, 1, new TGeoTranslation(0, -(fInMagY+fCoilY)/2., 0));
	

	// TRACKING STATIONS STRUCTURE
	Double_t fTrackerZ = 0.5; //cm
	Double_t fTSpacingZ = 2; // cm
	Double_t fLevArm = 100; // cm

	TGeoBBox *TrackPlane = new TGeoBBox("TrackPlane", fInMagX/2., fInMagY/2., fTrackerZ/2.);

	TGeoVolume *volTrackPlane = new TGeoVolume("volTrackPlane", TrackPlane, 0);
	volTrackPlane->SetLineColor(kBlue);
	volTrackPlane->SetTransparency(60);

	volMother->AddNode(volTrackPlane, 0, new TGeoTranslation(0, 0, -fMagZ/2.-fTSpacingZ-fTrackerZ/2.));
	volMother->AddNode(volTrackPlane, 1, new TGeoTranslation(0, 0, +fMagZ/2.+fTSpacingZ+fTrackerZ/2.));
	volMother->AddNode(volTrackPlane, 2, new TGeoTranslation(0, 0, -fMagZ/2.-fTSpacingZ-fTrackerZ-fLevArm-fTrackerZ/2.));
	volMother->AddNode(volTrackPlane, 3, new TGeoTranslation(0, 0, +fMagZ/2.+fTSpacingZ+fTrackerZ+fLevArm+fTrackerZ/2.));
	

	// MAGNETIC FIELD

	Double_t fField = 1; // Tesla

	TGeoUniformMagField *magField = new TGeoUniformMagField(-fField,0, 0);
	TGeoVolume *volMagRegion = new TGeoVolume("volMagRegion", MagRegion, 0);
	volMagRegion->SetField(magField);


	volMother->Draw("ogl");
}


