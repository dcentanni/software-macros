#include "histocanvas.h"
#include "TInterpreter.h"
#include "TTreeReader.h"
#include "TH1.h"
#include "TH2.h"
using namespace ROOT;

void mudensity(TString inFile, TString savepath, TString clusID, TString outfile){
    TFile *file = new TFile(inFile);
    if(!file) return;
    TTreeReader reader("cbmsim", file);

    TTreeReaderArray <ShipMCTrack>  tracks(reader, "MCTrack");
    TTreeReaderArray <EmulsionDetPoint>   emulsionpoints(reader, "EmulsionDetPoint");

    int nevents = reader.GetEntries(true);
    cout<<"Number of events: "<<nevents<<endl;
    cout.precision(10);

    TH2D *xy_density = new TH2D("xy_density", "XY distribution of muon hits in 1st plate of Wall1 Brick1", 30, -40, -10, 30, 10, 40);
    
        while (reader.Next()){

        int ientry = reader.GetCurrentEntry();
            for(EmulsionDetPoint& emulsionpoint: emulsionpoints){
                if (emulsionpoint.GetTrackID()==0 && emulsionpoint.GetDetectorID()==11001){
                    Double32_t x_mu = emulsionpoint.GetX();
                    Double32_t y_mu = emulsionpoint.GetY();
                    xy_density->Fill(x_mu, y_mu);
                }
            }

        }
    TFile *f1=new TFile(outfile, "RECREATE");
    xy_density->Write();
    cout << "Results stored in " << outfile << endl;
    f1->Close();
}
void DoDensity(int ClusterID){
    TString sims_path = TString("/eos/user/d/dannc/MuonBack_sim/");
    //TString sim_date = TString("03022022/");
    TString sim_date = TString("07022022/");
    TString filenames[2] = {"sndLHC.Ntuple-TGeant4-1E2cm2.root", "sndLHC.Ntuple-TGeant4-1E3cm2.root"};// "sndLHC.Ntuple-TGeant4-1E4cm2.root"};
    TString densities[2] = {"1E2", "1E3"};// "1E4"};
    TString savepath = "/afs/cern.ch/work/d/dannc/public/histo_saves/";
    TString clusID;
    clusID.Form("%d", ClusterID);

    for(int i = 0; i < 2; i++){
        mudensity(sims_path+sim_date+filenames[i], savepath, clusID, savepath+"mudensity"+densities[i]+".root");
    }
}
