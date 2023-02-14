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

void AdvSND_target(){

    TGeoBBox *mother = new TGeoBBox("mother", 1000, 1000, 1000);
	TGeoVolume *volMother = new TGeoVolume("volMother", mother, 0);

    Double_t fTargetWallX = 100.0; //cm
    Double_t fTargetWallY = 40.0; // cm
    Double_t fTargetWallZ = 17; // cm
    Double_t fTTX = fTargetWallX;
    Double_t fTTY = fTargetWallY;
    Double_t fTTZ = 3; //cm
    Int_t fnTT = 5;

    TGeoBBox *TargetWall = new TGeoBBox("TargetWall", fTargetWallX/2., fTargetWallY/2., fTargetWallZ/2.);
    TGeoBBox *TTracker = new TGeoBBox("TTracker", fTTX/2., fTTY/2., fTTZ/2.);

    TGeoVolume *volTargetWall = new TGeoVolume("volTargetWall", TargetWall, 0);
    TGeoVolume *volTTracker = new TGeoVolume("volTTracker", TTracker, 0);

    volTargetWall->SetLineColor(kYellow-4);
     volTTracker->SetLineColor(kGray);
 
    for(int i=0; i<fnTT; i++)
    {
        volMother->AddNode(volTargetWall, i, new TGeoTranslation(0, 0, -fnTT*(fTargetWallZ+fTTZ)/2.+fTargetWallZ/2.+i*(fTargetWallZ+fTTZ)));
        volMother->AddNode(volTTracker, i, new TGeoTranslation(0, 0, -fnTT*(fTargetWallZ+fTTZ)/2.+fTargetWallZ+fTTZ/2+i*(fTargetWallZ+fTTZ)));
    }



    volMother->Draw("ogl");
}