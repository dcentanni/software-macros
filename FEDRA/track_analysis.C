EdbDataProc  *dproc=0;
EdbPVRec     *gAli=0;
#include <stdlib.h>


void set_segments_dz(float dz)
{
  int np = gAli->Npatterns();
  for(int i=0; i<np; i++) {
    EdbPattern *p = gAli->GetPattern(i);
    int ns = p->N();
    for(int j=0; j<ns; j++) p->GetSegment(j)->SetDZ(dz);
  }
}

void init( const char *def, int iopt,  const char *rcut)
{
  if(!def)  dproc = new EdbDataProc();
  else      dproc = new EdbDataProc(def);

  dproc->InitVolume(iopt, rcut);  
  gAli = dproc->PVR();
  set_segments_dz(300.);
}

int FindMostCommonPdgSeg(EdbTrackP *track)
{
  map <int, int> nseg_pdg;
  int mostcommmonpdg = -1;
  int maxnsegments = -1;
  //looping over track segments, counting them
  for (int iseg = 0; iseg < track->N(); iseg++){

    EdbSegP * myseg = track->GetSegment(iseg);
    nseg_pdg[myseg->Vid(0)]++; 
  }
  //which Particle PDG has the most segments?

  for (auto && [pdgcode,nsegments]:nseg_pdg){
    //find maxnsegments
    if (nsegments > maxnsegments){
      maxnsegments = nsegments;
      mostcommmonpdg = pdgcode;
    } //end if condition

  } //end loop on map
  return mostcommmonpdg;
}

int FindMostCommonEvent(EdbTrackP *track)
{
  map <int, int> nseg_MCEvt;
  int mostcommonevent = -1;
  int maxnsegments = -1;
  //looping over track segments, counting them
  for (int iseg = 0; iseg < track->N(); iseg++){

    EdbSegP * myseg = track->GetSegment(iseg);
    nseg_MCEvt[myseg->MCEvt()]++; 
  }
  //which MCEvent has the most segments?

  for (auto && [MCEvent,nsegments]:nseg_MCEvt){
    //find maxnsegments
    if (nsegments > maxnsegments){
      maxnsegments = nsegments;
      mostcommonevent = MCEvent;
    } //end if condition

  } //end loop on map
  return mostcommonevent;
}
int FindMostCommonMCTrack(EdbTrackP *track)
{
  map <int, int> nseg_MCTrack;
  int mostcommonmctrack = -1;
  int maxnsegments = -1;
  //looping over track segments, counting them
  for (int iseg = 0; iseg < track->N(); iseg++){

    EdbSegP * myseg = track->GetSegment(iseg);
    nseg_MCTrack[myseg->MCTrack()]++; 
  }
  //which MCEvent has the most segments?

  for (auto && [MCTrack,nsegments]:nseg_MCTrack){
    //find maxnsegments
    if (nsegments > maxnsegments){
      maxnsegments = nsegments;
      mostcommonmctrack = MCTrack;
    } //end if condition

  } //end loop on map
  return mostcommonmctrack;
}

bool CheckDiffMCEvt(EdbTrackP *track)
{
	Int_t track_MCEvt = FindMostCommonEvent(track);
	bool flag = false;
	for (int iseg = 0; iseg < track-> N(); iseg++){
		EdbSegP *myseg = track->GetSegment(iseg);	
		if (track_MCEvt != myseg->MCEvt()) flag = true;
	}
	return flag;
}

void track_analysis(TString simFile)
{
    init(0, 100 ,"1");     
    gAli->FillCell(30,30,0.009,0.009);

    TObjArray *mytracks = gAli->eTracks;
	TH1F *htrk_purity = new TH1F("htrk_purity", "Track purity distribution", 100, 0, 1);
	TH1I *hnpl = new TH1I("hnpl", "N. of plates crossed by muon reconstructed track", 61, -0.5, 60.5);
	TH1I *hnseg = new TH1I("hnseg", "N. of segments of reconstructed tracks", 61, -0.5, 60.5);
	TH1I *hnseg_mu = new TH1I("hnseg_mu", "N. of segments of muon reconstructed track", 61, -0.5, 60.5);
	
	int ntracks = mytracks->GetEntries();
	cout.precision(10);

    cout<<"I have " << ntracks << " tracks !"<<endl;

	bool diff_mcflag = false;
	EdbTrackP *track = NULL;
	int dirty_tracks = 0;
	float sample_purity;
	float trk_purity;
	int diffMC = 0;

	/**** MUON TRACK PURITY ****/
	
	for (int itrack = 0; itrack < ntracks; itrack++){
		
		Int_t Vid_mem = -100000;
		track = (EdbTrackP *) mytracks->At(itrack);
		int trackpdg = FindMostCommonPdgSeg(track);
		// getting all tracks' nsegments
		hnseg->Fill(track->N());
		if (CheckDiffMCEvt(track) == true) {diff_mcflag = true;diffMC++;}//cout << "----Warning: there are tracks with different MCEvt!---- | trid: " << itrack <<endl;}
		// considering muon tracks only
		if (trackpdg != 13) continue;
		// getting all muon-tracks' segments
		hnseg_mu->Fill(track->N());
		bool flag = false;
		int ext_seg = 0;
		for (int iseg = 0; iseg < track->N(); iseg++){
			EdbSegP * myseg = track->GetSegment(iseg);
			if (myseg->Vid(0) != trackpdg) {flag = true; ext_seg++;}// cout << "flag true	itrack: " << itrack << " iseg: " << iseg << " ext_seg " << ext_seg << endl;}
												
		} // end loop on iseg

		if (flag == true) {dirty_tracks++;}// cout << "Dirty track no. " << itrack << " n. ext_seg: " << ext_seg << endl;}
		if (ext_seg != 0) {trk_purity = 1. - (float)ext_seg/(float)track->N(); htrk_purity->Fill(trk_purity);}
		hnpl->Fill(track->Npl());

	}// end loop on itrack
	
	if(diff_mcflag == true) cout << "----Warning: there are tracks with different MCEvt!----" << endl;
	sample_purity = 1. - (float)dirty_tracks/(float)ntracks;
	cout << "-----Sample purity: " << sample_purity << "-----" << endl;
	float MCmismatch = (float)diffMC/(float)ntracks;
	cout << "-----MCEvt mismatch %: " << MCmismatch << "-----" << endl;
	 
	
	
	TCanvas *c1 = new TCanvas();
	htrk_purity->Draw();
	TCanvas *c2 = new TCanvas();
	hnpl->Draw();
	TCanvas *c3 = new TCanvas();
	hnseg->Draw();
	TCanvas *c4 = new TCanvas();
	hnseg_mu->Draw();
	TFile *outFile = new TFile("histosb000011_tracksavedefparms.root", "RECREATE");
	htrk_purity->Write();
	hnpl->Write();
	hnseg->Write();
	hnseg_mu->Write();
	
	track = NULL;
	
	/**** MUON SPLITTING ANALYSIS ****/
	TFile *_simFile = new TFile(simFile);
	if(!_simFile) return;
	TTreeReader reader("cbmsim", _simFile);
	int MCEvts = reader.GetEntries(true);
	_simFile->Close();
	_simFile = NULL;
	
	float RecoMuons = ((float) hnpl->GetEntries()-(float) MCEvts)/MCEvts;
	cout << "-----Reco Muons %: +" << RecoMuons << "-----" << endl;
	
	
	//TH1D *hmu_tracks = new TH1D("hmu_tracks", "N. of mu tracks per simulated muon", 11, -0.5, 10.5);
	/*for(int iMC = 0; iMC < MCEvts; iMC++){
	    if(iMC%1000==0) cout<<"Arrivato all'evento "<<iMC<<endl;
		int mu_track = 0;
		for(int itrack = 0; itrack < ntracks; itrack ++){
			track = (EdbTrackP *) mytracks->At(itrack);				// TROPPO MACCHINOSO, DA CAMBIARE
			int trackMCEvt = FindMostCommonEvent(track);
			int trackMCTrackID = FindMostCommonMCTrack(track);
			if (trackMCEvt == iMC && trackMCTrackID == 0) mu_track++;
		}
		hmu_tracks->Fill(mu_track);
	}
	//TCanvas *c2 = new TCanvas();
	//hmu_tracks->Draw();*/
	

//int status = system("python -i ~/macros-snd/trackingquality.py ../");
}// end track_analysis







