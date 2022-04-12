#include "TFile.h"
#include "TTree.h"
#include "TRandom.h"

void muonPreTransport(Double_t z_extr, TString inFile, TString outFile){
    
    TFile *inFile_ = TFile::Open(inFile, "READ");
    if (inFile_->IsZombie()) {
    cout << "FLUKA: error while opening file " << inFile << endl;;
    return;
    }
    cout << "FLUKA: Opening input file " << inFile << endl;

    TTree *inTree = (TTree *) inFile_->Get("nt");
    Int_t inNevents = inTree->GetEntries();
    TFile *outFile_ = TFile::Open(outFile, "RECREATE");
    TTree *outTree = inTree->CloneTree(0);
    const Double_t SND_Z_FLUKA = 483.262*100.0; // cm
    const Double_t SND_Z = 326.2; // cm
    Double_t x, y, z, E, px, py, pz;
    inTree->SetBranchAddress("x", &x);
    inTree->SetBranchAddress("y", &y);
    inTree->SetBranchAddress("z", &z);
    inTree->SetBranchAddress("E", &E);
    inTree->SetBranchAddress("px", &px);
    inTree->SetBranchAddress("py", &py);
    inTree->SetBranchAddress("pz", &pz);
    // CONVERTING z_extr TO FLUKA COORDINATE SYSTEM
    Double_t z_FLUKA = z_extr - SND_Z;
    for (int i = 0; i < inNevents; i++){
        inTree->GetEntry(i);
        // projecting to the desired z_extr
        E = E - 27.;
        if (E > 0){
            Double_t lam = ((z_FLUKA+SND_Z_FLUKA)-z)/pz;
            E = E;
            x = x + lam * px;
            y = y + lam * py;
            z = z_FLUKA + SND_Z_FLUKA;
            outTree->Fill();
        }
    }
    outTree->Write();
    outFile_->Close();
    inFile_->Close();
}
void randXY(TString inFile, TString outFile){
    
    TFile *inFile_ = TFile::Open(inFile, "READ");
    TTree *inTree = (TTree *) inFile_->Get("nt");
    gRandom->SetSeed(2);

    TFile *outFile_ = TFile::Open(outFile, "RECREATE");
    TTree *outTree = inTree->CloneTree(0);

    Double_t x;
    Double_t y;
    inTree->SetBranchAddress("x", &x);
    inTree->SetBranchAddress("y", &y);

    for (int i = 0; i < inTree->GetEntries(); i++)
    {
        inTree->GetEntry(i);
	// Trying to set to brick1
        x = gRandom->Uniform(-18.300000, -17.500000);
        y = gRandom->Uniform(24.250000, 25.250000);
        outTree->Fill();
    }

    outTree->Write();
    outFile_->Close();
    inFile_->Close();
}

void DoNewFLUKA(TString inFile, Double_t z_ext){
    TString ext = ".root";
    if(inFile.EndsWith(".root")) cout << "Give me it without extension" <<endl; return;
    TString z_string;
    z_string.Form("%f", z_ext);
    muonPreTransport(z_ext, inFile+ext, inFile+"_z"+z_string+ext);
    randXY(inFile+"_z"+z_string+ext, inFile+"_z"+z_string+"_WallB1"+ext);
    cout << "Make new FLUKA complete" << endl;
}
