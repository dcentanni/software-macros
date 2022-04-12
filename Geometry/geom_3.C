#include "TGeoManager.h"
#include "TGeoBBox.h"
#include "TGeoMaterial.h"
#include "TGeoMedium.h"
#include "TGeoPara.h" 
#include "TMath.h"
#include "TGeoCompositeShape.h"
#include "TGeoArb8.h"

void geom_3(){

	Float_t Acrylic_width		= 5.0; 		// cm
	Float_t BPoly_width			= 4.0; 		// cm
    Float_t CBFrontWall_xdim	= 219.;		// cm
	Float_t CBFrontWall_ydim	= 170.72-Acrylic_width; 	// cm
	Float_t CBLatWall_zdim		= 176.0; 	// cm
	Float_t CBTiny_zdim			= 17.0; 	// cm
	Float_t CBExtra_zdim		= 41.0;		// cm
	Float_t CBExtra_xdim		= 67.5;		// cm
	Float_t SlopedWall_zproj	= 110.0;	// cm	
	Float_t CBRearWall_xdim		= CBFrontWall_xdim-SlopedWall_zproj*TMath::Tan(TMath::DegToRad()*15.)-CBExtra_xdim+Acrylic_width;

    Float_t FeX		= 80.;
	Float_t FeY		= 60.;
	Float_t FeZ		= 20.;

    TGeoBBox *mother = new TGeoBBox("mother", 1000, 1000, 1000);
    TGeoVolume *volMother = new TGeoVolume("volMother", mother, 0);
	TGeoVolumeAssembly *volColdBox = new TGeoVolumeAssembly("volColdBox");

    // ************************ ACRYLIC
    // Shapes definition
    TGeoBBox *FeBlock 		    = new TGeoBBox("FeBlock",FeX/2, FeY/2, FeZ/2);
	TGeoBBox *CBFrontWall_a 	= new TGeoBBox("CBFrontWall_a", CBFrontWall_xdim/2., CBFrontWall_ydim/2., Acrylic_width/2.);
	TGeoBBox *CBLateral_a 		= new TGeoBBox("CBLateral_a", Acrylic_width/2., CBFrontWall_ydim/2., (CBLatWall_zdim-2*Acrylic_width)/2.);
	TGeoBBox *CBExtraFront_a	= new TGeoBBox("CBExtraFront_a", CBExtra_xdim/2., CBFrontWall_ydim/2., Acrylic_width/2.);
	TGeoBBox *CBExtraLat_a		= new TGeoBBox("CBExtraLat_a", Acrylic_width/2., CBFrontWall_ydim/2., (CBExtra_zdim-2*Acrylic_width)/2.);
	TGeoBBox *CBTiny1_a			= new TGeoBBox("CBTiny1_a", Acrylic_width/2., CBFrontWall_ydim/2., (CBTiny_zdim-Acrylic_width-BPoly_width)/2.);
	TGeoBBox *CBTiny2_a			= new TGeoBBox("CBTiny2_a", Acrylic_width/2., CBFrontWall_ydim/2., (CBTiny_zdim-Acrylic_width)/2.);
	TGeoBBox *CBRearWall_a		= new TGeoBBox("CBRearWall_a", CBRearWall_xdim/2., CBFrontWall_ydim/2., Acrylic_width/2.);

    TGeoTranslation *CBWallpos = new TGeoTranslation("CBWallpos", (CBRearWall_xdim-FeX)/2. - 28.5, (FeY-CBFrontWall_ydim)/2., 0);
	CBWallpos->RegisterYourself();

	TGeoCompositeShape *CBWallDownstream = new TGeoCompositeShape("CBWallDownstream", "CBRearWall_a-(FeBlock:CBWallpos)");
    TGeoVolume *volCBWallDown = new TGeoVolume("volCBWallDown", CBWallDownstream, 0);

    TGeoPara *CBWallSlope_a = new TGeoPara("CBWallSlope_a", Acrylic_width/2., CBFrontWall_ydim/2., SlopedWall_zproj/2., 0, -15, 0);
	//TGeoVolume *volCBWallSlope_a = new TGeoVolume("volCBWallSlope_a", CBWallSlope_a, 0);

    // Acrylic mother shape definition
    TGeoTranslation *FrontWallpos = new TGeoTranslation("FrontWallpos", -CBRearWall_xdim/2.-CBExtra_xdim+Acrylic_width+CBFrontWall_xdim/2., 0, -(SlopedWall_zproj+2*(CBTiny_zdim-Acrylic_width)+Acrylic_width)+BPoly_width);
	FrontWallpos->RegisterYourself();
	TGeoTranslation *Tiny1pos = new TGeoTranslation("Tiny1pos", (CBRearWall_xdim-Acrylic_width)/2., 0, -CBTiny_zdim/2.+BPoly_width/2.);
	Tiny1pos->RegisterYourself();
	TGeoTranslation *SlopeWallpos = new TGeoTranslation("SlopeWallpos", (CBRearWall_xdim+Acrylic_width)/2.+Acrylic_width+SlopedWall_zproj/(2*TMath::Tan(TMath::DegToRad()*85.)),0, -CBTiny_zdim-SlopedWall_zproj/2.+Acrylic_width/2.+BPoly_width);
	SlopeWallpos->RegisterYourself();
	TGeoTranslation *Tiny2pos = new TGeoTranslation("Tiny2pos", 3*Acrylic_width+CBRearWall_xdim/2.+Acrylic_width/2.+SlopedWall_zproj/(TMath::Tan(TMath::DegToRad()*85.)), 0, -(SlopedWall_zproj+2*(CBTiny_zdim-Acrylic_width)+Acrylic_width)+CBTiny_zdim/2.+BPoly_width);
	Tiny2pos->RegisterYourself();
	TGeoTranslation *CBExtraLatpos = new TGeoTranslation("CBExtraLatpos", -CBRearWall_xdim/2.+Acrylic_width/2., 0, Acrylic_width/2.+(CBExtra_zdim-2*Acrylic_width)/2.);
	CBExtraLatpos->RegisterYourself();
	TGeoTranslation *CBExtraFrontpos = new TGeoTranslation("CBExtraFrontpos", -CBRearWall_xdim/2.+Acrylic_width-CBExtra_xdim/2., 0, CBExtra_zdim-Acrylic_width);
	CBExtraFrontpos->RegisterYourself();
	TGeoTranslation *CBLateralpos = new TGeoTranslation("CBLateralpos", -CBRearWall_xdim/2.-CBExtra_xdim+Acrylic_width+Acrylic_width/2., 0, CBExtra_zdim-CBLatWall_zdim/2.-Acrylic_width/2.);
	CBLateralpos->RegisterYourself();
    
    // Acrylic mother volume definition
    TGeoCompositeShape *COLDBOXA = new TGeoCompositeShape("COLDBOXA", "CBWallDownstream+(CBFrontWall_a:FrontWallpos)+(CBTiny1_a:Tiny1pos)+(CBWallSlope_a:SlopeWallpos)+(CBTiny2_a:Tiny2pos)+(CBExtraLat_a:CBExtraLatpos)+(CBExtraFront_a:CBExtraFrontpos)+(CBLateral_a:CBLateralpos)");
	TGeoVolume *volCOLDBOXA = new TGeoVolume("volCOLDBOXA", COLDBOXA, 0);
    volColdBox->AddNode(volCOLDBOXA, 0, 0);

    // ************************ BORATED POLYETHYLENE
    Float_t CBFrontWall_xdim_b	= CBFrontWall_xdim-2*Acrylic_width-BPoly_width;		// cm
	Float_t CBFrontWall_ydim_b	= CBFrontWall_ydim-BPoly_width;
	Float_t CBLatWall_zdim_b	= CBLatWall_zdim-2*Acrylic_width; 	// cm
	Float_t CBExtra_xdim_b		= CBExtra_xdim-2*Acrylic_width;		// cm
	Float_t CBRearWall_xdim_b	= CBRearWall_xdim-Acrylic_width;
    // Shapes definition
    TGeoBBox *CBFrontWall_b 	= new TGeoBBox("CBFrontWall_b", CBFrontWall_xdim_b/2.+(Acrylic_width-BPoly_width)/10., CBFrontWall_ydim_b/2., BPoly_width/2.); // (Acrylic_width-BPoly_width)/10. is due to approximations, I guess
	TGeoBBox *CBLateral_b 		= new TGeoBBox("CBLateral_b", BPoly_width/2., CBFrontWall_ydim_b/2., (CBLatWall_zdim-2*BPoly_width)/2.-Acrylic_width);
	TGeoBBox *CBExtraFront_b	= new TGeoBBox("CBExtraFront_b", CBExtra_xdim_b/2., CBFrontWall_ydim_b/2., BPoly_width/2.);
	TGeoBBox *CBExtraLat_b		= new TGeoBBox("CBExtraLat_b", BPoly_width/2., CBFrontWall_ydim_b/2., (CBExtra_zdim-Acrylic_width-BPoly_width)/2.);
	TGeoBBox *CBTiny1_b			= new TGeoBBox("CBTiny1_b", BPoly_width/2., CBFrontWall_ydim_b/2., (CBTiny_zdim-Acrylic_width-BPoly_width)/2.);
	TGeoBBox *CBTiny2_b			= new TGeoBBox("CBTiny2_b", BPoly_width/2., CBFrontWall_ydim_b/2., (CBTiny_zdim-Acrylic_width)/2.);
	TGeoBBox *CBRearWall_b		= new TGeoBBox("CBRearWall_b", CBRearWall_xdim_b/2., CBFrontWall_ydim_b/2., BPoly_width/2.);

    TGeoPara *CBWallSlope_b = new TGeoPara("CBWallSlope_b", BPoly_width/2., CBFrontWall_ydim_b/2., SlopedWall_zproj/2., 0, -15, 0);
	//TGeoVolume *volCBWallSlope_b = new TGeoVolume("volCBWallSlope_b", CBWallSlope_b, 0);

    // Borated Polyethylene mother shape definition
    TGeoTranslation *FrontWallpos_b = new TGeoTranslation("FrontWallpos_b", -CBRearWall_xdim_b/2.-CBExtra_xdim_b+BPoly_width+CBFrontWall_xdim_b/2.+0.1, 0,-SlopedWall_zproj-(CBTiny_zdim-Acrylic_width+BPoly_width)); // +0.1 is due to approximations, I guess 
	FrontWallpos_b->RegisterYourself();
	TGeoTranslation *Tiny1pos_b = new TGeoTranslation("Tiny1pos_b", CBRearWall_xdim_b/2.+BPoly_width/2., 0, -BPoly_width/2.);
	Tiny1pos_b->RegisterYourself();
	TGeoTranslation *SlopeWallpos_b = new TGeoTranslation("SlopeWallpos_b", SlopedWall_zproj/(2*TMath::Tan(TMath::DegToRad()*85.))+CBRearWall_xdim_b/2.+3*BPoly_width,0, -BPoly_width/2.-SlopedWall_zproj/2.-(CBTiny_zdim-Acrylic_width-BPoly_width)/2.);
	SlopeWallpos_b->RegisterYourself();
	TGeoTranslation *Tiny2pos_b = new TGeoTranslation("Tiny2pos_b", 5*BPoly_width+CBRearWall_xdim/2.+SlopedWall_zproj/(TMath::Tan(TMath::DegToRad()*85.))-(Acrylic_width-BPoly_width)/2., 0, -SlopedWall_zproj-(CBTiny_zdim-Acrylic_width));
	Tiny2pos_b->RegisterYourself();
	TGeoTranslation *CBExtraLatpos_b = new TGeoTranslation("CBExtraLatpos_b", -CBRearWall_xdim_b/2.+BPoly_width/2., 0, (CBExtra_zdim-Acrylic_width)/2.);
	CBExtraLatpos_b->RegisterYourself();
	TGeoTranslation *CBExtraFrontpos_b = new TGeoTranslation("CBExtraFrontpos_b", -CBRearWall_xdim_b/2.+BPoly_width-CBExtra_xdim_b/2., 0, CBExtra_zdim-Acrylic_width);
	CBExtraFrontpos_b->RegisterYourself();
	TGeoTranslation *CBLateralpos_b = new TGeoTranslation("CBLateralpos_b", -CBRearWall_xdim_b/2.-CBExtra_xdim_b+BPoly_width+BPoly_width/2., 0, CBExtra_zdim-CBLatWall_zdim_b/2.+BPoly_width/2.-Acrylic_width);
	CBLateralpos_b->RegisterYourself();
    
	// Borated Polyethylene mother volume definition
	TGeoCompositeShape *COLDBOXB = new TGeoCompositeShape("COLDBOXB","CBRearWall_b+(CBTiny1_b:Tiny1pos_b)+(CBExtraLat_b:CBExtraLatpos_b)+(CBWallSlope_b:SlopeWallpos_b)+(CBTiny2_b:Tiny2pos_b)+(CBExtraFront_b:CBExtraFrontpos_b)+(CBLateral_b:CBLateralpos_b)+(CBFrontWall_b:FrontWallpos_b)");
    TGeoVolume *volCOLDBOXB = new TGeoVolume("volCOLDBOXB", COLDBOXB, 0);
    volCOLDBOXB->SetLineColor(kBlue);
    volColdBox->AddNode(volCOLDBOXB, 0, new TGeoTranslation(-BPoly_width-Acrylic_width/2., -BPoly_width/2., -Acrylic_width/2.-BPoly_width/2.));

	// Acrylic Roof shape definition
	Double_t Roof4_averts [8][2];
	Roof4_averts[0][0] = 0.; Roof4_averts[0][1] = 0.;
	Roof4_averts[1][0] = 0.; Roof4_averts[1][1] = Acrylic_width;
	Roof4_averts[2][0] = SlopedWall_zproj*(TMath::Tan(TMath::DegToRad()*15.)); Roof4_averts[2][1] = Acrylic_width;
	Roof4_averts[3][0] = SlopedWall_zproj*(TMath::Tan(TMath::DegToRad()*15.)); Roof4_averts[3][1] = 0;
	Roof4_averts[4][0] = 0; Roof4_averts[4][1] = 0;
	Roof4_averts[5][0] = 0; Roof4_averts[5][1] = Acrylic_width;
	Roof4_averts[6][0] = 0; Roof4_averts[6][1] = Acrylic_width;
	Roof4_averts[7][0] = 0; Roof4_averts[7][1] = 0;
	
	TGeoBBox *CBRoof1_a 	= new TGeoBBox("CBRoof1_a", CBExtra_xdim/2., Acrylic_width/2., CBLatWall_zdim/2.);
	TGeoBBox *CBRoof2_a		= new TGeoBBox("CBRoof2_a", (CBRearWall_xdim-Acrylic_width)/2., Acrylic_width/2., (CBLatWall_zdim-CBExtra_zdim+Acrylic_width)/2.);
	TGeoBBox *CBRoof3_a		= new TGeoBBox("CBRoof3_a", (SlopedWall_zproj*(TMath::Tan(TMath::DegToRad()*15.)))/2., Acrylic_width/2., CBTiny_zdim/2.);
	TGeoArb8 *CBRoof4_a		= new TGeoArb8("CBRoof4_a", SlopedWall_zproj/2., (Double_t*) Roof4_averts);

	TGeoTranslation *Roof1_apos = new TGeoTranslation("Roof1_apos", -(CBRearWall_xdim-Acrylic_width)/2.-CBExtra_xdim/2., 0, CBExtra_zdim/2.-Acrylic_width/2.);
	Roof1_apos->RegisterYourself();
	TGeoTranslation *Roof3_apos = new TGeoTranslation("Roof3_apos", (CBRearWall_xdim-Acrylic_width)/2.+(SlopedWall_zproj*(TMath::Tan(TMath::DegToRad()*15.)))/2., 0, -(CBLatWall_zdim-CBExtra_zdim+Acrylic_width)/2.+CBTiny_zdim/2.);
	Roof3_apos->RegisterYourself();
	TGeoTranslation *Roof4_apos = new TGeoTranslation("Roof4_apos", (CBRearWall_xdim-Acrylic_width)/2., -Acrylic_width/2., -(CBLatWall_zdim-CBExtra_zdim+Acrylic_width)/2.+CBTiny_zdim+SlopedWall_zproj/2.);
	Roof4_apos->RegisterYourself();


	TGeoCompositeShape *CBRoof_a = new TGeoCompositeShape("CBRoof_a", "CBRoof2_a+(CBRoof1_a:Roof1_apos)+(CBRoof3_a:Roof3_apos)+(CBRoof4_a:Roof4_apos)");
	TGeoVolume *volCBRoof_a = new TGeoVolume("volCBRoof_a", CBRoof_a, 0);
	volColdBox->AddNode(volCBRoof_a, 0, new TGeoTranslation(Acrylic_width/2., CBFrontWall_ydim/2.+Acrylic_width/2., -(CBLatWall_zdim-CBExtra_zdim+Acrylic_width)/2.+Acrylic_width/2.));
	
	// Borated Polythylene Roof shape definition
	Double_t Roof4_bverts [8][2];
	Roof4_bverts[0][0] = 0.; Roof4_bverts[0][1] = 0.;
	Roof4_bverts[1][0] = 0.; Roof4_bverts[1][1] = BPoly_width;
	Roof4_bverts[2][0] = SlopedWall_zproj*(TMath::Tan(TMath::DegToRad()*15.)); Roof4_bverts[2][1] = BPoly_width;
	Roof4_bverts[3][0] = SlopedWall_zproj*(TMath::Tan(TMath::DegToRad()*15.)); Roof4_bverts[3][1] = 0;
	Roof4_bverts[4][0] = 0; Roof4_bverts[4][1] = 0;
	Roof4_bverts[5][0] = 0; Roof4_bverts[5][1] = BPoly_width;
	Roof4_bverts[6][0] = 0; Roof4_bverts[6][1] = BPoly_width;
	Roof4_bverts[7][0] = 0; Roof4_bverts[7][1] = 0;

	TGeoBBox *CBRoof1_b 	= new TGeoBBox("CBRoof1_b", CBExtra_xdim_b/2., BPoly_width/2., CBLatWall_zdim_b/2.);
	TGeoBBox *CBRoof2_b		= new TGeoBBox("CBRoof2_b", (CBRearWall_xdim_b-BPoly_width)/2.+BPoly_width/2., BPoly_width/2., (CBLatWall_zdim_b-CBExtra_zdim+Acrylic_width)/2.);
	TGeoBBox *CBRoof3_b		= new TGeoBBox("CBRoof3_b", (SlopedWall_zproj*(TMath::Tan(TMath::DegToRad()*15.)))/2., BPoly_width/2., (CBTiny_zdim-Acrylic_width)/2.);
	TGeoArb8 *CBRoof4_b		= new TGeoArb8("CBRoof4_b", SlopedWall_zproj/2., (Double_t*) Roof4_bverts);

	TGeoTranslation *Roof1_bpos = new TGeoTranslation("Roof1_bpos", -(CBRearWall_xdim-Acrylic_width)/2.-CBExtra_xdim_b/2., 0, CBExtra_zdim/2.-Acrylic_width/2.);
	Roof1_bpos->RegisterYourself();
	TGeoTranslation *Roof3_bpos = new TGeoTranslation("Roof3_bpos", (CBRearWall_xdim-Acrylic_width)/2.+(SlopedWall_zproj*(TMath::Tan(TMath::DegToRad()*15.)))/2., 0, -(CBLatWall_zdim_b-CBExtra_zdim+Acrylic_width)/2.+(CBTiny_zdim-Acrylic_width)/2.);
	Roof3_bpos->RegisterYourself();
	TGeoTranslation *Roof4_bpos = new TGeoTranslation("Roof4_bpos", (CBRearWall_xdim-Acrylic_width)/2., -BPoly_width/2., -(CBLatWall_zdim_b-CBExtra_zdim+Acrylic_width)/2.+CBTiny_zdim-Acrylic_width+SlopedWall_zproj/2.);
	Roof4_bpos->RegisterYourself();

	TGeoCompositeShape *CBRoof_b = new TGeoCompositeShape("CBRoof_b", "CBRoof2_b+(CBRoof1_b:Roof1_bpos)+(CBRoof3_b:Roof3_bpos)+(CBRoof4_b:Roof4_bpos)");
	TGeoVolume *volCBRoof_b = new TGeoVolume("volCBRoof_b", CBRoof_b, 0);
	
	volCBRoof_b->SetLineColor(kBlue);
	volColdBox->AddNode(volCBRoof_b, 0, new TGeoTranslation(-Acrylic_width/2., CBFrontWall_ydim/2.-BPoly_width/2., -(CBLatWall_zdim-CBExtra_zdim+Acrylic_width)/2.+Acrylic_width/2.));
	
	volMother->AddNode(volColdBox, 0, 0);
    volMother->Draw("ogl");
}


void oldgeometry(){
/******** OLD GEOMETRY **********/
//Cold Box	
/*
	InitMedium("Borated30polyethylene");
	TGeoMedium *Bor30Poly =gGeoManager->GetMedium("Borated30polyethylene");
	InitMedium("Epoxy");
	TGeoMedium *Acrylic =gGeoManager->GetMedium("Epoxy");


	Float_t CBWallWidth_a		= 5; // cm
	Float_t CBWallHeight		= 175; // cm
	Float_t CBWallLength		= 200; // cm
	Float_t CBWallWidth_b		= 4; // cm
	Float_t CBWallHeight_b		= CBWallHeight - CBWallWidth_a; // cm
	Float_t CBWallLength_b		= CBWallLength - 2*CBWallWidth_a; // cm 
	Float_t CBZOffset		= TTrackerZ+CBWallWidth_a/2.+0.34431500;

	TGeoBBox *CBWallUpstream_a = new TGeoBBox("CBWallUpstream_a", CBWallLength/2., CBWallHeight/2., CBWallWidth_a/2.);
	TGeoBBox *CBLateral_a = new TGeoBBox("CBLateral_a", CBWallWidth_a/2, CBWallHeight/2., (CBWallLength-2*CBWallWidth_a)/2.);
	TGeoBBox *CBTop_a = new TGeoBBox("CBTop_a", (CBWallLength-2*CBWallWidth_a)/2., CBWallWidth_a/2., (CBWallLength-2*CBWallWidth_a)/2.);

	TGeoBBox *CBWallUpstream_b = new TGeoBBox("CBWallUpstream_b", CBWallLength_b/2., CBWallHeight_b/2., CBWallWidth_b/2.);
	TGeoBBox *CBLateral_b = new TGeoBBox("CBLateral_b", CBWallWidth_b/2, CBWallHeight_b/2., (CBWallLength_b-2*CBWallWidth_b)/2.);
	
	TGeoTranslation *CBWallpos = new TGeoTranslation("CBWallpos", -dx_survey[4]+dx_survey[0]+XDimension/2., (YDimension-CBWallHeight_b)/2., 0);
	CBWallpos->RegisterYourself();
    	TGeoCompositeShape *CBWallDownstream_b = new TGeoCompositeShape("CBWallDownstream_b", "CBWallUpstream_b-(walltot:CBWallpos)");

	TGeoBBox *CBTop_b = new TGeoBBox("CBTop_b", (CBWallLength_b-2*CBWallWidth_b)/2., CBWallWidth_b/2., (CBWallLength_b-2*CBWallWidth_b)/2.);
    	
	
	TGeoVolume *volCBWallUp_a = new TGeoVolume("volCBWallUp_a", CBWallUpstream_a, Acrylic);
	TGeoVolume *volCBLateral_a = new TGeoVolume("volCBLateral_a", CBLateral_a, Acrylic);
    	TGeoVolume *volCBWallDown_a = new TGeoVolume("volCBWallDown_a", CBWallUpstream_a, Acrylic);
	TGeoVolume *volTop_a = new TGeoVolume("volTop_a", CBTop_a, Acrylic);

	TGeoVolume *volCBWallUp_b = new TGeoVolume("volCBWallUp_b", CBWallUpstream_b, Bor30Poly);
	TGeoVolume *volCBLateral_b = new TGeoVolume("volCBLateral_b", CBLateral_b, Bor30Poly);
    	TGeoVolume *volCBWallDown_b = new TGeoVolume("volCBWallDown_b", CBWallDownstream_b, Bor30Poly);
	TGeoVolume *volTop_b = new TGeoVolume("volTop_b", CBTop_b, Bor30Poly);

	//Painting
	volCBWallUp_a->SetLineColor(kGray-1);
	volCBWallUp_a->SetTransparency(50);
	volCBLateral_a->SetLineColor(kGray-1);
	volCBLateral_a->SetTransparency(50);
	volCBWallDown_a->SetLineColor(kGray-1);
	volCBWallDown_a->SetTransparency(50);
	volTop_a->SetLineColor(kGray-1);
	volTop_a->SetTransparency(50);

	volCBWallUp_b->SetLineColor(kGray+2);
	volCBLateral_b->SetLineColor(kGray+2);
	volCBWallDown_b->SetLineColor(kGray+2);
	volTop_b->SetLineColor(kGray+2);
	
	// Acrylic
	volTarget->AddNode(volCBWallDown_a, 0, new TGeoTranslation(-XDimension/2.-dx_survey[0]-XDimension/2., dz_survey[0]+CBWallHeight/2., dy_survey[4]+TotalWallZDim/2.+WallZBorder_offset+CBWallWidth_a/2.+CBZOffset));

	LOG(INFO) << "++++CBWallDown_a z-position: " << dy_survey[4]+TotalWallZDim/2.+WallZBorder_offset+CBWallWidth_a/2.+CBZOffset;

	volTarget->AddNode(volCBLateral_a, 0, new TGeoTranslation(-XDimension/2.-dx_survey[0]-XDimension/2.-CBWallLength/2.+CBWallWidth_a/2., dz_survey[0]+CBWallHeight/2., dy_survey[4]+TotalWallZDim/2.+WallZBorder_offset-(CBWallLength-2*CBWallWidth_a)/2.+CBZOffset));

	volTarget->AddNode(volCBLateral_a, 1, new TGeoTranslation(-XDimension/2.-dx_survey[0]-XDimension/2.+CBWallLength/2.-CBWallWidth_a/2., dz_survey[0]+CBWallHeight/2., dy_survey[4]+TotalWallZDim/2.+WallZBorder_offset-(CBWallLength-2*CBWallWidth_a)/2.+CBZOffset));

	volTarget->AddNode(volCBWallUp_a, 0, new TGeoTranslation(-XDimension/2.-dx_survey[0]-XDimension/2., dz_survey[0]+CBWallHeight/2., dy_survey[4]+TotalWallZDim/2.+WallZBorder_offset-(CBWallLength-2*CBWallWidth_a)-CBWallWidth_a/2.+CBZOffset));
	
	volTarget->AddNode(volTop_a, 0, new TGeoTranslation(-XDimension/2.-dx_survey[0]-XDimension/2., dz_survey[0]+CBWallHeight-CBWallWidth_a/2., dy_survey[4]+TotalWallZDim/2.+WallZBorder_offset-(CBWallLength-2*CBWallWidth_a)/2.+CBZOffset));
	
	// Borated polyethylene
	volTarget->AddNode(volCBWallDown_b, 0, new TGeoTranslation(-XDimension/2.-dx_survey[0]-XDimension/2., dz_survey[0]+CBWallHeight_b/2., dy_survey[4]+TotalWallZDim/2.+WallZBorder_offset-CBWallWidth_b/2.+CBZOffset));
	
	volTarget->AddNode(volCBLateral_b, 0, new TGeoTranslation(-XDimension/2.-dx_survey[0]-XDimension/2.-CBWallLength_b/2.+CBWallWidth_b/2., dz_survey[0]+CBWallHeight_b/2., dy_survey[4]+TotalWallZDim/2.+WallZBorder_offset-(CBWallLength-2*CBWallWidth_a)/2.+CBZOffset));
	
	volTarget->AddNode(volCBLateral_b, 1, new TGeoTranslation(-XDimension/2.-dx_survey[0]-XDimension/2.+CBWallLength_b/2.-CBWallWidth_b/2., dz_survey[0]+CBWallHeight_b/2., dy_survey[4]+TotalWallZDim/2.+WallZBorder_offset-(CBWallLength-2*CBWallWidth_a)/2.+CBZOffset));

	volTarget->AddNode(volCBWallUp_b, 0, new TGeoTranslation(-XDimension/2.-dx_survey[0]-XDimension/2., dz_survey[0]+CBWallHeight_b/2., dy_survey[4]+TotalWallZDim/2.+WallZBorder_offset-(CBWallLength-2*CBWallWidth_a)/2.-(CBWallLength_b-2*CBWallWidth_b)/2.-CBWallWidth_b/2.+CBZOffset));

	volTarget->AddNode(volTop_b, 0, new TGeoTranslation(-XDimension/2.-dx_survey[0]-XDimension/2., dz_survey[0]+CBWallHeight_b-CBWallWidth_b/2., dy_survey[4]+TotalWallZDim/2.+WallZBorder_offset-(CBWallLength-2*CBWallWidth_a)/2.+CBZOffset));
	
/********************************************
*/
}
