#include <cstdlib>
#include <iostream>
#include <iomanip>
#include <map>
#include <string>
#include <utility>
#include <string>
#include "TH1.h"
#include "TCanvas.h"
#include "TVector.h"
#include "TVector3.h"
#include "TLegend.h"
#include "TFile.h"
#include "TString.h"
#include "TObjString.h"
#include "TSystem.h"
#include "TROOT.h"
#include "/home/simsndlhc/macros-snd/FEDRA/trackutils.h"
namespace VERTEX_PAR
{
  float DZmax = 3000.;
  //float ProbMinV   = 0.0001;  // minimum acceptable probability for chi2-distance between tracks
  float ProbMinV   = 0.01;
  float ImpMax     = 15.;    // maximal acceptable impact parameter [microns] (for preliminary check)
  bool  UseMom     = false;  // use or not track momentum for vertex calculations
  bool  UseSegPar  = true;  // use only the nearest measured segments for vertex fit (as Neuchatel)
  int   QualityMode= 0;      // vertex quality estimation method (0:=Prob/(sigVX^2+sigVY^2); 1:= inverse average track-vertex distance)
}

void vtx_analysis(int bID, bool nu = false, bool drawopt = false){
	gEDBDEBUGLEVEL=0;
    TString inputfile_vtxname = "vertextree.root";
  	using namespace VERTEX_PAR;   
    TFile *inputfile_vtx = TFile::Open(inputfile_vtxname,"READ");
    if (inputfile_vtx == NULL) cout<<"ERROR: inputfile_vtx not found"<<endl;
	TTree *vtxtree = (TTree*) inputfile_vtx->Get("vtx");
	if( nu == true) cout << "++++Running analysis for neutrino vertices++++" << endl;
	else cout << "++++Running analysis for bkg vertices++++" << endl;
 	EdbVertexRec *vertexrec;
 	EdbDataProc *dproc = new EdbDataProc();
	EdbPVRec *ali = new EdbPVRec();
 	EdbScanCond *scancond = new EdbScanCond();
	ali->SetScanCond(scancond);
	
	TString brID;
	brID.Form("%d", bID);
	TString brickID = "b0000"+brID;
    const int maxtracks = 100;
    
    Int_t MCMotherID[maxtracks]={-99};
    TBranch *b_MCMotherID;
    vtxtree->SetBranchAddress("MCMotherID", MCMotherID, &b_MCMotherID);
    Int_t tID[maxtracks]={-99};
    TBranch *b_tID;
    vtxtree->SetBranchAddress("t.eID", tID, &b_tID);
	
	TH1F *h_ntrks = new TH1F("h_ntrks","ntrks; ntrks; events",19,1.5,20.5);
	TH1F *h_maxaperture = new TH1F("h_maxaperture","max aperture; maperture; events",100,0,1);
	TH1F *h_frac = new TH1F("h_frac","frac; frac; events",10,0.15,1.15);
	TH1F *h_frac2 = new TH1F("h_frac2","frac (2nd version); frac; events",10,0.15,1.15);
	TH1F *h_quality = new TH1F("h_quality","Quality; eQuality; events",100,0,0.1);
	TH1F *h_prob = new TH1F("h_prob", "Vtx probability;prob;events", 100, 0, 1);
	
	TH1F *h_IP_dau = new TH1F("h_IP_dau","Impact Parameter Dau; Impact Parameter; tracks",150/5,0,150);
	TH1F *h_meanIPdau = new TH1F("h_meanIPdau", "Mean IP of vtx ass. tracks;meanIP;events", 150/5, 0, 150);
	TH1F *h_maxIPdau = new TH1F("h_maxIPdau", "Max IP of vtx ass. tracks;maxIP;events", 150/5, 0, 150);
	
	TH1F *h_fillfact = new TH1F("h_fillfact", "Fill factor of vtx ass. tracks;fill fact;events", 100, -0.01, 1.01);
	TH1F *h_meanfillfact = new TH1F("h_meanfillfact", "Mean fill factor of vtx ass. tracks;mean fill fact;events", 100, -0.01, 1.01);
	
	TH1F *h_nonprimary = new TH1F("h_nonprimary","non primary / ntrks; ; events",20,0,1);
	
	TH1F *hmcevtID = new TH1F("hmcevtID", "Mostfrequent MCEvtID in vertices", 1501, -0.5, 1500.5);
	
	int b_0 = 0;
	int b_f = 0;
	int s_0 = 0;
	int s_f = 0;
	
	const int nvertices = vtxtree->GetEntries();
	cout<<"Reading number of vertices: "<<nvertices<<endl;
	
	const int maxvID = 100000;
	int ntracks_event[maxvID] = {0}; //arrays to be filled with vID
    int mostfrequentevent[maxvID] = {0};
	// SET OUTTREE VARIABLES
	TFile *treeFile = NULL;
	Int_t signal;
	Int_t ntrks;
	Int_t vID = 0;
	Float_t prob;
	Float_t maxaperture;
	Float_t meanIP;
	Float_t maxIP;
	Float_t fillfact;
	Float_t meanfillfact;
	Int_t 	flag;
	
	// SET OUTPUT FILE/TREE
	if (nu == true) treeFile = new TFile(brickID+".OUTvar_sig.root","RECREATE");
	else treeFile = new TFile(brickID+".OUTvar_bkg.root","RECREATE");
	TTree *tree = new TTree("vtx", "Tree containing SIG / BKG vertices informations");
	tree->Branch("vID", &vID, "vID/I");
	tree->Branch("ntrks", &ntrks, "ntrks/I");
	tree->Branch("signal", &signal, "signal/I");
	tree->Branch("brickID", &bID, "brickID/I");
	tree->Branch("prob", &prob, "prob/F");
	tree->Branch("maxaperture", &maxaperture, "maxaperture/F");
	tree->Branch("meanIP", &meanIP, "meanIP/F");
	tree->Branch("maxIP", &maxIP, "maxIP/F");
	tree->Branch("fillfact", &fillfact, "fillfact/F");
	tree->Branch("meanfillfact", &meanfillfact, "meanfillfact/F");
	tree->Branch("flag", &flag, "flag/I");
	
	
	map<int,EdbTrackP*>trackIDmap; //to associate tracks to vertices, needs to be studied further
	vertexrec = new EdbVertexRec();
    vertexrec->SetPVRec(ali);
 	vertexrec->eDZmax=DZmax;
 	vertexrec->eProbMin=ProbMinV;
 	vertexrec->eImpMax=ImpMax;
 	vertexrec->eUseMom=UseMom;
 	vertexrec->eUseSegPar=UseSegPar;
 	vertexrec->eQualityMode=QualityMode;
	
	map<int,int> frequencyEvent;
    map<int,int>::iterator it;  
	
	EdbVertex *vertex = 0;
	//first loop, filling the array
	dproc->ReadVertexTree(*vertexrec, "vertextree.root", "1",trackIDmap);
	TObjArray *vtxarr = (TObjArray*) ali->eVTX;
	//second loop, actually using the vertices
   	for (int i = 0; i < nvertices; i++){
     	frequencyEvent.clear();
   	
   		vID = i;		
        ntracks_event[vID] = 0;
        mostfrequentevent[vID] = -1;
        
        if (i% 1000 == 0) cout << "Reading vtx no. " << vID << endl;
   		vertex = (EdbVertex*) vtxarr->At(vID);
   		//cout << "Reading vtx no. " << vID << endl;
   		//vertex = dproc->GetVertexFromTree(*vertexrec,inputfile_vtxname,vID);   		
   		
   		vtxtree->GetEntry(vID);
   		if(vertex->Flag() == 2 || vertex->Flag() == 5) continue; // excluding impossible vertex topologies (back neutral)
   		
		Float_t IP_dau;
		Float_t maxIP_dau;
		const Int_t NPLATES = 60;
   		bool nu_vtx = false;
   		int ntracks = 0;
   		int nonprimary = 0;
		/******* Vertex purity check **************************************************/  		
   		for (int itrk = 0; itrk < vertex->N(); itrk++){
                EdbTrackP *track = vertex->GetTrack(itrk);
                int eventtrack=-99;
                if(vertex->GetVTa(itrk)->Zpos()==1){ // track-start attached to vertex (1st seg)
                    eventtrack = track->GetSegmentFirst()->MCEvt();
                }
                else eventtrack = track->GetSegmentLast()->MCEvt(); //track-end attached to vertex (last seg)
                frequencyEvent[eventtrack]++;      
		}
        for (it = frequencyEvent.begin(); it!=frequencyEvent.end();it++){
			//cout << "\t\t" << it->first << "\t" << it->second << endl;
            if(it->second > ntracks_event[vID]){
            	ntracks_event[vID] = it->second;
                mostfrequentevent[vID] = it->first;
            }
		}
        float frac = (float)ntracks_event[vID]/(float)vertex->N();
		h_frac->Fill(frac);
		// or as alternative, no matter what Zpos, taking as MCEvt the most frequent one occurring in a track (to be checked if valid)
		ntracks_event[vID] = 0;
        mostfrequentevent[vID] = -1;
		for (int itrk = 0; itrk < vertex->N(); itrk++){
                EdbTrackP *track = vertex->GetTrack(itrk);
                int eventtrack=-99;
                eventtrack = FindMostCommonEvent(track);
                frequencyEvent[eventtrack]++;
		}
        for (it = frequencyEvent.begin(); it!=frequencyEvent.end();it++){
            if(it->second > ntracks_event[vID]){
            	ntracks_event[vID] = it->second;
                mostfrequentevent[vID] = it->first;
            }
		}
        float frac2 = (float)ntracks_event[vID]/(float)vertex->N();
		h_frac2->Fill(frac2);
		/*****************************************************************************/
			IP_dau = 0.;
			maxIP_dau = -1;
	Int_t 	totsegs = 0;
   	Int_t 	totremplates = 0;
   	Float_t sumfillfact = 0.;
   	bool b0selected = false;
   		
	if	(nu == false){	
		for (int itrk = 0; itrk < vertex->N(); itrk++){
			EdbTrackP *track = vertex->GetTrack(itrk);
			if(vertex->GetVTa(itrk)->Zpos()==1){
				ntracks++;
				h_IP_dau->Fill(vertex->GetVTa(itrk)->Imp());
				IP_dau = IP_dau + vertex->GetVTa(itrk)->Imp();
				if(vertex->GetVTa(itrk)->Imp() > maxIP_dau){
					maxIP_dau = vertex->GetVTa(itrk)->Imp();	
				}
				Float_t remplates = NPLATES-track->GetSegmentFirst()->Plate()+1.;
   				totsegs = totsegs + track->N();
   				totremplates = totremplates + remplates;
   				sumfillfact = sumfillfact + (float)track->N()/(float)(NPLATES-track->GetSegmentFirst()->Plate()+1.);
			}// closes if on Zpos
		}// closes for
		h_fillfact->Fill((float)totsegs / (float)totremplates);
   		h_meanfillfact->Fill(sumfillfact/ntracks);
   		
   		fillfact = (float)totsegs / (float)totremplates;
   		meanfillfact = sumfillfact/ntracks;
	} // closes nu false
	
	if	(nu == true){
		for (int itrk = 0; itrk < vertex->N(); itrk++){
			EdbTrackP *track = vertex->GetTrack(itrk);
            if(MCMotherID[itrk] == 0 && vertex->GetVTa(itrk)->Zpos()==1){
            	ntracks++;
				h_IP_dau->Fill(vertex->GetVTa(itrk)->Imp());
				IP_dau = IP_dau + vertex->GetVTa(itrk)->Imp();
				if(vertex->GetVTa(itrk)->Imp() > maxIP_dau){
					maxIP_dau = vertex->GetVTa(itrk)->Imp();	
				}
				nu_vtx = true;	
            }
            else nonprimary++;
		} // closes loop on tracks
		
		//cout << "ntracks motherID=0 "<< ntracks << endl;
		if(ntracks > 1) {h_ntrks->Fill(ntracks); ntrks = ntracks;}
		if(nonprimary !=0 && ntracks >1) h_nonprimary->Fill((float)nonprimary/vertex->N());
    
    	if(nu_vtx == true && ntracks > 1){
    		s_0++;
    		h_prob->Fill(vertex->V()->prob());
    		if(vertex->V()->prob() > 0.95) s_f++;
    		hmcevtID->Fill(mostfrequentevent[vID]);
    		//cout << "MCEvtID " << mostfrequentevent[vID] << endl;
    		//cout << "vID " << vID << " ntracks " << ntracks  << " nonprimary " << nonprimary << endl;
   			h_maxaperture->Fill(vertex->MaxAperture());
   			//if(vertex->MaxAperture() > 0.2) cout << "MaxAperture Greater than 0.2, vID " << vID << endl;
   			h_quality->Fill(vertex->Quality());
   			h_meanIPdau->Fill(IP_dau/ntracks);
   			h_maxIPdau->Fill(maxIP_dau);

   			
   			
   			for (int itrk = 0; itrk < vertex->N(); itrk++){
   				EdbTrackP *track = vertex->GetTrack(itrk);
   				if(MCMotherID[itrk] == 0 && vertex->GetVTa(itrk)->Zpos()==1){
   					Float_t remplates = NPLATES-track->GetSegmentFirst()->Plate()+1.;
   					totsegs = totsegs + track->N();
   					totremplates = totremplates+ remplates;
   					sumfillfact = sumfillfact + (float)track->N()/(float)(NPLATES-track->GetSegmentFirst()->Plate()+1.);
   					//cout << "vID " << vID << " nseg " << track->N() << " Plate 1st seg " << track->GetSegmentFirst()->Plate() << " Fill fact " << (float)track->N()/(float)(NPLATES-track->GetSegmentFirst()->Plate()+1.) << " eID " << tID[itrk] << endl;
   				}
   			}//closes new for
   			h_fillfact->Fill((float)totsegs / (float)totremplates);
   			h_meanfillfact->Fill(sumfillfact/ntracks);
   			
   			// Tree fill
   			meanIP = IP_dau/ntracks;
   			maxIP = maxIP_dau;
   			prob = vertex->V()->prob();
   			maxaperture = vertex->MaxAperture();
   			fillfact = (float)totsegs / (float)totremplates;
   			meanfillfact = sumfillfact/ntracks;
   			flag = vertex->Flag();
   			signal = 1;
   			tree->Fill();
    	}   
    } // closes if on nu == true
    if	(nu == false){	
    					b_0++;
    					h_ntrks->Fill(vertex->N());
 						h_maxaperture->Fill(vertex->MaxAperture());
 						h_quality->Fill(vertex->Quality()); 							
   						h_prob->Fill(vertex->V()->prob());
   						if(vertex->V()->prob() > 0.95) b_f++;
   						h_meanIPdau->Fill(IP_dau/vertex->N());
   						h_maxIPdau->Fill(maxIP_dau);
   						
   						// Tree fill
   						meanIP = IP_dau/vertex->N();
   						maxIP = maxIP_dau;
   						prob = vertex->V()->prob();
   						maxaperture = vertex->MaxAperture();
   						ntrks = vertex->N();
   						flag = vertex->Flag();
   						signal = 0;
   						tree->Fill();
   	} // closes if on nu == false
    
    
     
        
	}//closes loop on vertices
	
	/*if (nu == false){
		cout << "B0 " << b_0 << endl;
		cout << "Bf " << b_f << " cut on prob > 0.95"<< endl;
		cout << "local rejection = " << (float) b_0 / (float) b_f << endl;
	}
	if (nu == true){
		cout << "S0 " << s_0 << endl;
		cout << "Sf " << s_f << " cut on prob > 0.95"<< endl;
		cout << "local efficiency = " << (float) s_f / (float) s_0 << endl;
	}*/
	// Tree write
	treeFile->cd();
	tree->Write();
	treeFile->Close();
	
	Double_t factor = 1.;
	TH1F *h_ntrks_n = (TH1F*)h_ntrks->Clone("h_ntrks_n");
	h_ntrks_n->Scale(factor/h_ntrks->GetEntries());
	
	TH1F *h_maxaperture_n = (TH1F*)h_maxaperture->Clone("h_maxaperture_n");
	h_maxaperture_n->Scale(factor/h_maxaperture->GetEntries());
	
	TH1F *h_IP_dau_n = (TH1F*)h_IP_dau->Clone("h_IP_dau_n");
	h_IP_dau_n->Scale(factor/h_IP_dau->GetEntries());
			

	// Style

	h_ntrks->SetLineWidth(2);
	h_ntrks->SetLineColor(kRed);
	h_ntrks->SetFillStyle(3005);
	h_ntrks->SetFillColor(kRed);
	
	hmcevtID->SetLineWidth(2);
	hmcevtID->SetLineColor(kRed);
	hmcevtID->SetFillStyle(3005);
	hmcevtID->SetFillColor(kRed);

	h_maxaperture->SetLineWidth(2);
	h_maxaperture->SetLineColor(kRed);
	h_maxaperture->SetFillStyle(3005);
	h_maxaperture->SetFillColor(kRed);
	
	h_frac->SetLineWidth(2);
	h_frac->SetLineColor(kRed);
	h_frac->SetFillStyle(3005);
	h_frac->SetFillColor(kRed);
	
	
	h_frac2->SetLineWidth(2);
	h_frac2->SetLineColor(kRed);
	h_frac2->SetFillStyle(3005);
	h_frac2->SetFillColor(kRed);
	
	h_IP_dau->SetLineWidth(2);
	h_IP_dau->SetLineColor(kRed);
	h_IP_dau->SetFillStyle(3005);
	h_IP_dau->SetFillColor(kRed);
	
	h_quality->SetLineWidth(2);
	h_quality->SetLineColor(kRed);
	h_quality->SetFillStyle(3005);
	h_quality->SetFillColor(kRed);
	
	h_ntrks_n->SetLineWidth(2);
	h_ntrks_n->SetLineColor(kRed);
	h_ntrks_n->SetFillStyle(3005);
	h_ntrks_n->SetFillColor(kRed);
	h_ntrks_n->SetNameTitle("h_ntrks_n","ntrks normalized");
	
	h_maxaperture_n->SetLineWidth(2);
	h_maxaperture_n->SetLineColor(kRed);
	h_maxaperture_n->SetFillStyle(3005);
	h_maxaperture_n->SetFillColor(kRed);
	h_maxaperture_n->SetNameTitle("h_maxaperture_n","max aperture normalized");
	
	h_IP_dau_n->SetLineWidth(2);
	h_IP_dau_n->SetLineColor(kRed);
	h_IP_dau_n->SetFillStyle(3005);
	h_IP_dau_n->SetFillColor(kRed);
	h_IP_dau_n->SetNameTitle("h_IP_dau_n", "Impact Parameter Dau normalized");
	
	h_nonprimary->SetLineWidth(2);
	h_nonprimary->SetLineColor(kRed);
	h_nonprimary->SetFillStyle(3005);
	h_nonprimary->SetFillColor(kRed);
	
	h_prob->SetLineWidth(2);
	h_prob->SetLineColor(kRed);
	h_prob->SetFillStyle(3005);
	h_prob->SetFillColor(kRed);
	
	h_meanIPdau->SetLineWidth(2);
	h_meanIPdau->SetLineColor(kRed);
	h_meanIPdau->SetFillStyle(3005);
	h_meanIPdau->SetFillColor(kRed);
	
	h_maxIPdau->SetLineWidth(2);
	h_maxIPdau->SetLineColor(kRed);
	h_maxIPdau->SetFillStyle(3005);
	h_maxIPdau->SetFillColor(kRed);
	
	h_fillfact->SetLineWidth(2);
	h_fillfact->SetLineColor(kRed);
	h_fillfact->SetFillStyle(3005);
	h_fillfact->SetFillColor(kRed);
	
	h_meanfillfact->SetLineWidth(2);
	h_meanfillfact->SetLineColor(kRed);
	h_meanfillfact->SetFillStyle(3005);
	h_meanfillfact->SetFillColor(kRed);
	
	//Drawing
	if(drawopt == true){
	TCanvas *c_htrk = new TCanvas("c_htrk", "c_htrk", 600,500);
	c_htrk->SetGrid();
	h_ntrks->Draw();
	TCanvas *c_hmcevt = new TCanvas("c_hmcevt", "c_hmcevt", 600,500);
	c_hmcevt->SetGrid();
	hmcevtID->Draw();
	TCanvas *c_hmaperture = new TCanvas("c_hmaperture", "c_hmaperture", 600,500);
	c_hmaperture->SetGrid();
	h_maxaperture->Draw();
	TCanvas *c_hfrac = new TCanvas("c_hfrac", "c_hfrac", 600,500);
	c_hfrac->SetGrid();
	h_frac->Draw();
	TCanvas *c_hfrac2 = new TCanvas("c_hfrac2", "c_hfrac2", 600,500);
	c_hfrac2->SetGrid();
	h_frac2->Draw();
	TCanvas *c_hIPdau = new TCanvas("c_hIPdau", "c_hIPdau", 600,500);
	c_hIPdau->SetGrid();
	h_IP_dau->Draw();
	TCanvas *c_hquality = new TCanvas("c_hquality", "c_hquality", 600,500);
	c_hquality->SetGrid();
	h_quality->Draw();
	TCanvas *c_htrk_n = new TCanvas("c_htrk_n", "c_htrk_n", 600,500);
	c_htrk_n->SetGrid();
	h_ntrks_n->Draw("HIST");
	TCanvas *c_hmaperture_n = new TCanvas("c_hmaperture_n", "c_hmaperture_n", 600,500);
	c_hmaperture_n->SetGrid();
	h_maxaperture_n->Draw("HIST");
	TCanvas *c_hIPdau_n = new TCanvas("c_hIPdau_n", "c_hIPdau_n", 600,500);
	c_hIPdau_n->SetGrid();
	h_IP_dau_n->Draw("HIST");
	if(nu == true){
	TCanvas *c_hnonprimary = new TCanvas("c_hnonprimary", "c_hnonprimary", 600,500);
	c_hnonprimary->SetGrid();
	h_nonprimary->Draw();
	}
	TCanvas *c_hprob = new TCanvas("c_hprob", "c_hprob", 600,500);
	c_hprob->SetGrid();
	h_prob->Draw();
	TCanvas *c_hmeanIP = new TCanvas("c_hmeanIP", "c_hmeanIP", 600,500);
	c_hmeanIP->SetGrid();
	h_meanIPdau->Draw();
	TCanvas *c_hmaxIP = new TCanvas("c_hmaxIP", "c_hmaxIP", 600,500);
	c_hmaxIP->SetGrid();
	h_maxIPdau->Draw();
	TCanvas *c_hfill = new TCanvas("c_hfill", "c_hfill", 600,500);
	c_hfill->SetGrid();
	h_fillfact->Draw();
	TCanvas *c_hmeanfill = new TCanvas("c_hmeanfill", "v", 600,500);
	c_hmeanfill->SetGrid();
	h_meanfillfact->Draw();
	}//closes drawopt
	
	
	//Saving
	TFile *outFile = new TFile("hvtx."+brickID+".root", "RECREATE");
	h_ntrks->Write();
	h_maxaperture->Write();
	h_frac->Write();
	h_frac2->Write();
	h_IP_dau->Write();
	h_ntrks_n->Write();
	h_maxaperture_n->Write();
	h_IP_dau_n->Write();
	h_prob->Write();
	h_meanIPdau->Write();
	h_maxIPdau->Write();
	h_fillfact->Write();
	h_meanfillfact->Write();
	if(nu == true) {h_nonprimary->Write(); hmcevtID->Write();}
	outFile->Close();
	
	inputfile_vtx->cd();
	inputfile_vtx->Close();
	
}
