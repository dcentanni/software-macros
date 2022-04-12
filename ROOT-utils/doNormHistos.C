#include "TFile.h"
#include "TTree.h"
#include "TH1.h"

void doNormHistos(){

	TFile *inFile = TFile::Open("hvtx.allbricks.root", "READ");
	
	TH1F *hntrks = (TH1F*) inFile->Get("h_ntrks");
	TH1F *hmaxaperture = (TH1F*) inFile->Get("h_maxaperture");
	TH1F *hIPdau = (TH1F*) inFile->Get("h_IP_dau");
	TH1F *h_prob = (TH1F*) inFile->Get("h_prob");
	TH1F *h_meanIPdau = (TH1F*) inFile->Get("h_meanIPdau");
	TH1F *h_maxIPdau = (TH1F*) inFile->Get("h_maxIPdau");
	TH1F *h_fillfact = (TH1F*) inFile->Get("h_fillfact");
	TH1F *h_meanfillfact = (TH1F*) inFile->Get("h_meanfillfact");
	
	Double_t factor = 1.;
	TH1F *h_ntrks_n = (TH1F*)hntrks->Clone("h_ntrks_n");
	h_ntrks_n->Scale(factor/hntrks->GetEntries());
	
	TH1F *h_maxaperture_n = (TH1F*)hmaxaperture->Clone("h_maxaperture_n");
	h_maxaperture_n->Scale(factor/hmaxaperture->GetEntries());
	
	TH1F *h_IP_dau_n = (TH1F*)hIPdau->Clone("h_IP_dau_n");
	h_IP_dau_n->Scale(factor/hIPdau->GetEntries());
	
	TH1F *h_prob_n = (TH1F*)h_prob->Clone("h_prob_n");
	h_prob_n->Scale(factor/h_prob->GetEntries());
	
	TH1F *h_meanIPdau_n = (TH1F*)h_meanIPdau->Clone("h_meanIPdau_n");
	h_meanIPdau_n->Scale(factor/h_meanIPdau->GetEntries());
	
	TH1F *h_maxIPdau_n = (TH1F*)h_maxIPdau->Clone("h_maxIPdau_n");
	h_maxIPdau_n->Scale(factor/h_maxIPdau->GetEntries());
	
	TH1F *h_fillfact_n = (TH1F*)h_fillfact->Clone("h_fillfact_n");
	h_fillfact_n->Scale(factor/h_fillfact->GetEntries());
	
	TH1F *h_meanfillfact_n = (TH1F*)h_meanfillfact->Clone("h_meanfillfact_n");
	h_meanfillfact_n->Scale(factor/h_meanfillfact->GetEntries());
	
	
	
	TFile *outFile = new TFile("hvtx.allbricks_norm.root", "RECREATE");
	h_ntrks_n->Write();
	h_maxaperture_n->Write();
	h_IP_dau_n->Write();
	h_prob_n->Write();
	h_meanIPdau_n->Write();
	h_maxIPdau_n->Write();
	h_fillfact_n->Write();
	h_meanfillfact_n->Write();
	outFile->Close();
	inFile->Close();	
}

void NormalizeAt(Int_t nfb = 150, Bool_t neutrino){

	TFile *inFile = TFile::Open("hvtx.allbricks.root", "READ");
	TString fbs;
	fbs.Form("%d", nfb);

	TH1F *hntrks = (TH1F*) inFile->Get("h_ntrks");
	TH1F *hmaxaperture = (TH1F*) inFile->Get("h_maxaperture");
	TH1F *hprob = (TH1F*) inFile->Get("h_prob");
	TH1F *hmeanIP = (TH1F*) inFile->Get("h_meanIPdau");
	TH1F *hmaxIP = (TH1F*) inFile->Get("h_maxIPdau");
	TH1F *hfillfact = (TH1F*) inFile->Get("h_fillfact");
	TH1F *hmeanfillfact = (TH1F*) inFile->Get("h_meanfillfact");


	TH1F *h_ntrks_n = (TH1F*)hntrks->Clone("h_ntrks_n");
	TH1F *h_maxaperture_n = (TH1F*)hmaxaperture->Clone("h_maxaperture_n");
	TH1F *h_prob_n = (TH1F*)hprob->Clone("h_prob_n");
	TH1F *h_meanIP_n = (TH1F*)hmeanIP->Clone("h_meanIPdau_n");
	TH1F *h_maxIP_n = (TH1F*)hmaxIP->Clone("h_maxIPdau_n");
	TH1F *h_fillfact_n = (TH1F*)hfillfact->Clone("h_fillfact_n");
	TH1F *h_meanfillfact_n = (TH1F*)hmeanfillfact->Clone("h_meanfillfact_n");

	const Int_t nnuvtx_150fb = 1845; // from SND@LHC TP
	
	Float_t nnuvtx_nfb = nnuvtx_150fb*(nfb/150.);
	Int_t	nbkgvtx_5bricks = hntrks->GetEntries();
	Int_t	nbkgvtx_5walls	= nbkgvtx_5bricks*400.;
	Float_t factor = 0.;
	
	if ( neutrino == true ) factor = nnuvtx_nfb;
	else factor = nbkgvtx_5walls;
	
	h_ntrks_n->Scale(factor/hntrks->GetEntries());
	h_maxaperture_n->Scale(factor/hmaxaperture->GetEntries());
	h_prob_n->Scale(factor/hprob->GetEntries());
	h_meanIP_n->Scale(factor/hmeanIP->GetEntries());
	h_maxIP_n->Scale(factor/hmaxIP->GetEntries());
	h_fillfact_n->Scale(factor/hfillfact->GetEntries());
	h_meanfillfact_n->Scale(factor/hmeanfillfact->GetEntries());
	
	if ( neutrino == true ) TFile *outFile = new TFile("hvtx.allbricks_"+fbs+"fb.root", "RECREATE");
	else TFile *outFile = new TFile("hvtx.allbricks_full.root", "RECREATE");
	h_ntrks_n->Write();
	h_maxaperture_n->Write();
	h_prob_n->Write();
	h_meanIP_n->Write();
	h_maxIP_n->Write();
	h_fillfact_n->Write();
	h_meanfillfact_n->Write();
	outFile->Close();
	inFile->Close();
}
