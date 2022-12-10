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

void AdvSND_magnet_vol2(){

    TGeoBBox *mother = new TGeoBBox("mother", 1000, 1000, 1000);
	TGeoVolume *volMother = new TGeoVolume("volMother", mother, 0);

    Double_t fMuonSysPlaneX = 120.;     // cm
    Double_t fMuonSysPlaneY = 60.;      // cm
    Double_t fCutOffset     = 5.;       // cm
    Double_t fFeX           = 180.;     // cm
    Double_t fFeY           = 124.;     // cm
    Double_t fFeZ           = 8.;       // cm
    Double_t fFeGap         = 2.;       // cm
    Int_t    fNplanes       = 22;       // cm
    Double_t fCoilX         = fMuonSysPlaneX;
    Double_t fCoilY         = 2.;       // cm
    Double_t fCoilZ         = (fNplanes)*(fFeZ+fFeGap)-fFeGap;
    Double_t fFeYokeX       = (fFeX-fMuonSysPlaneX)/2.;
    Double_t fFeYokeY       = (fFeY-fMuonSysPlaneY-fCoilY)/2.;
    Double_t fFeCutX        = fFeYokeX - fCutOffset;
    Double_t fFeCutY        = fFeYokeY - fCutOffset;
    

    

    TGeoBBox *FeWall = new TGeoBBox("FeWall", fFeX/2., fFeY/2., fFeZ/2.);
    TGeoBBox *MuonSysPlane = new TGeoBBox("MuonSysPlane", fMuonSysPlaneX/2., fMuonSysPlaneY/2., fFeZ/2.+0.001);
    TGeoBBox *CoilSpace = new TGeoBBox("CoilSpace", fCoilX/2., fCoilY/2.+0.005, fFeZ/2.+0.05);
    TGeoBBox *Coil = new TGeoBBox("Coil", fCoilX/2., fCoilY/2., fCoilZ/2.);
    TGeoBBox *MuonSysDet = new TGeoBBox("MuonSysDet", fMuonSysPlaneX/2., fMuonSysPlaneY/2., fFeGap/2.);

    Double_t cutvers[8][2];
    cutvers[0][0] = 0;
    cutvers[0][1] = 0;
    cutvers[1][0] = 0;
    cutvers[1][1] = -fFeCutY;
    cutvers[2][0] = 0;
    cutvers[2][1] = -fFeCutY;
    cutvers[3][0] = +fFeCutX;
    cutvers[3][1] = 0;

    cutvers[4][0] = 0;
    cutvers[4][1] = 0;
    cutvers[5][0] = 0;
    cutvers[5][1] = -fFeCutY;
    cutvers[6][0] = 0;
    cutvers[6][1] = -fFeCutY;
    cutvers[7][0] = +fFeCutX;
    cutvers[7][1] = 0;
    TGeoArb8 *FeCut = new TGeoArb8("FeCut", fFeZ/2.+0.001, (Double_t *)cutvers);

    TGeoTranslation *CutUpRight = new TGeoTranslation("CutUpRight", -fFeX/2.-0.001, fFeY/2.+0.001, 0);
    CutUpRight->RegisterYourself();
    TGeoCombiTrans *CutDownRight = new TGeoCombiTrans( TGeoTranslation(-fFeX/2.-0.001, -fFeY/2.-0.001, 0), TGeoRotation("rot", 0, 0, 90));
    CutDownRight->SetName("CutDownRight");
    CutDownRight->RegisterYourself();
    TGeoCombiTrans *CutDownLeft = new TGeoCombiTrans(TGeoTranslation(+fFeX/2.+0.001, -fFeY/2.-0.001, 0), TGeoRotation("rot1", 0, 0, 180));
    CutDownLeft->SetName("CutDownLeft");
    CutDownLeft->RegisterYourself();
    TGeoCombiTrans *CutUpLeft = new TGeoCombiTrans(TGeoTranslation(+fFeX/2.+0.001, +fFeY/2.+0.001, 0), TGeoRotation("rot2", 0, 0, -90));
    CutUpLeft->SetName("CutUpLeft");
    CutUpLeft->RegisterYourself();


    TGeoTranslation *CoilUp = new TGeoTranslation("CoilUp", 0, fMuonSysPlaneY/2.+fCoilY/2., 0);
    TGeoTranslation *CoilDown = new TGeoTranslation("CoilDown", 0, -fMuonSysPlaneY/2.-fCoilY/2., 0);
    CoilUp->RegisterYourself();
    CoilDown->RegisterYourself();

    TGeoCompositeShape *MuonSysFe = new TGeoCompositeShape("MuonSysFe", "FeWall-MuonSysPlane-(CoilSpace:CoilUp)-(CoilSpace:CoilDown)-(FeCut:CutUpRight)-(FeCut:CutDownRight)-(FeCut:CutDownLeft)-(FeCut:CutUpLeft)");
    TGeoVolume *volFeWall = new TGeoVolume("volFeWall", MuonSysFe, 0);
    TGeoVolume *volMagFe = new TGeoVolume("volMagFe", MuonSysPlane, 0);
    volFeWall->SetLineColor(kGreen-4);
    volMagFe->SetLineColor(kGreen);
    
    Double_t fField = 1.5; // Tesla
    TGeoUniformMagField *magField = new TGeoUniformMagField(-fField,0, 0);
    volMagFe->SetField(magField);

    TGeoVolume *volCoil = new TGeoVolume("volCoil", Coil, 0);
    volCoil->SetLineColor(kOrange+1);

    TGeoVolume *volMuonSysDet = new TGeoVolume("volMuonSysDet", MuonSysDet, 0);
    volMuonSysDet->SetLineColor(kGray-2);

    for(int i = 0; i<fNplanes; i++)
    {
        volMother->AddNode(volFeWall, i, new TGeoTranslation(0, 0, i*(fFeZ+fFeGap)));
        volMother->AddNode(volMagFe, i, new TGeoTranslation(0, 0, i*(fFeZ+fFeGap)));
        if (i == fNplanes-1) continue;
        volMother->AddNode(volMuonSysDet, i, new TGeoTranslation(0, 0, (fFeZ+fFeGap)/2.+i*(fFeZ+fFeGap)));
    }
    volMother->AddNode(volCoil, 0, new TGeoTranslation(0, fMuonSysPlaneY/2.+fCoilY/2., fCoilZ/2.-fFeZ/2.));
    volMother->AddNode(volCoil, 1, new TGeoTranslation(0, -fMuonSysPlaneY/2.-fCoilY/2., fCoilZ/2.-fFeZ/2.));

    // Second magnet part
    Double_t fNplanes2 = 20;
    Double_t fMagnetsGap = 90+2.5; // cm
    Double_t FirstMagZ = fNplanes*(fFeZ+fFeGap);
    Double_t fShortCoilZ = fNplanes2*fFeZ;

    TGeoBBox *ShortCoil = new TGeoBBox("ShortCoil", fCoilX/2., fCoilY/2., fShortCoilZ/2.);
    TGeoVolume *volShortCoil = new TGeoVolume("volShortCoil", ShortCoil, 0);
    volShortCoil->SetLineColor(kOrange+1);


    for(int i = 0; i< 20; i++)
    {
        volMother->AddNode(volFeWall, i, new TGeoTranslation(0, 0, FirstMagZ+fMagnetsGap+i*fFeZ-fFeGap));
        volMother->AddNode(volMagFe, i, new TGeoTranslation(0, 0, FirstMagZ+fMagnetsGap+i*fFeZ-fFeGap));
    }
    volMother->AddNode(volShortCoil, 0, new TGeoTranslation(0, fMuonSysPlaneY/2.+fCoilY/2., fShortCoilZ/2.-fFeZ/2.+fMagnetsGap+FirstMagZ-fFeGap));
    volMother->AddNode(volShortCoil, 1, new TGeoTranslation(0, -fMuonSysPlaneY/2.-fCoilY/2., fShortCoilZ/2.-fFeZ/2.+fMagnetsGap+FirstMagZ-fFeGap));


    // Trackers part
    Double_t fMagTrackerZ = 2.5; // cm Alu tubes diameter
    TGeoBBox *MagTracker = new TGeoBBox("MagTracker", fMuonSysPlaneX/2., fMuonSysPlaneY/2., fMagTrackerZ/2.);
    TGeoVolume *volMagTracker = new TGeoVolume("volMagTracker", MagTracker, 0);
    volMagTracker->SetLineColor(kGray);

    volMother->AddNode(volMagTracker, 0, new TGeoTranslation(0, 0, FirstMagZ-fFeZ/2.-fFeGap+fMagTrackerZ/2.));
    volMother->AddNode(volMagTracker, 1, new TGeoTranslation(0, 0, FirstMagZ-fFeZ/2.-fFeGap+fMagnetsGap-fMagTrackerZ/2.));
    volMother->AddNode(volMagTracker, 2, new TGeoTranslation(0, 0, FirstMagZ-fFeZ/2.-fFeGap+fMagnetsGap+fShortCoilZ+fMagTrackerZ/2.));



volMother->Draw("ogl");
}

