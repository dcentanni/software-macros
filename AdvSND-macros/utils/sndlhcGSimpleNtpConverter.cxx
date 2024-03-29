#include <iostream>
#include <fstream>
#include <set>

#include "TFile.h"
#include "TTree.h"
#include "TMath.h"
#include "TRandom3.h"

#include "ShipUnit.h"

#include "Tools/Flux/GSimpleNtpFlux.h"

/*
  Converts neutrino rays generated by FLUKA into GSimpleNtpFlux format for GENIE
*/

int main(int argc, char** argv){

  if (argc != 4) {
    std::cout << "Three arguments required: path to FLUKA file AND output file name AND number of pp collisions used to generate FLUKA file." << std::endl;
    return -1;
  }

  std::string inFileName = std::string(argv[1]);
  std::string outFileName = std::string(argv[2]);
  double pp_collision_number = std::stod(argv[3]);

  // Convert FLUKA to PDG particle IDs. (ONLY NEUTRINOS IMPLEMENTED!!!)
  std::map<int, int> FLUKAtoPDG { {27, 14},
                                  {28, -14},
				  {5, 12},
				  {6, -12},
				  {43, 16},
				  {44, -16} };

  // To generate a random seed which is stored in the metadata.
  TRandom3 * ran = new TRandom3();

  bool verbose = false;

  // Scoring plane info
  // Plane z in FLUKA coordinates: 48386 cm
  // FLUKA z = 0 in sndsw coordinates : -48000 cm
 // double z = (48386-48000); // In cm for consistency with the FLUKA file.

  //double plane_corner[] = {-70., 5., z};
  //double plane_dir1[] = {140., 0, 0};
  //double plane_dir2[] = {0, 65., 0};

  // Set up input file
  std::ifstream in_file(inFileName);

  // Input variables
  /*
 # Scoring particles entering Region No         2935
 # Col  1: FLUKA run number
 # Col  2: primary event number
 # -- Particle information --
 # Col  3: FLUKA particle type ID
 # Col  4: Generation number
 # Col  5: Kinetic energy (GeV)
 # Col  6: Statistical weight
 # -- Crossing at scoring plane --
 # Col  7: x coord (cm)
 # Col  8: y coord (cm)
 # Col  9: x dir cosine
 # Col 10: y dir cosine
 # Col 11: z coord (cm)
 # Col 12: Particle age since primary event (sec)
 # Col 13: Origin of the charm decay
  */

  int FlukaRun, evtNumber, FlukaID, generationN;
  float Ekin, weight, x, y, x_cos, y_cos, z, age, dcay_charm;

  TFile * fOut = new TFile(outFileName.c_str(), "RECREATE");
  TTree * tOut = new TTree("flux", "a simple flux n-tuple");
  TTree * metaOut = new TTree("meta","metadata for flux n-tuple");
  
  genie::flux::GSimpleNtpEntry * gsimple_entry = new genie::flux::GSimpleNtpEntry;
  tOut->Branch("entry", &gsimple_entry);
  genie::flux::GSimpleNtpMeta*  meta_entry  = new genie::flux::GSimpleNtpMeta;
  metaOut->Branch("meta", &meta_entry);

  genie::flux::GSimpleNtpAux*  aux_entry  = new genie::flux::GSimpleNtpAux;
  tOut->Branch("aux", &aux_entry);


  UInt_t metakey = TString::Hash(outFileName.c_str(),strlen(outFileName.c_str()));
  metakey &= 0x7FFFFFFF;

  // Metadata accumulators:
  std::set<int> pdglist;
  double min_weight = 1e10;
  double max_weight = -1e10;
  double max_energy = 0;

  unsigned long int counter = 0;

  if (in_file.is_open()){
    string in_line;
    while (!in_file.eof()){
      getline(in_file, in_line);

      // Skip lines containing "#"
      if (in_line.find("#") == in_line.npos){
	in_file >> FlukaRun
		>> evtNumber
		>> FlukaID
		>> generationN
		>> Ekin
		>> weight
		>> x
		>> y
		>> x_cos
		>> y_cos
		>> z
		>> age
		>> dcay_charm;

	gsimple_entry->Reset();
	aux_entry->Reset();

    
	if (verbose) std::cout << "Got entry " << counter++ << std::endl;
    
	if (verbose){
	  std::cout << FlukaRun << "\n"
		    << evtNumber << "\n"
		    << FlukaID << "\n"
		    << generationN << "\n"
		    << Ekin << "\n"
		    << weight << "\n"
		    << x << "\n"
		    << y << "\n"
		    << z << "\n"
		    << x_cos << "\n"
		    << y_cos << "\n"
		    << z << "\n"	
		    << age << "\n"
		    << dcay_charm << "\n"
		    << "--------------------------------------------------" << std::endl;
	}
  z = (z-48000);
	gsimple_entry->metakey = metakey;
	gsimple_entry->pdg = FLUKAtoPDG[FlukaID];
	gsimple_entry->wgt = weight;
	gsimple_entry->vtxx = x*ShipUnit::cm/ShipUnit::m; // in m
	gsimple_entry->vtxy = y*ShipUnit::cm/ShipUnit::m;
	gsimple_entry->vtxz = z*ShipUnit::cm/ShipUnit::m;
	gsimple_entry->dist = 0.; // Distance from hadron decay point to neutrino "vertex", to use for oscillations, for example. Don't use.

	// I'm assuming x_cos, y_cos are normalized.
	double z_cos = sqrt(1 - pow(x_cos, 2) - pow(y_cos, 2));
	// And massless neutrinos
	gsimple_entry->px = Ekin*x_cos; // in GeV/c
	gsimple_entry->py = Ekin*y_cos;
	gsimple_entry->pz = Ekin*z_cos;
	gsimple_entry->E = Ekin;
    
	// Set auxiliary data
	aux_entry->auxint.push_back(FlukaRun);
	aux_entry->auxint.push_back(evtNumber);
	aux_entry->auxint.push_back(FlukaID);
	aux_entry->auxint.push_back(generationN);
	aux_entry->auxint.push_back(dcay_charm);    

	aux_entry->auxdbl.push_back(age);
	aux_entry->auxdbl.push_back(weight);

	// Accumulate metadata
	pdglist.insert(gsimple_entry->pdg);
	min_weight = TMath::Min(min_weight, gsimple_entry->wgt);
	max_weight = TMath::Max(max_weight, gsimple_entry->wgt);
	max_energy = TMath::Max(max_energy, gsimple_entry->E);

	// All done!
	tOut->Fill();
      }
    }
  }
  double plane_corner[] = {-100., -20, 47810-48000}; // scoring plane dimensions of HL-LHC FLUKA Neutrino file
  double plane_dir1[] = {200., 0, 0};
  double plane_dir2[] = {0, 160., 0};

  // Sort out metadata
  // Copy pdg list
  meta_entry->pdglist.clear();
  for (std::set<int>::const_iterator pdg_iterator = pdglist.begin();
       pdg_iterator != pdglist.end();
       ++pdg_iterator) meta_entry->pdglist.push_back(*pdg_iterator);
  meta_entry->maxEnergy = max_energy;
  meta_entry->maxWgt = max_weight;
  meta_entry->minWgt = min_weight;
  
  meta_entry->protons = pp_collision_number; // Number of pp collisions.
  for (int i = 0; i < 3; i++) meta_entry->windowBase[i] = plane_corner[i]*ShipUnit::cm/ShipUnit::m;
  for (int i = 0; i < 3; i++) meta_entry->windowDir1[i] = plane_dir1[i]*ShipUnit::cm/ShipUnit::m;
  for (int i = 0; i < 3; i++) meta_entry->windowDir2[i] = plane_dir2[i]*ShipUnit::cm/ShipUnit::m;
  
  meta_entry->infiles.push_back(inFileName);
  meta_entry->seed = ran->GetSeed();
  meta_entry->metakey = metakey;

  meta_entry->auxintname.push_back("FlukaRun");
  meta_entry->auxintname.push_back("evtNumber");
  meta_entry->auxintname.push_back("FlukaID");
  meta_entry->auxintname.push_back("generationN");
  meta_entry->auxintname.push_back("dcay_charm");

  meta_entry->auxdblname.push_back("age");
  meta_entry->auxdblname.push_back("FLUKA_weight");

  metaOut->Fill();
  
  fOut->cd();
  metaOut->Write();
  tOut->Write();
  fOut->Close();

}

