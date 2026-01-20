int create_couplecells(int cell){

  const int nplates = 57;
  int brickID = 21;
  float xmin=200000;
  float ymin=4500;
  float cellsize=10000;
  int i = (cell % 18);
  int j = (cell / 18);
  float xpos = xmin + (i * cellsize) + cellsize/2;
  float ypos = ymin + (j * cellsize) + cellsize/2;
  int xcell=(i + 1)*10;
  int ycell=(j + 1)*10;

  TString cutstring = Form("eCHI2P<2.4&&eN1<=1&&eN2<=1&&s.Theta()<10.1&&abs(s.eX-%f)<6000&&abs(s.eY-%f)<6000", xpos, ypos);
  TCut *cut = new TCut(cutstring);
  printf("Using cut: %s\n", cut->GetTitle());
  TString mupath = Form("/eos/experiment/sndlhc/MonteCarlo/FEDRA/muon_Euniform_RUN1/cells/b0000%i", brickID);
  TString newpath = Form("/eos/experiment/sndlhc/users/dancc/FEDRA/muon_Euniform_RUN1/cell_reco/cell_%i_%i/b0000%i", xcell, ycell, brickID);
  //TString newpath = "./muon";
  
  for (int i = 1; i <= 57; i++) {
    EdbCouplesTree *ect = new EdbCouplesTree();
    EdbCouplesTree *ect_mu = new EdbCouplesTree();
    TString cpname = Form("/p%03i/%i.%i.0.0.cp.root", i, brickID, i);
    ect->InitCouplesTree("couples", newpath+cpname, "RECREATE");
    ect_mu->InitCouplesTree("couples", mupath+cpname, "READ");
    
    if (!(ect_mu->eTree)){
      cout << "File not existing" << endl;
      return -1;
    }
    ect_mu->eCut = *cut;
    TEventList *cutlist = ect_mu->InitCutList();
    if (!cutlist){ 
      cout << "We have no entries" << endl;
      return -1;
    }
    
    // adding neutrino couples
    int nsegcut = cutlist->GetN();
    cut->Print();
    cout << "We have "<< nsegcut<< " good couples in plate "<< i << endl;
    int ihit = 0;
    for (int ientry=0; ientry < nsegcut; ientry++){
      int iseg = cutlist->GetEntry(ientry);
      ect_mu->GetEntry(iseg);
      EdbSegP *seg = ect_mu->eS;
      ect->eS->Set(ihit,seg->X(),seg->Y(),seg->TX(),seg->TY(),1,1);
      ect->eS->SetMC(seg->MCEvt(), seg->MCTrack());
      ect->eS->SetAid(seg->Aid(0), 0);
      ect->eS->SetP(seg->P());
      ect->eS->SetVid(seg->Vid(0),0);
      ect->eS->SetW(70);
      ect->eS->SetDZem(seg->DZem());
      ect->Fill();
      ihit++;
    }
    cout << "We have saved " << ihit << " hits in plate " << i << endl;
    ect->Close();
  }
  return 0;
}
