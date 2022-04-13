#include "histocanvas.h"
#include "TInterpreter.h"
#include "TTreeReader.h"
#include "TH1.h"
#include "TH2.h"
using namespace ROOT;

float GetP_det(Double32_t Px, Double32_t Py, Double32_t Pz){
	float p = TMath::Sqrt(Px*Px+Py*Py+Pz*Pz);
	return p;
}
bool isVertical(int DetID){
  if  (floor(DetID/10000)==3&&DetID%1000>59) {return kTRUE;}
  else{return kFALSE;}
}

void dis_analysis(TString inputfile, TString savepath, TString filename, TString geofile, TString crsecfile){
    TStopwatch mychrono;
    mychrono.Start();
    TFile *file = new TFile(inputfile);
    gGeoManager->Import(geofile);
    if(!file) return;
    TFile *file2 = new TFile(crsecfile);
    if(!file2) return;

    TGraph *crsec = (TGraph*) file2->Get("g_13");
    /* crsec->Eval(muontrack.GetEnergy); */

    cout << "- Reading file : " << inputfile << endl;
    cout << "- Reading geofile : " << geofile << endl;
    cout << "- Reading cross-section file : " << crsecfile << endl;

    TTreeReader reader("cbmsim", file);
    TTreeReaderArray <ShipMCTrack>  tracks(reader, "MCTrack");
    TTreeReaderArray <ScifiPoint>   scifipoints(reader, "ScifiPoint");
    TTreeReaderArray <MuFilterPoint>   mufilterpoints(reader, "MuFilterPoint");
    TDatabasePDG *b=TDatabasePDG::Instance();

    /******* HISTOS *****************/
    TH2F *mu_xy_N_int = new TH2F("mu_xy_N_int", "XY distribution of interaction points of neutrons associated with muon", 200, -140, 60, 200, -60, 140);
    TH2F *mu_yz_N_int = new TH2F("mu_yz_N_int", "YZ distribution of interaction points of neutrons associated with muon", 400, -100, 300, 400, -160, 240);
    TH1F *muneutron_int_p = new TH1F("muneutron_int_p", "Momentum distribution of neutron interacting in SND associated with muon", 300, 0, 300);
    TH2F *nomu_xy_N_int = new TH2F("nomu_xy_N_int", "XY distribution of interaction points of neutrons not associated with muon", 200, -140, 60, 200, -60, 140);
    TH2F *nomu_yz_N_int = new TH2F("nomu_yz_N_int", "YZ distribution of interaction points of neutrons not associated with muon", 400, -100, 300, 400, -160, 240);
    TH1F *nomuneutron_int_p = new TH1F("nomuneutron_int_p", "Momentum distribution of neutron interacting in SND not associated with muon", 300, 0, 300);
    TH1F *neutron_chdau_mu_p = new TH1F("neutron_chdau_mu_p", "Momentum of neutron charged daughters associated with muon", 300, 0, 300);
    TH1F *neutron_chdau_nomu_p = new TH1F("neutron_chdau_nomu_p", "Momentum of neutron charged daughters not associated with muon", 150, 0, 150);
    TH1F *neutron_chdau_mu = new TH1F("neutron_chdau_mu", "Multiplicity of neutron charged daughters associated with muon", 32, -0.5, 31.5);
    TH1F *neutron_chdau_nomu = new TH1F("neutron_chdau_nomu", "Multiplicity of neutron charged daughters not associated with muon", 32, -0.5, 31.5); 
    TH1F *neutron_chdau_nomu_p_ecut = new TH1F("neutron_chdau_nomu_p_ecut", "Momentum of neutron charged daughters not associated with muon (E > 1 GeV)", 150, 0, 150);
    TH1F *neutron_chdau_nomu_1G = new TH1F("neutron_chdau_nomu_1G", "Multiplicity of neutron charged daughters not associated with muon (E > 1 GeV)", 32, -0.5, 31.5);
    TH1F *moltnchdau_scifi = new TH1F("moltnchdau_scifi","Multiplicity of neutron charged daughters hitting Scifi", 32, -0.5, 31.5);
    TH1F *moltnchdau_mufilt = new TH1F("moltnchdau_mufilt","Multiplicity of neutron charged daughters hitting MuFilter", 32, -0.5, 31.5);

    /******** VARIABLES *************/
    int nevents = reader.GetEntries(true);
    cout << "- Number of events " << nevents << endl;
    cout.precision(10);
    int ientry = 0;
    int pdgcode, charge;
    int itrack = 0;
    const float crossect_fb = 8E+13;
    const float collision_rate = 8E+8;
    const float Luminosity = 25;
    const float collision_rate25fb = Luminosity*crossect_fb;  
    const float nppevent = 78E+6; // for fluka muons_up_V1
    const float normalization = collision_rate/nppevent;
    const float normalization2 = collision_rate25fb/nppevent;
    const float nMult = 10;
    const char *volName;

    /************* LOOP *****************/
    while (reader.Next())
    {
        ientry = reader.GetCurrentEntry();
        itrack = 0;
        ShipMCTrack muontrack = tracks[0];
        /*** WEIGHTS ***/
        float W = normalization*muontrack.GetWeight();
        float W2 = normalization2*muontrack.GetWeight();
        float wLHC = W2/nMult;
        float wInter = tracks[2].GetWeight();
        float wDis = 0.6E-3*crsec->Eval(muontrack.GetEnergy());
        float WEIGHT = wLHC*wInter*wDis;
        bool int_N;
        bool scifi_int = false;
        bool mufilt_int = false;
        /******* DETECTORS LOOP *******/

        for(ScifiPoint& scifipoint: scifipoints){
            if(scifipoint.PdgCode()==13){scifi_int = true; break;}
        }// scifi point

        for(MuFilterPoint& mufilterpoint: mufilterpoints){
            if(mufilterpoint.PdgCode()==13){mufilt_int = true; break;}
        }// mufilt point

        /******* TRACKS LOOP ******/
        for(ShipMCTrack& track: tracks){
            itrack++;
            if(itrack == 1) continue; // excludes the backward muon
            pdgcode = track.GetPdgCode();
            charge = 0;
            int_N = false;
            if(b->GetParticle(pdgcode) != NULL) charge = b->GetParticle(pdgcode)->Charge();
            if(gGeoManager->FindNode(track.GetStartX(), track.GetStartY(), track.GetStartZ())->GetMotherVolume() != NULL) volName = gGeoManager->FindNode(track.GetStartX(), track.GetStartY(), track.GetStartZ())->GetMotherVolume()->GetName(); 
            

            /* Neutron with muon */
        if(mufilt_int == true || scifi_int == true){ 
            if(pdgcode == 2112){
                int neutron_nchdau_mu = 0;
                for(ShipMCTrack& track2: tracks){
                    if(gGeoManager->FindNode(track2.GetStartX(), track2.GetStartY(), track2.GetStartZ())->GetMotherVolume() != NULL){
                        if(track2.GetMotherId()==itrack){
                            if(strncmp(gGeoManager->FindNode(track2.GetStartX(), track2.GetStartY(), track2.GetStartZ())->GetMotherVolume()->GetName(), "Tunnel", 6)!=0){
                                int_N = true;
                                //cout << "MU IN:" << endl;
                                //cout << "ev no. " << ientry << " process " << track.GetProcName() << endl;
                                //cout << "       produced " << track2.GetPdgCode() << " in " <<  gGeoManager->FindNode(track2.GetStartX(), track2.GetStartY(), track2.GetStartZ())->GetName() << endl;
                                mu_xy_N_int->Fill(track2.GetStartX(), track2.GetStartY(), WEIGHT);
                                mu_yz_N_int->Fill(track2.GetStartZ(), track2.GetStartY(), WEIGHT);
                                if(b->GetParticle(track2.GetPdgCode()) != NULL){
                                    if(b->GetParticle(track2.GetPdgCode()) != 0){ // charged particles from neutron
                                        neutron_nchdau_mu++;
                                        neutron_chdau_mu_p->Fill(track2.GetP(), WEIGHT);
                                    }
                                }
                            }
                        }
                    } 
                }// closes nested loop
            if(int_N == true) {muneutron_int_p->Fill(track.GetP(), WEIGHT);}
            if(neutron_nchdau_mu !=0) neutron_chdau_mu->Fill(neutron_nchdau_mu, WEIGHT);
            }// pdgcode 2112
        }
            /* Neutron without muon */
        if(mufilt_int == false && scifi_int == false){ 
            if(pdgcode == 2112){
                int neutron_nchdau_nomu = 0;
                int neutron_nchdau_nomu_1G = 0;
                for(ShipMCTrack& track2: tracks){
                    if(gGeoManager->FindNode(track2.GetStartX(), track2.GetStartY(), track2.GetStartZ())->GetMotherVolume() != NULL){
                        if(track2.GetMotherId()==itrack){
                            if(strncmp(gGeoManager->FindNode(track2.GetStartX(), track2.GetStartY(), track2.GetStartZ())->GetMotherVolume()->GetName(), "Tunnel", 6)!=0){
                                int_N = true;
                                //cout << "NO MU IN:" << endl;
                                //cout << "ev no. " << ientry << " process " << track.GetProcName() << endl;
                                //cout << "       produced " << track2.GetPdgCode() << " in " <<  gGeoManager->FindNode(track2.GetStartX(), track2.GetStartY(), track2.GetStartZ())->GetName() << endl;
                                nomu_xy_N_int->Fill(track2.GetStartX(), track2.GetStartY(), WEIGHT);
                                nomu_yz_N_int->Fill(track2.GetStartZ(), track2.GetStartY(), WEIGHT);
                                if(b->GetParticle(track2.GetPdgCode()) != NULL){
                                    if(b->GetParticle(track2.GetPdgCode())->Charge() != 0){ // charged particles from neutron
                                        neutron_nchdau_nomu++;
                                        neutron_chdau_nomu_p->Fill(track2.GetP(), WEIGHT);
                                        if(track2.GetP()>=1.) {neutron_nchdau_nomu_1G++; neutron_chdau_nomu_p_ecut->Fill(track2.GetP(), WEIGHT);}
                                    }
                                }
                            }
                        }
                    } 
                }// closes nested loop
            if(int_N == true) {nomuneutron_int_p->Fill(track.GetP(), WEIGHT);}
            if(neutron_nchdau_nomu !=0) neutron_chdau_nomu->Fill(neutron_nchdau_nomu, WEIGHT);
            if(neutron_nchdau_nomu_1G !=0) neutron_chdau_nomu_1G->Fill(neutron_nchdau_nomu_1G, WEIGHT);
            }// pdgcode 2112
        }

        }// closes MCTrack

        /***** Searching for neutron charged daughters hit in elctronic detectors (counting per neutron) ******/
        itrack = 0;
        for(ShipMCTrack& track: tracks){
            itrack ++;
            if(itrack == 1) continue; 
            if(track.GetPdgCode() == 2112){
                /*** Searching in Scifi ***/
                int scifi_detmem = -1000;
                int scifi_trackmem = -2000;
                int nchdau_scifi = 0;
                for(ScifiPoint& scifipoint: scifipoints){
                    int scifiTrackID = scifipoint.GetTrackID();
                    int scifiDetID = scifipoint.station();
                    if(scifi_trackmem == scifiTrackID && scifi_detmem == scifiDetID) continue; //avoiding repetition for same scifi
                    if(scifiTrackID > -1){
                        if(gGeoManager->FindNode(tracks[scifiTrackID].GetStartX(), tracks[scifiTrackID].GetStartY(), tracks[scifiTrackID].GetStartZ())->GetMotherVolume() != NULL){
                            if(strncmp(gGeoManager->FindNode(tracks[scifiTrackID].GetStartX(), tracks[scifiTrackID].GetStartY(), tracks[scifiTrackID].GetStartZ())->GetMotherVolume()->GetName(), "Tunnel", 6)!=0){
                                if(tracks[scifiTrackID].GetMotherId() == itrack){
                                    if(b->GetParticle(scifipoint.PdgCode()) != NULL){
                                        if(b->GetParticle(scifipoint.PdgCode())->Charge()!=0){
                                            nchdau_scifi++;
                                            //cout << "ev no. " << ientry << " particle " << scifipoint.PdgCode() << " Mother Id " << tracks[scifiTrackID].GetMotherId() << " Track id " << scifiTrackID << endl;
                                        }
                                    }
                                }
                            }
                        }
                    }
                    scifi_trackmem = scifiTrackID;
                    scifi_detmem = scifiDetID;
                } // scifi point
                /** Fill histogram per neutron **/
                if(nchdau_scifi !=0) moltnchdau_scifi->Fill(nchdau_scifi, WEIGHT);
                /*** Searching in MuFilter ***/
                int mufilt_detmem = -1000;
                int mufilt_trackmem = -2000;
                int nchdau_mufilt = 0;
                for(MuFilterPoint& mufilterpoint: mufilterpoints){
                    int mufiltTrackID = mufilterpoint.GetTrackID();
                    if(mufilterpoint.GetDetectorID()/10000 == 1) continue; //excludes VetoPlane
                    int mufilt_UpDown = mufilterpoint.GetDetectorID()/10000;
                    int mufiltstation = mufilterpoint.GetDetectorID()/1000%10;
                    if(mufilt_UpDown == 3 && mufiltstation == 3) continue; // excludes last vertical plane
                    if(isVertical(mufilterpoint.GetDetectorID())== kTRUE) continue; // excludes vertical bars on Downstream
                    if(mufilt_trackmem == mufiltTrackID && mufilt_detmem == mufiltstation) continue; //avoiding repetition for same mufilter
                    if(mufiltTrackID > -1){
                        if(gGeoManager->FindNode(tracks[mufiltTrackID].GetStartX(), tracks[mufiltTrackID].GetStartY(), tracks[mufiltTrackID].GetStartZ())->GetMotherVolume() != NULL){
                            if(strncmp(gGeoManager->FindNode(tracks[mufiltTrackID].GetStartX(), tracks[mufiltTrackID].GetStartY(), tracks[mufiltTrackID].GetStartZ())->GetMotherVolume()->GetName(), "Tunnel", 6)!=0){
                                if(tracks[mufiltTrackID].GetMotherId()== itrack){
                                    if(b->GetParticle(mufilterpoint.PdgCode()) != NULL){
                                        if(b->GetParticle(mufilterpoint.PdgCode())->Charge()!=0){
                                            nchdau_mufilt++;
                                        }
                                    }
                                }
                            }
                        }
                    }
                    mufilt_trackmem = mufiltTrackID;
                    mufilt_detmem = mufiltstation;
                } // mufilter point
                /** Fill histogram per neutron **/
                if(nchdau_mufilt !=0) moltnchdau_mufilt->Fill(nchdau_mufilt, WEIGHT);
            }// if on neutron mc
        } // closes mctrack
    
    
    } // while
/********* WRITING TO FILE **********/
TFile *f1=new TFile(savepath+filename, "RECREATE");

muneutron_int_p->Write();
nomu_xy_N_int->Write();
nomu_yz_N_int->Write();
nomuneutron_int_p->Write();
//neutron_chdau_mu_p->Write();
neutron_chdau_nomu_p->Write();
neutron_chdau_nomu_p_ecut->Write();
//neutron_chdau_mu->Write();
neutron_chdau_nomu->Write();
neutron_chdau_nomu_1G->Write();
moltnchdau_mufilt->Write();
moltnchdau_scifi->Write();

f1->Close();
file->Close();
file2->Close();
cout <<"-- " << filename << " saved at " << savepath << endl;
mychrono.Stop();
cout << "++++ Elapsed time ++++";
mychrono.Print(); 
cout << "++++++++++++++++++++++" << endl;
}

void dis_condor(int clusterID, int run, bool singleshot = false){
    TString sims_path = "/eos/experiment/sndlhc/MonteCarlo/MuonBackground/muonDis/";
    TString muproton_prefix = "ecut1.0/ecut1.0_run_1";
    TString muneutron_prefix = "ecut1.0/ecut1.0_run_6";
    TString simfile = "ship.conical.muonDIS-TGeant4.root";
    TString savepath = "/afs/cern.ch/work/d/dannc/public/histo_dis/";
    TString geofile = "geofile_full.conical.muonDIS-TGeant4.root";
    TString crsecfile = "/eos/experiment/sndlhc/MonteCarlo/Pythia6/MuonDIS/muDIScrossSec.root";
    TString clusID;
    TString runID;
    runID.Form("%02d", run);
    clusID.Form("%d", clusterID);
    TString i_file;
    if(singleshot == false){
        for(int i = 0; i< 200; i++){
            i_file.Form("%d", i);
            dis_analysis(sims_path+muproton_prefix+runID+"_"+i_file+"/"+simfile, savepath, clusID+".histos_ecut1.0_run_1"+runID+"_"+i_file+".root", sims_path+"ecut1.0/"+geofile, crsecfile);
            dis_analysis(sims_path+muneutron_prefix+runID+"_"+i_file+"/"+simfile, savepath, clusID+".histos_ecut1.0_run_6"+runID+"_"+i_file+".root", sims_path+"ecut1.0/"+geofile, crsecfile);
        }// for loop
    }
    if(singleshot == true){
        i_file = "0";
        dis_analysis(sims_path+muproton_prefix+runID+"_"+i_file+"/"+simfile, savepath, clusID+".histos_ecut1.0_run_1"+runID+"_"+i_file+".root", sims_path+"ecut1.0/"+geofile, crsecfile);
        dis_analysis(sims_path+muneutron_prefix+runID+"_"+i_file+"/"+simfile, savepath, clusID+".histos_ecut1.0_run_6"+runID+"_"+i_file+".root", sims_path+"ecut1.0/"+geofile, crsecfile);
    }  
    
    cout << "- histos from" << sims_path+muproton_prefix+runID << " Successfully created at " << savepath <<endl;
    cout << "- histos from" << sims_path+muneutron_prefix+runID << " Successfully created at " << savepath <<endl;
}