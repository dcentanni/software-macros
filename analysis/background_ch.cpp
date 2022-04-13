#include "histocanvas.h"
#include "TInterpreter.h"
#include "TTreeReader.h"
#include "TH1.h"
#include "TH2.h"

/**************************
    EXPERIMENT DIMENSIONS

        START       END
X       -82.800     -2.000
Y         5.750     69.600
Z       -33.475    217.095
***************************/

void Loop(string inputfile, string savepath, string filename, string geofile){

    TFile *file = new TFile((inputfile).c_str());
    gGeoManager->Import((geofile).c_str());
    if(!file) return;
    cout << "Reading file : " << inputfile << endl;
    cout << "Reading geofile : " << geofile << endl;

    TTreeReader reader("cbmsim", file);
    TTreeReaderArray <ShipMCTrack> tracks(reader, "MCTrack");

    gStyle->SetCanvasDefH(757);
    gStyle->SetCanvasDefW(1190);
    gStyle->SetOptStat("emr");
    TDatabasePDG *b=TDatabasePDG::Instance();
    /******* HISTOS *****************/
    TH1F *muon_p = new TH1F("muon_p", "Momentum of primary background muons", 250, 0, 3500);
    TH2F *muonint_distyz_in = new TH2F("muonint_distyz_in", "YZ Distribution of interacting points of background muons", 1400, -700, 700, 150, -50, 100);


    TH1F *neutral_p = new TH1F("neutral_p", "Momentum neutral particles", 1000, 0, 1000);
    TH2F *neutr_distxy = new TH2F("neutr_distxy", "XY Distribution of starting pos of neutral particles", 1000, -200, 30, 1000, -50, 100);
    TH2F *neutr_distyz = new TH2F("neutr_distyz", "YZ Distribution of starting pos of neutral particles", 1000, -700, 700, 1000, -50, 100);
    
    TH1F *neutral_p_out = new TH1F("neutral_p_out", "Outer neutral particles momentum", 1000, 0, 1000);
    TH2F *neutr_distxy_out = new TH2F("neutr_distxy_out", "XY Distribution of starting pos of outer neutral particles", 1000, -200, 30, 1000, -50, 100);
    TH2F *neutr_distyz_out = new TH2F("neutr_distyz_out", "YZ Distribution of starting pos of outer neutral particles", 1400, -700, 700, 150, -50, 100);
    TH3F *particle_cloud_out = new TH3F("particle_cloud_out", "3D distrib. of starting pos of outer neutral particles", 230, -200, 30, 150, -50, 100, 300, -50, 250);
    
    TH1F *neutral_p_in = new TH1F("neutral_p_in", "Inner neutral particles momentum", 1000, 0, 1000);
    TH2F *neutr_distxy_in = new TH2F("neutr_distxy_in", "XY Distribution of starting pos of inner neutral particles", 1400, -700, 700, 150, -50, 100);
    //TH2F *neutr_distxy_in = new TH2F("neutr_distxy_in", "XY Distribution of starting pos of inner neutral particles", 1000, -200, 30, 1000, -50, 100);
    TH2F *neutr_distyz_in = new TH2F("neutr_distyz_in", "YZ Distribution of starting pos of inner neutral particles", 1400, -700, 700, 150, -50, 100);
    TH3F *particle_cloud_in = new TH3F("particle_cloud_in", "3D distrib. of starting pos of inner neutral particles", 230, -200, 30, 150, -50, 100, 300, -50, 250);
    
    TH1I *daughts_c = new TH1I("daughts_c", "Multiplicity of charged daughters from neutral particles", 11, -0.5, 10.5);
    TH1I *daughts_n = new TH1I("daughts_n", "Multiplicity of neutral daughters from neutral particles", 61, -0.5, 60.5);
    /******** VARIABLES *************/
    int ientry = 0;
    int pdgcode, charge;
    int itrack = 0;
    int nevents = reader.GetEntries(true);
    int nnparts =0;
    int nnparts_out = 0;
    int daug_c = 0; int daug_n = 0;
    cout << "Number of events " << nevents << endl;
    cout.precision(10);
    const char *volName;


    /*********** MAIN LOOP **********/

    while (reader.Next())
    {
        ientry = reader.GetCurrentEntry();
        itrack = 0;
    if(ientry <= 10000){
        ShipMCTrack muontrack = tracks[0];
        muon_p->Fill(muontrack.GetP());
        for(ShipMCTrack& track: tracks){
            itrack++;
            pdgcode = track.GetPdgCode();
            charge=0;
            if(b->GetParticle(pdgcode) != NULL) charge = b->GetParticle(pdgcode)->Charge();
            if(gGeoManager->FindNode(track.GetStartX(), track.GetStartY(), track.GetStartZ())->GetMotherVolume() != NULL) volName = gGeoManager->FindNode(track.GetStartX(), track.GetStartY(), track.GetStartZ())->GetMotherVolume()->GetName();
            if(track.GetMotherId()==0){
                if(strncmp(volName, "Tunnel", 6)!=0){ 
                    muonint_distyz_in->Fill(track.GetStartZ(), track.GetStartY());
                    cout << "Particle " << track.GetPdgCode() << " MotherId " << track.GetMotherId() << " volName " << volName << endl;
                }
            }
            
        // get Neutral Particles
            if(charge==0){
                /*for(ShipMCTrack& track2: tracks){
                    if(track2.GetMotherId()== itrack){ //cout << "Ev. no. " << ientry << " Daughter " << track2.GetPdgCode() << " " << track2.GetMotherId() << " Mother PDGcode " << track.GetPdgCode() << " itrack: " << itrack << " Proc name " << track2.GetProcName() << endl;
                        //if(track.GetPdgCode()==22 && track2.GetPdgCode()!=11 && track2.GetPdgCode()!=-11 && track2.GetPdgCode()!=13 && track2.GetPdgCode()!=-13 && track2.GetPdgCode()!=22) cout << "ev no. " << ientry << " daughter " << track2.GetPdgCode() << " Proc name " << track2.GetProcName() << endl;
                        if(b->GetParticle(track2.GetPdgCode()) != NULL){
                        if(b->GetParticle(track2.GetPdgCode())->Charge()!=0)    daug_c++;
                        if(b->GetParticle(track2.GetPdgCode())->Charge()==0)    daug_n++;}
                        }
                    }
                    //cout << "daugh_c " << daug_c << endl;
                    //if(daug_n > 36) cout << "ev no. " << ientry << " daug_n " << daug_n << endl;
                    daughts_c->Fill(daug_c);
                    daughts_n->Fill(daug_n);
                    daug_c = 0;
                    daug_n = 0;*/
                neutral_p->Fill(track.GetP());
                neutr_distxy->Fill(track.GetStartX(), track.GetStartY());
                neutr_distyz->Fill(track.GetStartZ(), track.GetStartY());
                 
                if(strncmp(volName, "Tunnel", 6)!=0)
                    {
                        //cout << "Ev. no. " << ientry << " Particle " << track.GetPdgCode() << " Volume " << volName << endl;
                        neutral_p_in->Fill(track.GetP());
                        neutr_distxy_in->Fill(track.GetStartX(), track.GetStartY());
                        neutr_distyz_in->Fill(track.GetStartZ(), track.GetStartY());
                        particle_cloud_in->Fill(track.GetStartX(), track.GetStartY(), track.GetStartZ());
                }
                else{
                        neutral_p_out->Fill(track.GetP());
                        neutr_distxy_out->Fill(track.GetStartX(), track.GetStartY());
                        neutr_distyz_out->Fill(track.GetStartZ(), track.GetStartY());
                        particle_cloud_out->Fill(track.GetStartX(), track.GetStartY(), track.GetStartZ());
                }
            }// if charge 
            
        }// loop on track
        
    }//if ientry



        
    }// main loop
    
//TCanvas *c1;
//DoCanvas(c1, "c1", neutral_p, "Momentum (GeV/c)", "Counts");
cout << "N. neutral particles " << neutral_p->GetEntries() << endl;
cout << "N. outer neutral particles  " << neutral_p_out->GetEntries() << endl;
cout << "N. inner neutral particles  " << neutral_p_in->GetEntries() << endl;
cout << "% of  inner production w.r.t. total " << neutral_p_in->GetEntries()/neutral_p->GetEntries() << endl;
/********* WRITING TO FILE **********/
TFile *f1=new TFile((savepath+filename).c_str(), "RECREATE");
muon_p->Write();
muonint_distyz_in->Write();

neutral_p->Write();
neutr_distxy->Write();
neutr_distyz->Write();

neutral_p_out->Write();
neutr_distxy_out->Write();
neutr_distyz_out->Write();
particle_cloud_out->Write();

neutral_p_in->Write();
neutr_distxy_in->Write();
neutr_distyz_in->Write();
particle_cloud_in->Write();

daughts_c->Write();
daughts_n->Write();
f1->Close();
}// loop func

void background_ch(){
    string sims_path = "/eos/experiment/sndlhc/MonteCarlo/MuonBackground/muons_up/";
    string prefix = "sndLHC.Ntuple-TGeant4-Up_run";
    string filename = "N1_20_dig.root";
    string savepath = "/eos/user/d/dannc/SND_sim/histo_saves/";
    string geofile = "geofile_full.Ntuple-TGeant4.root";

    Loop(sims_path+prefix+filename, savepath, ("offline_histos_from_"+filename).c_str(), sims_path+geofile);
    cout << "histos_from_" << filename << " Successfully created at " << savepath <<endl;
}
/*************************
N. neutral particles 21948713
N. outer neutral particles  21608055
N. inner neutral particles  340658
% of  inner production w.r.t. total 0.01552063668
**************************/

