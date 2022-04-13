#include "histocanvas.h"
#include "TInterpreter.h"
#include "TTreeReader.h"
#include "TH1.h"
#include "TH2.h"
using namespace ROOT;

void muonrate_scoringplane(TChain *chain, TString savepath, TString clusID){
    TTreeReader reader(chain);

    TTreeReaderArray <ShipMCTrack>  tracks(reader, "MCTrack");
    TTreeReaderArray <ScifiPoint>   scifipoints(reader, "ScifiPoint");
    TTreeReaderArray <MuFilterPoint>   mufilterpoints(reader, "MuFilterPoint");

    int nevents = reader.GetEntries(true);
    cout<<"Number of events: "<<nevents<<endl;
    cout.precision(10);

    double lplane = 0;
    const float crossect_fb = 8E+13;
    const float collision_rate = 8E+8;
    const float Luminosity = 25;
    const float collision_rate25fb = Luminosity*crossect_fb;  
    const float nppevent = 78E+6; // for fluka muons_up_V1
    const float normalization = collision_rate/nppevent;
    const float normalization2 = collision_rate25fb/nppevent;
    const double scifi_plane = 1600;
    const double mufilt_plane = 5108;

    TGraph *scifi_scplane = new TGraph();
    TGraph *mufilt_scplane = new TGraph();
    TGraph *sndlhc_scplane = new TGraph();
    TGraph *general_scplane = new TGraph();
    TGraph *scifi_eff_scplane = new TGraph();
    TGraph *mufilt_eff_scplane = new TGraph();

    //for (int i = 0; i < 91; i++){

        TH1F *muon_p = new TH1F("muon_p", "Momentum of background muons", 250, 0, 3500);
        TH1F *scifi_p = new TH1F("scifi_p", "Momentum of background muons hitting scifi", 250, 0, 3500);
        TH1F *mufilter_p = new TH1F("mufilter_p", "Momentum of background muons hitting mufilter", 250, 0, 3500);
        TH1F *sndlhc_p = new TH1F("sndlhc_p", "Momentum of background muons hitting SND@LHC", 250, 0, 3500);
        TH2F *mu_xy = new TH2F("mu_xy", "XY Distribution of incoming muons", 200, -100, 100, 200, -100, 100);
        TH2F *mu_xy_scifi = new TH2F("mu_xy_scifi", "XY Distribution of incoming muons hitting Scifi", 200, -100, 100, 200, -100, 100);
        TH2F *mu_xy_mufilt = new TH2F("mu_xy_mufilt", "XY Distribution of incoming muons hitting MuFilter", 200, -100, 100, 200, -100, 100);
        TH1F *strange_scifi_mu_p = new TH1F("strange_scifi_mu_p", "Momentum of scifi strange muons", 250, 0, 3500);
        TH1F *strange_mufilt_mu_p = new TH1F("strange_mufilt_mu_p", "Momentum of mufilt strange muons", 250, 0, 3500);
        TH1F *strange_scifi_mu_tx = new TH1F("strange_scifi_mu_tx", "TX distribution for scifi strange muons", 400, -0.2, 0.2);
        TH1F *strange_scifi_mu_ty = new TH1F("strange_scifi_mu_ty", "TY distribution for scifi strange muons", 400, -0.2, 0.2);
        TH1F *strange_mufilt_mu_tx = new TH1F("strange_mufilt_mu_tx", "TX distribution for mufilt strange muons", 400, -0.2, 0.2);
        TH1F *strange_mufilt_mu_ty = new TH1F("strange_mufilt_mu_ty", "TY distribution for mufilt strange muons", 400, -0.2, 0.2);
        TH1F *mu_theta = new TH1F("mu_theta", "Theta distribution of background muons", 400, -0.4, 0.4);
        TH1F *mu_theta_scifi = new TH1F("mu_theta_scifi", "Theta distribution of muons hitting Scifi", 300, 0, 0.03);
        TH1F *mu_theta_mufilt = new TH1F("mu_theta_mufilt", "Theta distribution of muons hitting MuFilter", 300, 0, 0.03);
        TH3F *mu_xy_energy_scifi = new TH3F("mu_xy_energy_scifi", "XY starting position and Energy of muons hitting Scifi", 200, -100, 100, 200, -100, 100, 250, 0, 3500);
        TH3F *mu_xy_energy_mufilt = new TH3F("mu_xy_energy_mufilt", "XY starting position and Energy of muons hitting MuFilter", 200, -100, 100, 200, -100, 100, 250, 0, 3500);
        TH3F *mu_xy_theta_scifi = new TH3F("mu_xy_theta_scifi", "XY starting position and theta of muons hitting Scifi", 200, -100, 100, 200, -100, 100, 300, 0, 0.03);
        TH3F *mu_xy_theta_mufilt = new TH3F("mu_xy_theta_mufilt", "XY starting position and theta of muons hitting MuFilter", 200, -100, 100, 200, -100, 100, 300, 0, 0.03);
        TH2F *mu_energy_x_scifi = new TH2F("mu_energy_x_scifi", "Distribution Energy vs X starting position at Scifi", 200, -100, 100, 250, 0, 3500);
        TH2F *mu_tx_x_scifi = new TH2F("mu_tx_x_scifi", "Distribution TX vs X starting position at Scifi", 200, -100, 100, 200, -0.02, 0.02);
        TH2F *mu_ty_x_scifi = new TH2F("mu_ty_x_scifi", "Distribution TY vs X starting position at Scifi", 200, -100, 100, 200, -0.02, 0.02);      
        TH2F *mu_energy_x_mufilt = new TH2F("mu_energy_x_mufilt", "Distribution Energy vs X starting position at Mufilter", 200, -100, 100, 250, 0, 3500);
        TH2F *mu_tx_x_mufilt = new TH2F("mu_tx_x_mufilt", "Distribution TX vs X starting position at Mufilter", 200, -100, 100, 200, -0.02, 0.02);
        TH2F *mu_ty_x_mufilt = new TH2F("mu_ty_x_mufilt", "Distribution TY vs X starting position at Mufilter", 200, -100, 100, 200, -0.02, 0.02);
        TH3F *tx_x_energy_scifi = new TH3F("tx_x_energy_scifi", "TX vs X vs Energy of muons hitting Scifi", 200, -100, 100, 200, -0.02, 0.02, 250, 0, 3500);
        TH3F *tx_x_energy_mufilt = new TH3F("tx_x_energy_mufilt", "TX vs X vs Energy of muons hitting MuFilter", 200, -100, 100, 200, -0.02, 0.02, 250, 0, 3500);
	TH1F *firstcompProcID = new TH1F("firstcompProcID", "ProcID distrib of the 1st comp. of muons (bottom-left corner)", 10, 0.5, 10.5);  
	TH1F *secondcompProcID = new TH1F("secondcompProcID", "ProcID distrib of the 2nd comp. of muons (center)", 10, 0.5, 10.5);
	TH1F *thirdcompProcID = new TH1F("thirdcompProcID", "ProcID distrib of the 3rd comp. of muons (right)", 10, 0.5, 10.5);
        TH1F *mu_weight_scifi_in = new TH1F("mu_weight_scifi_in", "Muon event weight for #mu in Scifi", 150, 0, 0.15);
        TH1F *mu_weight_scifi_out = new TH1F("mu_weight_scifi_out", "Muon event weight for #mu out Scifi", 150, 0, 0.15);
        TH1F *mu_weight_mufilt_in = new TH1F("mu_weight_mufilt_in", "Muon event weight for #mu in MuonSystem", 150, 0, 0.15);
        TH1F *mu_weight_mufilt_out = new TH1F("mu_weight_mufilt_out", "Muon event weight for #mu out MuonSystem", 150, 0, 0.15);
        
        while (reader.Next())
        {
            int ientry = reader.GetCurrentEntry();
            ShipMCTrack muontrack = tracks[0];
            float W = normalization*muontrack.GetWeight();
            float W2 = normalization2*muontrack.GetWeight();
            bool mufilt_int = false;
            bool scifi_int = false;
            
            //if(TMath::Abs(muontrack.GetStartX()) < lplane/2. && TMath::Abs(muontrack.GetStartY()) < lplane/2.){
                //cout << muontrack.GetStartX() << " " << muontrack.GetStartY() << endl;
                muon_p->Fill(muontrack.GetP(), W2);
                mu_xy->Fill(muontrack.GetStartX(), muontrack.GetStartY(), W2);
                if(muontrack.GetPz()!=0) {float mu_tx = muontrack.GetPx()/muontrack.GetPz(); float mu_ty = muontrack.GetPy()/muontrack.GetPz();
                mu_theta->Fill(TMath::Sqrt(mu_tx*mu_tx+mu_ty*mu_ty), W2);}
                for(ScifiPoint& scifipoint: scifipoints){
                    if(scifipoint.GetTrackID()==0){
                    scifi_int = true;
                    scifi_p->Fill(muontrack.GetP(), W2);
                    //cout << "fuond scifi" << endl;
                    break;}
                }
                for(MuFilterPoint& mufilterpoint: mufilterpoints){
                if(mufilterpoint.GetTrackID()==0){
                    mufilt_int = true;
                    mufilter_p->Fill(muontrack.GetP(), W2);
                    //cout << "fuond mufilter" << endl;
                    break;}
                }
            if(scifi_int == true || mufilt_int == true) sndlhc_p->Fill(muontrack.GetP(), W2);
            if(scifi_int == true) { mu_xy_scifi->Fill(muontrack.GetStartX(), muontrack.GetStartY(), W2);
                                    if (muontrack.GetStartX() < 10. && muontrack.GetStartX() > -90. && muontrack.GetStartY() < 60. && muontrack.GetStartY() > 0.){
                                            mu_weight_scifi_in->Fill(muontrack.GetWeight());}
                                    else{   mu_weight_scifi_out->Fill(muontrack.GetWeight());}
                                        mu_xy_energy_scifi->Fill(muontrack.GetStartX(), muontrack.GetStartY(), muontrack.GetP(), W2);
                                        mu_energy_x_scifi->Fill(muontrack.GetStartX(), muontrack.GetP(), W2);

                                        if(muontrack.GetStartX()<= -40. && muontrack.GetStartX()>= -80. && muontrack.GetStartY()>=0. && muontrack.GetStartY()<=30.){
                                            //cout << "Muons in bottom left corner (Scifi) procID " << muontrack.GetProcID() << endl;
                                        }
                                        else{
                                            //cout << "Muons elsewhere " << muontrack.GetProcID() << endl;

                                        }
                                        if(muontrack.GetPz()!=0){
                                            double tx_scifi = muontrack.GetPx()/muontrack.GetPz(); double ty_scifi = muontrack.GetPy()/muontrack.GetPz();
                                            mu_theta_scifi->Fill(TMath::Sqrt(tx_scifi*tx_scifi+ty_scifi*ty_scifi), W2);

                                            mu_xy_theta_scifi->Fill(muontrack.GetStartX(), muontrack.GetStartY(), TMath::Sqrt(tx_scifi*tx_scifi+ty_scifi*ty_scifi), W2);
                                            mu_tx_x_scifi->Fill(muontrack.GetStartX(), tx_scifi, W2);
                                            mu_ty_x_scifi->Fill(muontrack.GetStartX(), ty_scifi, W2);
                                            tx_x_energy_scifi->Fill(muontrack.GetStartX(), tx_scifi, muontrack.GetP(), W2);
						if (tx_scifi < 0.01 && tx_scifi > 0.0025) firstcompProcID->Fill(muontrack.GetProcID(), W2);
						if (tx_scifi <= 0.0025 && tx_scifi > -0.0025) secondcompProcID->Fill(muontrack.GetProcID(), W2);
						if (tx_scifi <= -0.0025 && tx_scifi > -0.01) thirdcompProcID->Fill(muontrack.GetProcID(), W2);
                                        }
                                    }
            if(mufilt_int == true){ mu_xy_mufilt->Fill(muontrack.GetStartX(), muontrack.GetStartY(), W2);
                                    if (muontrack.GetStartX() < 10. && muontrack.GetStartX() > -90. && muontrack.GetStartY() < 60. && muontrack.GetStartY() > 0.){
                                            mu_weight_mufilt_in->Fill(muontrack.GetWeight());}
                                    else{   mu_weight_mufilt_out->Fill(muontrack.GetWeight());}

                                        mu_xy_energy_mufilt->Fill(muontrack.GetStartX(), muontrack.GetStartY(), muontrack.GetP(), W2);
                                        mu_energy_x_mufilt->Fill(muontrack.GetStartX(), muontrack.GetP(), W2);

                                        if(muontrack.GetStartX()<= -40. && muontrack.GetStartX()>= -100. && muontrack.GetStartY()>=0. && muontrack.GetStartY()<=30.){

                                        }
                                        if(muontrack.GetPz()!=0){
                                            double tx_mufilt = muontrack.GetPx()/muontrack.GetPz(); double ty_mufilt = muontrack.GetPy()/muontrack.GetPz();
                                            mu_theta_mufilt->Fill(TMath::Sqrt(tx_mufilt*tx_mufilt+ty_mufilt*ty_mufilt), W2);

                                            mu_xy_theta_mufilt->Fill(muontrack.GetStartX(), muontrack.GetStartY(), TMath::Sqrt(tx_mufilt*tx_mufilt+ty_mufilt*ty_mufilt), W2);
                                            mu_tx_x_mufilt->Fill(muontrack.GetStartX(), tx_mufilt, W2);
                                            mu_ty_x_mufilt->Fill(muontrack.GetStartX(), ty_mufilt, W2);
                                            tx_x_energy_mufilt->Fill(muontrack.GetStartX(), tx_mufilt, muontrack.GetP(), W2);
                                        }
                                    }
            //}// if on lplane
        }//while
    //reader.SetEntry(0);
    double intgr_general = muon_p->Integral();
    double intgr_scifi = scifi_p->Integral();
    double intgr_mufilt = mufilter_p->Integral();
    double intgr_snd = sndlhc_p->Integral();
    double rate_scifi = intgr_scifi/25E5;
    double rate_mufilt = intgr_mufilt/25E5;
    double rate_sndlhc = intgr_snd/25E5;
    double rate_general = intgr_general/25E5;
    double rate_scifi_cm2 = intgr_scifi/(scifi_plane*25E5);
    double rate_mufilt_cm2 = intgr_mufilt/(mufilt_plane*25E5);
    
    general_scplane->AddPoint(lplane*lplane, rate_general);
    scifi_scplane->AddPoint(lplane*lplane, rate_scifi_cm2);
    mufilt_scplane->AddPoint(lplane*lplane, rate_mufilt_cm2);
    sndlhc_scplane->AddPoint(lplane*lplane, rate_sndlhc);
    if(rate_general!=0){
    scifi_eff_scplane->AddPoint(lplane*lplane, rate_scifi/rate_general);
    mufilt_eff_scplane->AddPoint(lplane*lplane, rate_mufilt/rate_general);
    }
    cout << "Current scoring plane: " << lplane <<"x" << lplane << " cm2" << endl;
    lplane = lplane + 2.; //step = 2

    
    delete muon_p;
    delete scifi_p;
    delete mufilter_p;
    delete sndlhc_p;
    //} // for on plane
    general_scplane->GetXaxis()->SetTitle("Scoring plane (cm^{2})");
    general_scplane->GetYaxis()->SetTitle("Muon rate");
    general_scplane->SetNameTitle("general_scplane", "Muon rate vs Scoring plane");
    scifi_scplane->GetXaxis()->SetTitle("Scoring plane (cm^{2})");
    scifi_scplane->GetYaxis()->SetTitle("Muon rate Hz/cm2");
    scifi_scplane->SetNameTitle("scifi_scplane", "Muon rate vs Scoring plane at Scifi");
    mufilt_scplane->GetXaxis()->SetTitle("Scoring plane (cm^{2})");
    mufilt_scplane->GetYaxis()->SetTitle("Muon rate Hz/cm2");
    mufilt_scplane->SetNameTitle("mufilt_scplane", "Muon rate vs Scoring plane at MuFilter");
    sndlhc_scplane->GetXaxis()->SetTitle("Scoring plane (cm^{2})");
    sndlhc_scplane->GetYaxis()->SetTitle("Muon rate Hz");
    sndlhc_scplane->SetNameTitle("sndlhc_scplane", "Muon rate vs Scoring plane at SND@LHC");
    scifi_eff_scplane->GetXaxis()->SetTitle("Scoring plane (cm^{2})");
    scifi_eff_scplane->GetYaxis()->SetTitle("Efficiency");
    scifi_eff_scplane->SetNameTitle("scifi_eff_scplane", "Efficiency vs Scoring plane at Scifi");
    mufilt_eff_scplane->GetXaxis()->SetTitle("Scoring plane (cm^{2})");
    mufilt_eff_scplane->GetYaxis()->SetTitle("Efficiency");
    mufilt_eff_scplane->SetNameTitle("mufilt_eff_scplane", "Efficiency vs Scoring plane at MuFilter");

    TEfficiency *eff_xy_scifi = new TEfficiency(*mu_xy_scifi, *mu_xy);
    TH2 *scifi_eff_hist = eff_xy_scifi->CreateHistogram();
    // Antonio's fix for 0/0 & 0/n bins
    for (int ibinx = 1; ibinx <= mu_xy->GetNbinsX();ibinx++){
        for (int ibiny = 1; ibiny <= mu_xy->GetNbinsY(); ibiny++){
            if (eff_xy_scifi->GetTotalHistogram()->GetBinContent(ibinx,ibiny) == 0) scifi_eff_hist->SetBinContent(ibinx,ibiny,-2);
        } 
    }
    scifi_eff_hist->SetMinimum(-0.00001);
    TEfficiency *eff_xy_mufilt = new TEfficiency(*mu_xy_mufilt, *mu_xy);
    TH2 *mufilt_eff_hist = eff_xy_mufilt->CreateHistogram();
    // Antonio's fix for 0/0 & 0/n bins
    for (int ibinx = 1; ibinx <= mu_xy->GetNbinsX();ibinx++){
        for (int ibiny = 1; ibiny <= mu_xy->GetNbinsY(); ibiny++){
            if (eff_xy_mufilt->GetTotalHistogram()->GetBinContent(ibinx,ibiny) == 0) mufilt_eff_hist->SetBinContent(ibinx,ibiny,-2);
        } 
    }
    mufilt_eff_hist->SetMinimum(-0.00001);
    

    TFile *f1=new TFile(savepath+clusID+".muonRatesN_180.root", "RECREATE");
    general_scplane->Write();
    scifi_scplane->Write();
    mufilt_scplane->Write();
    sndlhc_scplane->Write();
    scifi_eff_scplane->Write();
    mufilt_eff_scplane->Write();
    mu_xy_mufilt->Write();
    mu_xy->Write();
    mu_xy_scifi->Write();
    scifi_eff_hist->Write();
    mufilt_eff_hist->Write();
    strange_scifi_mu_p->Write();
    strange_mufilt_mu_p->Write();
    strange_scifi_mu_tx->Write();
    strange_scifi_mu_ty->Write();
    strange_mufilt_mu_tx->Write();
    strange_mufilt_mu_ty->Write();
    mu_theta->Write();
    mu_theta_scifi->Write();
    mu_theta_mufilt->Write();
    mu_xy_energy_scifi->Write();
    mu_xy_theta_scifi->Write();
    mu_xy_energy_mufilt->Write();
    mu_xy_theta_mufilt->Write();
    mu_energy_x_scifi->Write();
    mu_tx_x_scifi->Write();
    mu_ty_x_scifi->Write();
    mu_energy_x_mufilt->Write();
    mu_tx_x_mufilt->Write();
    mu_ty_x_mufilt->Write();
    tx_x_energy_scifi->Write();
    tx_x_energy_mufilt->Write();
	firstcompProcID->Write();
	secondcompProcID->Write();
	thirdcompProcID->Write();
    mu_weight_scifi_in->Write();
    mu_weight_mufilt_in->Write();
    mu_weight_scifi_out->Write();
    mu_weight_mufilt_out->Write();
    f1->Close();
}

void DoChain(int ClusterID){
    TString sims_path = TString("/eos/experiment/sndlhc/MonteCarlo/MuonBackground/muons_up/");
    TString prefix = "sndLHC.Ntuple-TGeant4-Up_run";
    TString filenames[5] = {"N1_20_dig", "N21_40_dig", "N41_60_dig", "N61_80_dig", "N81_99_dig"};
    TString ext = ".root";
    TString savepath = "/afs/cern.ch/work/d/dannc/public/histo_saves/";
    TChain *mainChain = new TChain("cbmsim");
    TString clusID;
    clusID.Form("%d", ClusterID);

    for(const TString& filename: filenames){
        mainChain->Add(sims_path+prefix+filename+ext);}

    muonrate_scoringplane(mainChain, savepath, clusID);


}
