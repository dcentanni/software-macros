#include "histocanvas.h"
#include "TInterpreter.h"
#include "TTreeReader.h"
#include "TH1.h"
#include "TH2.h"
using namespace ROOT;

/**************************
    EXPERIMENT DIMENSIONS

        START       END
X       -82.800     -2.000
Y         5.750     69.600
Z       -33.475    217.095
***************************/
bool isVertical(int DetID){
  if  (floor(DetID/10000)==3&&DetID%1000>59) {return kTRUE;}
  else{return kFALSE;}
}
float GetP_det(Double32_t Px, Double32_t Py, Double32_t Pz){
	float p = TMath::Sqrt(Px*Px+Py*Py+Pz*Pz);
	return p;
}


void muon_background(TString inputfile, TString savepath, TString filename, TString geofile, int evstart, int evend, bool muplus = false){

    TFile *file = new TFile(inputfile);
    gGeoManager->Import(geofile);
    if(!file) return;
    cout << "- Reading file : " << inputfile << endl;
    cout << "- Reading geofile : " << geofile << endl;

    TTreeReader reader("cbmsim", file);
    TTreeReaderArray <ShipMCTrack>  tracks(reader, "MCTrack");
    TTreeReaderArray <ScifiPoint>   scifipoints(reader, "ScifiPoint");
    TTreeReaderArray <MuFilterPoint>   mufilterpoints(reader, "MuFilterPoint");

    gStyle->SetCanvasDefH(757);
    gStyle->SetCanvasDefW(1190);
    gStyle->SetOptStat("emr");
    TDatabasePDG *b=TDatabasePDG::Instance();
    /******* HISTOS *****************/
    TH1F *muon_p = new TH1F("muon_p", "Momentum of primary background muons", 250, 0, 3500);
    TH1F *scifi_p = new TH1F("scifi_p", "Momentum of primary background muons hitting scifi", 250, 0, 3500);
    TH1F *mufilter_p = new TH1F("mufilter_p", "Momentum of primary background muons hitting mufilter", 250, 0, 3500);
    TH1F *mu_mufilter = new TH1F("mu_mufilter", "N. of muon hits per n. MuFilter station", 10, -0.5, 9.5);
    TH1F *mu_scifi = new TH1F("mu_scifi", "N. of muon hits per n. Scifi station", 7, -0.5, 6.5);
    TH1F *nmufilt_hits = new TH1F("nmufilt_hits", "N. of muon hits in MuFilter", 10, -0.5, 9.5);
    TH1F *nscifi_hits = new TH1F("nscifi_hits", "N. of muon hits in Scifi station", 7, -0.5, 6.5);
    TH2F *mxy_scifi = new TH2F("mxy_scifi", "XY Distribution of first muon hits in Scifi", 200, -140, 60, 200, -60, 140);
    TH2F *mxy_mufilter = new TH2F("mxy_mufilter", "XY Distribution of first muon hits in MuFilter", 200, -140, 60, 200, -60, 140);
    TH2F *mu_xy = new TH2F("mu_xy", "XY Distribution of incoming muons", 200, -100, 100, 200, -100, 100);
    TH2F *mu_xy_proj = new TH2F("mu_xy_proj", "XY Projections at SND", 200, -100, 100, 200, -100, 100);
    TH2F *mu_xy_snd = new TH2F("mu_xy_snd", "XY Distribution of incoming muons hitting SND Detectors", 200, -100, 100, 200, -100, 100);
    TH1F *nomu_neutron_p = new TH1F("nomu_neutron_p", "Momentum distribution of neutron interacting in SND without muon", 300, 0, 30);
    TH1F *nomu_neutron_p_in = new TH1F("nomu_neutron_p_in", "Momentum distribution of inner generated neutron interacting in SND without muon", 300, 0, 30);
    TH1F *hit1_mu_tx = new TH1F("hit1_mu_tx", "TX distribution for 1 hit muons in MuFilter", 400, -0.4, 0.4);
    TH1F *hit1_mu_ty = new TH1F("hit1_mu_ty", "TY distribution for 1 hit muons in MuFilter", 400, -0.4, 0.4);
    TH1F *hit7_mu_tx = new TH1F("hit7_mu_tx", "TX distribution for 7 hit muons in MuFilter", 400, -0.4, 0.4);
    TH1F *hit7_mu_ty = new TH1F("hit7_mu_ty", "TY distribution for 7 hit muons in MuFilter", 400, -0.4, 0.4);
    TH1F *npmufilt_hits100M = new TH1F("npmufilt_hits100M", "N. of particle hits in MuFilter with energy > 100 MeV", 152, -0.5, 151.5);
    TH1F *npmufilt_hits1G = new TH1F("npmufilt_hits1G", "N. of particle hits in MuFilter with energy > 1 GeV", 102, -0.5, 101.5);
    TH1F *npscifi_hits100M = new TH1F("npscifi_hits100M", "N. of particle hits in Scifi with energy > 100 MeV", 102, -0.5, 101.5);
    TH1F *npscifi_hits1G = new TH1F("npscifi_hits1G", "N. of particle hits in Scifi with energy > 1 GeV", 42, -0.5, 41.5);
    TH2F *xy_N_int = new TH2F("xy_N_int", "XY distribution of interaction points of neutrons", 200, -140, 60, 200, -60, 140);
    TH2F *yz_N_int = new TH2F("yz_N_int", "YZ distribution of interaction points of neutrons", 400, -100, 300, 400, -160, 240);
    TH1F *musnd_p = new TH1F("musnd_p", "Momentum of primary background muons prducing hits in SND@LHC", 250, 0, 3500);
    /******** VARIABLES *************/
    int ientry = 0;
    int pdgcode, charge;
    int itrack = 0;
    int iscifi = 0;
    int imufilter = 0;
    int nevents = reader.GetEntries(true);
    int scifiDetID;
    int scifiTrackID, mufiltTrackID;
    int mufiltstation;
    int mufilt_UpDown;
    cout << "- Number of events " << nevents << endl;
    cout.precision(10);
    const float crossect_fb = 8E+13;
    const float collision_rate = 8E+8;
    const float Luminosity = 25;
    const float collision_rate25fb = Luminosity*crossect_fb;  
    const float nppevent = 78E+6; // for fluka muons_up_V1
    const float normalization = collision_rate/nppevent;
    const float normalization2 = collision_rate25fb/nppevent;
    int scifi_detmem, scifi_trackmem;
    int mufilt_detmem, mufilt_trackmem;
    int mufilt_hit;
    int scifi_hit;
    int pmufilt_hit_100M;
    int pmufilt_hit_1G;
    int pscifi_hit_100M;
    int pscifi_hit_1G;
    bool mufilt_int;
    bool scifi_int;
    const char *volName;
    bool int_N;
    bool int_N_in;
    const float z_veto = -33.475;
    float mu_tx, mu_ty;
    float y_proj, x_proj;
    if(evend > nevents) evend = nevents;
    if(evstart > nevents) {cout << "Maximum n. of entries reached, quitting" << endl; return;}
    cout << "- Executing script from ev no. " << evstart << " to ev no. " << evend << endl;
    /************* LOOP *****************/
    while (reader.Next())
    {
        ientry = reader.GetCurrentEntry();
        itrack = 0;
        iscifi = 0;
        imufilter = 0;
        mufilt_hit = 0;
        scifi_hit = 0;
        scifi_int = false;
        mufilt_int = false;
        pmufilt_hit_100M = 0;
        pmufilt_hit_1G = 0;
        pscifi_hit_1G = 0;
        pscifi_hit_100M = 0;
    if(ientry >= evstart && ientry < evend){
        ShipMCTrack muontrack = tracks[0]; //muons
        float W = normalization*muontrack.GetWeight();
        float W2 = normalization2*muontrack.GetWeight();
        muon_p->Fill(muontrack.GetP(), W2);
        mu_xy->Fill(muontrack.GetStartX(), muontrack.GetStartY(), W2);
        if(muontrack.GetPz() !=0) {
            mu_tx = muontrack.GetPx()/muontrack.GetPz();
            mu_ty = muontrack.GetPy()/muontrack.GetPz();
            y_proj = mu_ty*(z_veto-muontrack.GetStartZ())+muontrack.GetStartY();
            x_proj = mu_tx*(z_veto-muontrack.GetStartZ())+muontrack.GetStartX();
            mu_xy_proj->Fill(x_proj, y_proj, W2);
        }
        
        for(ScifiPoint& scifipoint: scifipoints){
            pdgcode = scifipoint.PdgCode();
            if(scifipoint.PdgCode()==13 && muplus == false){
                scifi_int = true;
                scifi_p->Fill(muontrack.GetP(), W2);
                mxy_scifi->Fill(scifipoint.GetX(), scifipoint.GetY(), W2);
                break;}
            if(scifipoint.PdgCode()==-13 && muplus == true){
                scifi_int = true;
                scifi_p->Fill(muontrack.GetP(), W2);
                mxy_scifi->Fill(scifipoint.GetX(), scifipoint.GetY(), W2);
                break;}
        }// scifi point
        for(MuFilterPoint& mufilterpoint: mufilterpoints){
            if(mufilterpoint.PdgCode()==13 && muplus == false){
                mufilt_int = true;
                mufilter_p->Fill(muontrack.GetP(), W2);
                mxy_mufilter->Fill(mufilterpoint.GetX(), mufilterpoint.GetY(), W2);
                break;}
            if(mufilterpoint.PdgCode()==-13 && muplus == true){
                mufilt_int = true;
                mufilter_p->Fill(muontrack.GetP(), W2);
                mxy_mufilter->Fill(mufilterpoint.GetX(), mufilterpoint.GetY(), W2);
                break;}
        }// mufilter point
        scifi_detmem = -1000;
        scifi_trackmem = -2000;
        for(ScifiPoint& scifipoint: scifipoints){
            scifiTrackID = scifipoint.GetTrackID();
            scifiDetID = scifipoint.station();
            if(scifi_trackmem == scifiTrackID && scifi_detmem == scifiDetID) continue; //avoiding repetition for same scifi
            if(scifipoint.PdgCode()==13 && muplus == false) {mu_scifi->Fill(scifiDetID, W2); scifi_hit++;}
            if(scifipoint.PdgCode()==-13 && muplus == true) {mu_scifi->Fill(scifiDetID, W2); scifi_hit++;}
            if(scifiTrackID > -1) pscifi_hit_100M++;
            if(scifiTrackID > -1 && GetP_det(scifipoint.GetPx(), scifipoint.GetPy(), scifipoint.GetPz())>=1.) pscifi_hit_1G++;
            scifi_trackmem = scifiTrackID;
            scifi_detmem = scifiDetID;
        } // scifipoint

        mufilt_detmem = -1000;
        mufilt_trackmem = -2000;
        for(MuFilterPoint& mufilterpoint: mufilterpoints){
            mufiltTrackID = mufilterpoint.GetTrackID();
            if(mufilterpoint.GetDetectorID()/10000 == 1) continue; //excludes VetoPlane
            mufilt_UpDown = mufilterpoint.GetDetectorID()/10000;
            mufiltstation = mufilterpoint.GetDetectorID()/1000%10;
            if(mufilt_UpDown == 3 && mufiltstation == 3) continue; // excludes last vertical plane
            if(isVertical(mufilterpoint.GetDetectorID())== kTRUE) continue; // excludes vertical bars on Downstream
            if(mufilt_trackmem == mufiltTrackID && mufilt_detmem == mufiltstation) continue; //avoiding repetition for same mufilter
            if(mufilterpoint.PdgCode()==13 && mufiltTrackID==0 && muplus == false){
                if(mufilt_UpDown == 3) mu_mufilter->Fill(mufiltstation+6, W2); //Downstream
                if(mufilt_UpDown == 2) mu_mufilter->Fill(mufiltstation+1, W2); // Upstream
                mufilt_hit++;
            }
            if(mufilterpoint.PdgCode()==-13 && mufiltTrackID==0 && muplus == true){
                if(mufilt_UpDown == 3) mu_mufilter->Fill(mufiltstation+6, W2); //Downstream
                if(mufilt_UpDown == 2) mu_mufilter->Fill(mufiltstation+1, W2); // Upstream
                mufilt_hit++;
            }
            if(mufiltTrackID > -1) pmufilt_hit_100M++;
            if(mufiltTrackID > -1 && GetP_det(mufilterpoint.GetPx(), mufilterpoint.GetPy(), mufilterpoint.GetPz())>=1.) pmufilt_hit_1G++;
            mufilt_trackmem = mufiltTrackID;
            mufilt_detmem = mufiltstation;
        } // mufilter point
        if(pscifi_hit_100M > 80) cout << "ientry " << ientry << " scifi hit100M > 80" << endl;
        if(pmufilt_hit_100M > 140) cout << "ientry " << ientry << " mufilt hit100M > 140" << endl;
        if(pmufilt_hit_100M !=0) npmufilt_hits100M->Fill(pmufilt_hit_100M, W2);
        if(pmufilt_hit_1G !=0) npmufilt_hits1G->Fill(pmufilt_hit_1G, W2);
        if(pscifi_hit_100M !=0) npscifi_hits100M->Fill(pscifi_hit_100M, W2);
        if(pscifi_hit_1G !=0) npscifi_hits1G->Fill(pscifi_hit_1G, W2);
        if(mufilt_hit == 1) {hit1_mu_tx->Fill(mu_tx, W2); hit1_mu_ty->Fill(mu_ty, W2);}
        if(mufilt_hit == 7) {hit7_mu_tx->Fill(mu_tx, W2); hit7_mu_ty->Fill(mu_ty, W2);}
        if(mufilt_hit !=0) nmufilt_hits->Fill(mufilt_hit, W2);
        if(scifi_hit !=0) nscifi_hits->Fill(scifi_hit, W2);
        if(mufilt_int == true || scifi_int == true){
            mu_xy_snd->Fill(muontrack.GetStartX(), muontrack.GetStartY(), W2);
        }
        if(mufilt_int == false && scifi_int == false){ //NO MUONS IN SND
            for(ShipMCTrack& track: tracks){
                itrack++;
                int_N = false;
                int_N_in = false;
                if(gGeoManager->FindNode(track.GetStartX(), track.GetStartY(), track.GetStartZ())->GetMotherVolume() != NULL) volName = gGeoManager->FindNode(track.GetStartX(), track.GetStartY(), track.GetStartZ())->GetMotherVolume()->GetName();
                if(track.GetPdgCode()==2112){
                    for(ShipMCTrack& track2: tracks){
                        if(gGeoManager->FindNode(track2.GetStartX(), track2.GetStartY(), track2.GetStartZ())->GetMotherVolume() != NULL){
                            if(track2.GetMotherId()==itrack){
                                if(strncmp(gGeoManager->FindNode(track2.GetStartX(), track2.GetStartY(), track2.GetStartZ())->GetMotherVolume()->GetName(), "Tunnel", 6)!=0){
                                    int_N = true;
                                    //cout << "ev no. " << ientry << " process " << track.GetProcName() << endl;
                                    //cout << "       produced " << track2.GetPdgCode() << " in " <<  gGeoManager->FindNode(track2.GetStartX(), track2.GetStartY(), track2.GetStartZ())->GetName() << endl;
                                    xy_N_int->Fill(track2.GetStartX(), track2.GetStartY(), W2);
                                    yz_N_int->Fill(track2.GetStartZ(), track2.GetStartY(), W2);
                                }
                            }
                        } 
                    }
                    if(strncmp(volName, "Tunnel", 6)!=0){ 
                        for(ShipMCTrack& track2: tracks){
                            if(gGeoManager->FindNode(track2.GetStartX(), track2.GetStartY(), track2.GetStartZ())->GetMotherVolume() != NULL){
                                if(track2.GetMotherId()==itrack){
                                    if(strncmp(gGeoManager->FindNode(track2.GetStartX(), track2.GetStartY(), track2.GetStartZ())->GetMotherVolume()->GetName(), "Tunnel", 6)!=0){
                                        int_N_in = true;
                                        //cout << "ev no. " << ientry << " process " << track.GetProcName() << " intN_in TRUE" << endl;
                                        //cout << "       produced " << track2.GetPdgCode() << " in " <<  gGeoManager->FindNode(track2.GetStartX(), track2.GetStartY(), track2.GetStartZ())->GetName() << endl;
                                        //xy_N_int_in->Fill(track2.GetStartX(), track2.GetStartY(), W2);
                                        //yz_N_int_in->Fill(track2.GetStartZ(), track2.GetStartY(), W2);
                                    }
                                }
                            } 
                        }
                    }
                    if(int_N == true) {nomu_neutron_p->Fill(track.GetP(), W2);}
                    if(int_N_in == true) nomu_neutron_p_in->Fill(track.GetP(), W2);
                }
            } // MCTracks
        }// No muons in SND
        if(mufilt_int == true || scifi_int == true) musnd_p->Fill(muontrack.GetP(), W2);
    }//event if
    } // while

/********* WRITING TO FILE **********/
TFile *f1=new TFile(savepath+filename, "RECREATE");
muon_p->Write();
mufilter_p->Write();
scifi_p->Write();
mu_mufilter->Write();
mu_scifi->Write();
nmufilt_hits->Write();
nscifi_hits->Write();
mxy_mufilter->Write();
mxy_scifi->Write();
mu_xy_snd->Write();
mu_xy->Write();
nomu_neutron_p->Write();
nomu_neutron_p_in->Write();
mu_xy_proj->Write();
hit1_mu_tx->Write();
hit1_mu_ty->Write();
hit7_mu_tx->Write();
hit7_mu_ty->Write();
npscifi_hits100M->Write();
npmufilt_hits100M->Write();
npscifi_hits1G->Write();
npmufilt_hits1G->Write();
xy_N_int->Write();
yz_N_int->Write();
musnd_p->Write();
f1->Close();
}


void Loop(TString inputfile, TString savepath, TString filename, TString geofile, int evstart, int evend){

    TFile *file = new TFile(inputfile);
    gGeoManager->Import(geofile);
    if(!file) return;
    cout << "- Reading file : " << inputfile << endl;
    cout << "- Reading geofile : " << geofile << endl;

    TTreeReader reader("cbmsim", file);
    TTreeReaderArray <ShipMCTrack> tracks(reader, "MCTrack");

    gStyle->SetCanvasDefH(757);
    gStyle->SetCanvasDefW(1190);
    gStyle->SetOptStat("emr");
    TDatabasePDG *b=TDatabasePDG::Instance();
    /******* HISTOS *****************/
    TH1F *muon_p = new TH1F("muon_p", "Momentum of primary background muons", 250, 0, 3500);
    TH2F *muonint_distyz_in = new TH2F("muonint_distyz_in", "YZ Distribution of inner interacting points of background muons", 400, -100, 300, 400, -160, 240);
    TH2F *muonint_distxy_in = new TH2F("muonint_distxy_in", "XY Distribution of inner interacting points of background muons", 230, -200, 30, 150, -50, 100);
    TH2F *muonint_distyz = new TH2F("muonint_distyz", "YZ Distribution of interacting points of background muons", 400, -100, 300, 400, -160, 240);
    TH2F *muonint_distxy = new TH2F("muonint_distxy", "XY Distribution of interacting points of background muons", 230, -200, 30, 150, -50, 100);

    TH1F *muon_p_in = new TH1F("muon_p_in", "Momentum of primary background muons interacting in SND@LHC", 250, 0, 3500);
    TH1F *muonBrickp = new TH1F("muonBrickp", "Momentum of primary background muons interacting in SND@LHC Bricks", 250, 0, 3500);
    TH1F *muonMuFilterp = new TH1F("muonMuFilterp", "Momentum of primary background muons interacting in SND@LHC MuFilter", 250, 0, 3500);
    TH1F *muonUpStreamp = new TH1F("muonUpStreamp", "Momentum of primary background muons interacting in SND@LHC Upstream", 250, 0, 3500);
    TH1F *muonDownStreamp = new TH1F("muonDownStreamp", "Momentum of primary background muons interacting in SND@LHC Downstream", 250, 0, 3500);
    TH1F *mupassing_p = new TH1F("mupassing_p", "Momentum of non interacting primary background muons", 100, 0, 100);
    TH1F *muTunnelp = new TH1F("muTunnelp", "Momentum of primary background muons interacting in Tunnel", 250, 0, 3500);

    TH1D *molt_mu_ch = new TH1D("molt_mu_ch", "Multiplicity of charged daughters from background muons", 101, -0.5, 100.5);
    TH1D *molt_mu_n = new TH1D("molt_mu_n", "Multiplicity of neutral daughters from background muons", 31, -0.5, 30.5);
    TH1D *molt_mu_ch_in = new TH1D("molt_mu_ch_in", "Multiplicity of inner charged daughters from background muons", 31, -0.5, 30.5);
    TH1D *molt_mu_n_in = new TH1D("molt_mu_n_in", "Multiplicity of inner neutral daughters from background muons", 31, -0.5, 30.5);

    TH1F *pgamma_p = new TH1F("pgamma_p", "Momentum of muon produced gamma", 200, 0, 2000);
    TH1F *pneutron_p = new TH1F("pneutron_p", "Momentum of muon produced neutron", 300, 0, 300);
    TH2F *pgamma_yz = new TH2F("pgamma_yz", "YZ Distribution of interacting points of muon produced gamma", 400, -100, 300, 400, -160, 240);
    TH2F *pneutron_yz = new TH2F("pneutron_yz", "YZ Distribution of interacting points of muon produced neutron", 400, -100, 300, 400, -160, 240);
    TH1F *pgamma_p_in = new TH1F("pgamma_p_in", "Momentum of inner muon produced gamma", 200, 0, 2000);
    TH1F *pneutron_p_in = new TH1F("pneutron_p_in", "Momentum of inner muon produced neutron", 300, 0, 300);
    TH2F *pgamma_yz_in = new TH2F("pgamma_yz_in", "YZ Distribution of inner interacting points of muon produced gamma", 400, -100, 300, 400, -160, 240);
    TH2F *pneutron_yz_in = new TH2F("pneutron_yz_in", "YZ Distribution of inner interacting points of muon produced neutron", 400, -100, 300, 400, -160, 240);

    TH1F *pintgamma_p = new TH1F("pintgamma_p", "Momentum of muon produced and interacting gamma", 200, 0, 2000);
    TH1F *pintneutron_p = new TH1F("pintneutron_p", "Momentum of muon produced and interacting neutron", 300, 0, 300);
    TH1F *pintgamma_p_in = new TH1F("pintgamma_p_in", "Momentum of inner muon produced and interacting gamma", 200, 0, 2000);
    TH1F *pintneutron_p_in = new TH1F("pintneutron_p_in", "Momentum of inner muon produced and interacting neutron", 300, 0, 300);
    
    TH1F *pint_ingamma_p = new TH1F("pint_ingamma_p", "Momentum of muon produced and interacting in SND@LHC gamma", 200, 0, 2000);
    TH1F *pint_inneutron_p = new TH1F("pint_inneutron_p", "Momentum of muon produced and interacting in SND@LHC neutron", 20, 0, 20);
    TH1F *pint_ingamma_p_in = new TH1F("pint_ingamma_p_in", "Momentum of inner muon produced and interacting in SND@LHC gamma", 200, 0, 2000);
    TH1F *pint_inneutron_p_in = new TH1F("pint_inneutron_p_in", "Momentum of inner muon produced and interacting in SND@LHC neutron", 20, 0, 20);

    TH1F *neutral_p = new TH1F("neutral_p", "Momentum neutral particles", 1000, 0, 1000);
    TH2F *neutr_distxy = new TH2F("neutr_distxy", "XY Distribution of starting pos of neutral particles", 230, -200, 30, 150, -50, 100);
    TH2F *neutr_distyz = new TH2F("neutr_distyz", "YZ Distribution of starting pos of neutral particles", 400, -100, 300, 400, -160, 240);
    
    TH1F *neutral_p_out = new TH1F("neutral_p_out", "Outer neutral particles momentum", 1000, 0, 1000);
    TH2F *neutr_distxy_out = new TH2F("neutr_distxy_out", "XY Distribution of starting pos of outer neutral particles", 230, -200, 30, 150, -50, 100);
    TH2F *neutr_distyz_out = new TH2F("neutr_distyz_out", "YZ Distribution of starting pos of outer neutral particles", 400, -100, 300, 400, -160, 240);
   
    TH1F *neutral_p_in = new TH1F("neutral_p_in", "Inner neutral particles momentum", 1000, 0, 1000);
    TH2F *neutr_distxy_in = new TH2F("neutr_distxy_in", "XY Distribution of starting pos of inner neutral particles", 230, -200, 30, 150, -50, 100);
    TH2F *neutr_distyz_in = new TH2F("neutr_distyz_in", "YZ Distribution of starting pos of inner neutral particles", 400, -100, 300, 400, -160, 240);
    
    TH1D *daughts_c = new TH1D("daughts_c", "Multiplicity of charged daughters from neutral particles", 11, -0.5, 10.5);
    TH1D *daughts_n = new TH1D("daughts_n", "Multiplicity of neutral daughters from neutral particles", 61, -0.5, 60.5);
    /******** VARIABLES *************/
    int ientry = 0;
    int pdgcode, charge;
    int itrack = 0;
    int nevents = reader.GetEntries(true);
    int nnparts =0;
    int nnparts_out = 0;
    int daug_c = 0; int daug_n = 0;
    int mu_ch = 0; int mu_n = 0;
    int mu_ch_in = 0; int mu_n_in = 0;
    bool intBrick, intMuFilter, intMuUpstream, intMuDownstream;
    bool intMu;
    bool intN, intGamma, intN_in, intGamma_in;
    bool int_inN_in, int_inN, int_inGamma_in, int_inGamma;  
    bool muTunnel;
    int muBrick = 0; int muMuFilter = 0; int muMuUpstream = 0; int muMuDownstream = 0;
    int multiple_int = 0;
    int inMu = 0;
    bool has_daugh;
    bool has_ch, has_n, has_ch_in, has_n_in;
    cout << "- Number of events " << nevents << endl;
    cout.precision(10);
    const char *volName;
    const float crossect_fb = 8E+13;
    const float collision_rate = 8E+8;
    const float Luminosity = 25;
    const float collision_rate25fb = Luminosity*crossect_fb;  
    const float nppevent = 78E+6; // for fluka muons_up_V1
    const float normalization = collision_rate/nppevent;
    const float normalization2 = collision_rate25fb/nppevent;
    if(evend > nevents) evend = nevents;
    if(evstart > nevents) {cout << "Maximum n. of entries reached, quitting" << endl; return;}
    cout << "- Executing script from ev no. " << evstart << " to ev no. " << evend << endl;
    /*********** MAIN LOOP **********/

    while (reader.Next())
    {
        ientry = reader.GetCurrentEntry();
        itrack = 0;
    if(ientry >= evstart && ientry < evend){
        ShipMCTrack muontrack = tracks[0]; //muons
        float W = normalization*muontrack.GetWeight();
        float W2 = normalization2*muontrack.GetWeight();
        muon_p->Fill(muontrack.GetP(), W2);
        intBrick = false; intMuFilter = false; intMuUpstream = false; intMuDownstream = false; intMu = false; muTunnel = false;
        has_daugh = false;
        has_ch = false; has_n = false; has_ch_in = false; has_n_in = false;
        mu_ch_in = 0; mu_ch = 0;
        mu_n_in = 0;  mu_n = 0;
        
        for(ShipMCTrack& track: tracks){ // track loop
            itrack++;
            pdgcode = track.GetPdgCode();
            charge=0;
            intN_in = false;        intN = false;
            intGamma_in = false;    intGamma = false;
            int_inN_in = false;     int_inN = false;   
            int_inGamma_in = false; int_inGamma = false; 


            if(b->GetParticle(pdgcode) != NULL) charge = b->GetParticle(pdgcode)->Charge();
            if(gGeoManager->FindNode(track.GetStartX(), track.GetStartY(), track.GetStartZ())->GetMotherVolume() != NULL) volName = gGeoManager->FindNode(track.GetStartX(), track.GetStartY(), track.GetStartZ())->GetMotherVolume()->GetName();
            
            if(track.GetMotherId()==0){
                    has_daugh = true;
                    muonint_distyz->Fill(track.GetStartZ(), track.GetStartY(), W2);
                    muonint_distxy->Fill(track.GetStartX(), track.GetStartY(), W2);
                    //if(pdgcode != 13 && pdgcode != 22 && pdgcode != 11 && pdgcode != -11 && pdgcode != 2112) cout << "ev no. " << ientry << " itrack " << itrack << " pdgcode " << pdgcode << endl;
                    if(charge != 0){ has_ch = true; mu_ch++;}
                    if(charge == 0){ has_n = true; mu_n++;

                        if(track.GetPdgCode()==22){ // gamma
                            pgamma_p->Fill(track.GetP(), W2);
                            for(ShipMCTrack& track3: tracks){
                                if(track3.GetMotherId()== itrack) { 
                                    intGamma = true; 
                                    pgamma_yz->Fill(track3.GetStartZ(), track3.GetStartY(), W2);
                                    if(gGeoManager->FindNode(track3.GetStartX(), track3.GetStartY(), track3.GetStartZ())->GetMotherVolume() != NULL){
                                       if(strncmp(gGeoManager->FindNode(track3.GetStartX(), track3.GetStartY(), track3.GetStartZ())->GetMotherVolume()->GetName(), "Tunnel", 6)!=0){
                                           int_inGamma = true;
                                       } 
                                    }
                                }
                            }
                            if(intGamma == true) pintgamma_p->Fill(track.GetP(), W2);
                            if(intGamma == true && int_inGamma == true) pint_ingamma_p->Fill(track.GetP(), W2);
                        }//closes gamma

                        if(track.GetPdgCode()==2112){ // neutrons
                            pneutron_p->Fill(track.GetP(), W2);
                            for(ShipMCTrack& track4: tracks){
                                if(track4.GetMotherId()==itrack) {
                                    intN = true; 
                                    pneutron_yz->Fill(track4.GetStartZ(), track4.GetStartY(), W2);
                                    if(gGeoManager->FindNode(track4.GetStartX(), track4.GetStartY(), track4.GetStartZ())->GetMotherVolume() != NULL){
                                       if(strncmp(gGeoManager->FindNode(track4.GetStartX(), track4.GetStartY(), track4.GetStartZ())->GetMotherVolume()->GetName(), "Tunnel", 6)!=0){
                                           int_inN = true;
                                       } 
                                    }
                                }
                            }
                            if(intN == true) pintneutron_p->Fill(track.GetP(), W2);
                            if(intN == true && int_inN == true) pint_inneutron_p->Fill(track.GetP(), W2);
                        }//closes neutron

                    }//closes charge = 0
                if(strncmp(volName, "Tunnel", 6)!=0){ 
                    //if(pdgcode != 13 && pdgcode != 22 && pdgcode != 11 && pdgcode != -11 && pdgcode != 2112) cout << "INSIDE ev no. " << ientry << " itrack " << itrack << " pdgcode " << pdgcode << endl;
                    if(charge != 0 ) { has_ch_in = true; mu_ch_in++;}
                    if(charge == 0 ) { has_n_in = true; mu_n_in++;

                        if(track.GetPdgCode()==22){ // gamma
                            pgamma_p_in->Fill(track.GetP(), W2);
                            for(ShipMCTrack& track5: tracks){
                                if(track5.GetMotherId()== itrack) {
                                    intGamma_in = true; 
                                    pgamma_yz_in->Fill(track5.GetStartZ(), track5.GetStartY(), W2);
                                    if(gGeoManager->FindNode(track5.GetStartX(), track5.GetStartY(), track5.GetStartZ())->GetMotherVolume() != NULL){
                                       if(strncmp(gGeoManager->FindNode(track5.GetStartX(), track5.GetStartY(), track5.GetStartZ())->GetMotherVolume()->GetName(), "Tunnel", 6)!=0){
                                           int_inGamma_in = true;
                                       } 
                                    }
                                }
                            }
                            if(intGamma_in == true) pintgamma_p_in->Fill(track.GetP(), W2);
                            if(intGamma == true && int_inGamma_in == true) pint_ingamma_p_in->Fill(track.GetP(), W2);
                        } // closes gamma

                        if(track.GetPdgCode()==2112){ // neutron
                            pneutron_p_in->Fill(track.GetP(), W2);
                            for(ShipMCTrack& track6: tracks){
                                if(track6.GetMotherId()==itrack) {
                                    intN_in = true; 
                                    pneutron_yz_in->Fill(track6.GetStartZ(), track6.GetStartY(), W2);
                                    if(gGeoManager->FindNode(track6.GetStartX(), track6.GetStartY(), track6.GetStartZ())->GetMotherVolume() != NULL){
                                       if(strncmp(gGeoManager->FindNode(track6.GetStartX(), track6.GetStartY(), track6.GetStartZ())->GetMotherVolume()->GetName(), "Tunnel", 6)!=0){
                                           int_inN_in = true;
                                       } 
                                    }
                                }
                            }
                            if(intN_in == true) pintneutron_p_in->Fill(track.GetP(), W2);
                            if(intN == true && int_inN_in == true) pint_inneutron_p_in->Fill(track.GetP(), W2);
                        } // closes neutron

                    } // closes charge = 0

                    muonint_distyz_in->Fill(track.GetStartZ(), track.GetStartY(), W2);
                    muonint_distxy_in->Fill(track.GetStartX(), track.GetStartY(), W2);
                    //cout << "Ev no. " << ientry << " volName " << volName << endl;
                    intMu = true;
                    if(strncmp(volName, "Brick", 5)==0) intBrick = true;
                    if(strncmp(volName, "volMuFilter", 11)==0) intMuFilter = true;
                    if(strncmp(volName, "volMuUpstreamDet_", 16)==0) intMuUpstream = true;
                    if(strncmp(volName, "volMuDownstreamDet_", 18)==0) intMuDownstream = true;
                } // closes volName
                if(strncmp(volName, "Tunnel", 6)==0) muTunnel = true; 
            } // closes motherId = 0

        }// closes track
        if(has_daugh == true){
        if(has_ch == true) molt_mu_ch->Fill(mu_ch, W2);
        if(has_n == true) molt_mu_n->Fill(mu_n, W2);
        if(has_ch_in == true) molt_mu_ch_in->Fill(mu_ch_in, W2);
        if(has_n_in == true) molt_mu_n_in->Fill(mu_n_in, W2);
        }
        if(has_daugh == false) mupassing_p->Fill(muontrack.GetP(), W2);
        if(muTunnel == true) muTunnelp->Fill(muontrack.GetP(), W2);
        
        if(intMu == true) {inMu++; muon_p_in->Fill(muontrack.GetP(), W2);}
        if(intBrick == true) {muBrick++; muonBrickp->Fill(muontrack.GetP(), W2);}
        if(intMuFilter == true) {muMuFilter++; muonMuFilterp->Fill(muontrack.GetP(), W2);}
        if(intMuUpstream == true) {muMuUpstream++; muonUpStreamp->Fill(muontrack.GetP(), W2);}
        if(intMuDownstream == true) {muMuDownstream++; muonDownStreamp->Fill(muontrack.GetP(), W2);}
        if(intBrick == true && intMuFilter == true) multiple_int++;
    }//if ientry   
    }// main loop

/********* WRITING TO FILE **********/
TFile *f1=new TFile(savepath+filename, "RECREATE");
muon_p->Write();
muonint_distyz_in->Write();
muonint_distxy_in->Write();
muonint_distyz->Write();
muonint_distxy->Write();

muon_p_in->Write();
muonBrickp->Write();
muonMuFilterp->Write();
muonUpStreamp->Write();
muonDownStreamp->Write();

mupassing_p->Write();
muTunnelp->Write();

pgamma_yz->Write();
pneutron_yz->Write();
pgamma_p->Write();
pneutron_p->Write();

pintgamma_p->Write();
pintneutron_p->Write();
pintgamma_p_in->Write();
pintneutron_p_in->Write();

pint_ingamma_p->Write();
pint_inneutron_p->Write();
pint_ingamma_p_in->Write();
pint_inneutron_p_in->Write();

pgamma_yz_in->Write();
pneutron_yz_in->Write();
pgamma_p_in->Write();
pneutron_p_in->Write();

molt_mu_ch->Write();
molt_mu_n->Write();
molt_mu_ch_in->Write();
molt_mu_n_in->Write();

neutral_p->Write();
neutr_distxy->Write();
neutr_distyz->Write();

neutral_p_out->Write();
neutr_distxy_out->Write();
neutr_distyz_out->Write();


neutral_p_in->Write();
neutr_distxy_in->Write();
neutr_distyz_in->Write();


daughts_c->Write();
daughts_n->Write();
f1->Close();
}// loop func


void background_condor(int clusterID, int procID, bool mu_minus = true){
    TString sims_path = "/eos/experiment/sndlhc/MonteCarlo/MuonBackground/muons_up/";
    TString prefix = "sndLHC.Ntuple-TGeant4-Up_run";
    RVec<TString> filename = {"N1_20_dig", "N21_40_dig", "N41_60_dig", "N61_80_dig", "N81_99_dig"};
    if(mu_minus == false) filename = {"P1_20_dig", "P21_40_dig", "P41_60_dig", "P61_80_dig", "P81_99_dig"};
    TString ext = ".root";
    TString savepath = "/afs/cern.ch/work/d/dannc/public/histo_saves/";
    TString geofile = "geofile_full.Ntuple-TGeant4.root";
    TString clusID;
    clusID.Form("%d", clusterID);
    int evstart = (procID%10)*10000;
    int increment = 10000;
    int evend = evstart + increment;
    int iFile = procID/10;

    TFile *file = new TFile(sims_path+prefix+filename[iFile]+ext);
    if(!file) return;
    TTreeReader reader("cbmsim", file);
    if(evend > reader.GetEntries(true)) evend = reader.GetEntries(true);
    file->Close();

    //Loop(sims_path+prefix+filename+ext, savepath, clusID+".histos_"+filename+"_ev"+evstart+"to"+evend+"_25fb.root", sims_path+geofile, evstart, evend);
    if(mu_minus == true) muon_background(sims_path+prefix+filename[iFile]+ext, savepath, clusID+".histos_"+filename[iFile]+"_ev"+evstart+"to"+evend+"_25fb_muonback.root", sims_path+geofile, evstart, evend);
    if(mu_minus == false) muon_background(sims_path+prefix+filename[iFile]+ext, savepath, clusID+".histos_"+filename[iFile]+"_ev"+evstart+"to"+evend+"_25fb_antimuonback.root", sims_path+geofile, evstart, evend, true);
    cout << "- histos from " << prefix+filename[iFile] << " Successfully created at " << savepath <<endl;
}

void background_offline(int evstart, int evend, int clusterID, int iFile, bool mu_minus = true){
    TString sims_path = "/eos/experiment/sndlhc/MonteCarlo/MuonBackground/muons_up/";
    TString prefix = "sndLHC.Ntuple-TGeant4-Up_run";
    RVec<TString> filename = {"N1_20_dig", "N21_40_dig", "N41_60_dig", "N61_80_dig", "N81_99_dig"};
    if(mu_minus == false) filename = {"P1_20_dig", "P21_40_dig", "P41_60_dig", "P61_80_dig", "P81_99_dig"};
    TString ext = ".root";
    TString savepath = "/afs/cern.ch/work/d/dannc/public/histo_saves/";
    TString geofile = "geofile_full.Ntuple-TGeant4.root";
    TString clusID;
    clusID.Form("%d", clusterID);

    TFile *file = new TFile(sims_path+prefix+filename[iFile]+ext);
    if(!file) return;
    TTreeReader reader("cbmsim", file);
    if(evend > reader.GetEntries(true)) evend = reader.GetEntries(true);
    file->Close();

    //Loop(sims_path+prefix+filename+ext, savepath, clusID+".histos_"+filename+"_ev"+evstart+"to"+evend+"_25fb.root", sims_path+geofile, evstart, evend);
    if(mu_minus == true) muon_background(sims_path+prefix+filename[iFile]+ext, savepath, clusID+".histos_"+filename[iFile]+"_ev"+evstart+"to"+evend+"_25fb_muonback.root", sims_path+geofile, evstart, evend);
    if(mu_minus == false) muon_background(sims_path+prefix+filename[iFile]+ext, savepath, clusID+".histos_"+filename[iFile]+"_ev"+evstart+"to"+evend+"_25fb_antimuonback.root", sims_path+geofile, evstart, evend, true);
    cout << "- histos from " << prefix+filename[iFile] << " Successfully created at " << savepath <<endl;
}
/*************************
N. neutral particles 21948713
N. outer neutral particles  21608055
N. inner neutral particles  340658
% of  inner production w.r.t. total 0.01552063668
**************************/
