void DoCanvas(TCanvas *name, string objname, TH1 *hname, string x, string y){
   gStyle->SetOptStat("emr");
   name = new TCanvas((objname).c_str(), "", 1190, 757);
   hname->GetXaxis()->SetTitle((x).c_str());
   hname->GetYaxis()->SetTitle((y).c_str());
   hname->SetLineWidth(2);
   hname->SetLineColor(kRed);
   hname->SetFillStyle(3005);
   hname->SetFillColor(kRed);
   hname->Draw();
}

void DoCanvas2(TCanvas *name1, TH1 *hname1, TH1 *hname2, string x, string y){
   gStyle->SetOptStat("emr");
	name1 = new TCanvas("name1", "", 1190, 757);
	name1->Divide(1, 2);
   name1->cd(1);
   hname1->Draw();
   name1->cd(2);
   hname2->Draw();
}

void Histo2(TCanvas *c,TH1 *h1, TH1 *h2, string histo_name[2], string h_axis[2]){
   gStyle->SetOptStat("emr");
   c = new TCanvas("c", "", 1190, 757);
   int n1 = h1->GetEntries();
   int n2 = h2->GetEntries();
   h1->SetLineColor(kCyan-7); h2->SetLineColor(kOrange+8);
   h1->GetXaxis()->SetTitle((h_axis[0]).c_str()); h1->GetYaxis()->SetTitle((h_axis[1]).c_str());
   h2->GetXaxis()->SetTitle((h_axis[0]).c_str()); h2->GetYaxis()->SetTitle((h_axis[1]).c_str());
   h1->SetLineWidth(2); h2->SetLineWidth(2);
   h1->SetFillColor(kCyan-7); h2->SetFillColor(kOrange+8);
   h1->SetFillStyle(3001); h2->SetFillStyle(3001);
   TLegend *legenda= new TLegend(0.7, 0.9, 0.9, 0.7);    
   legenda->AddEntry(h1,(histo_name[0]).c_str(),"f"); 
   legenda->AddEntry(h2,(histo_name[1]).c_str(),"f");
   h1->Draw();
   h2->Draw("SAME");
   legenda->Draw();
}
void Histo3(TCanvas *c, string objname, TH1 *h1, TH1 *h2, TH1 *h3, string histo_name[3], string h_axis[2]){
   gStyle->SetOptStat("emr");
   c = new TCanvas((objname).c_str(), "", 1190, 757);
   int n1 = h1->GetEntries();
   int n2 = h2->GetEntries();
   int n3 = h3->GetEntries();
   h1->SetLineColor(kCyan-7); h2->SetLineColor(kOrange+8); h3->SetLineColor(kGreen-3); 
   h1->GetXaxis()->SetTitle((h_axis[0]).c_str()); h1->GetYaxis()->SetTitle((h_axis[1]).c_str());
   h2->GetXaxis()->SetTitle((h_axis[0]).c_str()); h2->GetYaxis()->SetTitle((h_axis[1]).c_str());
   h3->GetXaxis()->SetTitle((h_axis[0]).c_str()); h3->GetYaxis()->SetTitle((h_axis[1]).c_str());
   h1->SetLineWidth(2); h2->SetLineWidth(2); h3->SetLineWidth(2);
   h1->SetFillColor(kCyan-7); h2->SetFillColor(kOrange+8); h3->SetFillColor(kGreen-3);
   h1->SetFillStyle(3004); h2->SetFillStyle(3005); h3->SetFillStyle(3004);
   TLegend *legenda= new TLegend(0.7, 0.9, 0.9, 0.7);    
   legenda->AddEntry(h1,(histo_name[0]+" - N. entries "+std::to_string(n1)).c_str()); 
   legenda->AddEntry(h2,(histo_name[1]+" - N. entries "+std::to_string(n2)).c_str());
   legenda->AddEntry(h3,(histo_name[2]+" - N. entries "+std::to_string(n3)).c_str());
   h1->Draw();
   h2->Draw("SAME");
   h3->Draw("SAME");
   legenda->Draw();
}

   void Histo23(TCanvas *c, string objname, TH2 *h1, TH2 *h2, TH2 *h3, string histo_name[3], string h_axis[2]){
 
   c = new TCanvas((objname).c_str(), "", 1190, 757);
   int n1 = h1->GetEntries();
   int n2 = h2->GetEntries();
   int n3 = h3->GetEntries();
   h1->GetXaxis()->SetTitle((h_axis[0]).c_str()); h1->GetYaxis()->SetTitle((h_axis[1]).c_str());
   h2->GetXaxis()->SetTitle((h_axis[0]).c_str()); h2->GetYaxis()->SetTitle((h_axis[1]).c_str());
   h3->GetXaxis()->SetTitle((h_axis[0]).c_str()); h3->GetYaxis()->SetTitle((h_axis[1]).c_str());
   h1->SetMarkerColor(9); h2->SetMarkerColor(46);
   h1->SetMarkerStyle(20); h2->SetMarkerStyle(20); h3->SetMarkerStyle(38);
   TLegend *legenda= new TLegend(0.7, 0.9, 0.9, 0.7);    
   legenda->AddEntry(h1,(histo_name[0]+" N. entries "+std::to_string(n1)).c_str()); 
   legenda->AddEntry(h2,(histo_name[1]+" N. entries "+std::to_string(n2)).c_str());
   legenda->AddEntry(h3,(histo_name[2]+" N. entries "+std::to_string(n3)).c_str());
   h3->Draw();
   h2->Draw("SAME");
   h1->Draw("SAME");
   legenda->Draw();

} 

   void Histo25(TCanvas *c, string objname, TH2 *h1, TH2 *h2, TH2 *h3, TH2 *h4, TH2 *h5, string histo_name[5], string h_axis[2]){
 
   c = new TCanvas((objname).c_str(), "", 1190, 757);
   int n1 = h1->GetEntries();
   int n2 = h2->GetEntries();
   int n3 = h3->GetEntries();
   int n4 = h4->GetEntries();
   int n5 = h5->GetEntries();
   h1->GetXaxis()->SetTitle((h_axis[0]).c_str()); h1->GetYaxis()->SetTitle((h_axis[1]).c_str());
   h2->GetXaxis()->SetTitle((h_axis[0]).c_str()); h2->GetYaxis()->SetTitle((h_axis[1]).c_str());
   h3->GetXaxis()->SetTitle((h_axis[0]).c_str()); h3->GetYaxis()->SetTitle((h_axis[1]).c_str());
   h4->GetXaxis()->SetTitle((h_axis[0]).c_str()); h4->GetYaxis()->SetTitle((h_axis[1]).c_str());
   h5->GetXaxis()->SetTitle((h_axis[0]).c_str()); h5->GetYaxis()->SetTitle((h_axis[1]).c_str());
   h1->SetMarkerColor(9); h2->SetMarkerColor(46);  h3->SetMarkerColor(4);  h4->SetMarkerColor(12);
   h1->SetMarkerStyle(20); h2->SetMarkerStyle(20); h3->SetMarkerStyle(38); h4->SetMarkerStyle(22); h5->SetMarkerStyle(23);
   TLegend *legenda= new TLegend(0.7, 0.9, 0.9, 0.7);    
   legenda->AddEntry(h1,(histo_name[0]+" N. entries "+std::to_string(n1)).c_str()); 
   legenda->AddEntry(h2,(histo_name[1]+" N. entries "+std::to_string(n2)).c_str());
   legenda->AddEntry(h3,(histo_name[2]+" N. entries "+std::to_string(n3)).c_str());
   legenda->AddEntry(h4,(histo_name[3]+" N. entries "+std::to_string(n4)).c_str());
   legenda->AddEntry(h5,(histo_name[4]+" N. entries "+std::to_string(n5)).c_str());
   h5->Draw();
   h4->Draw("SAME");
   h3->Draw("SAME");
   h2->Draw("SAME");
   h1->Draw("SAME");
   legenda->Draw();

} 
   void Histo26(TCanvas *c, string objname, TH2 *h1, TH2 *h2, TH2 *h3, TH2 *h4, TH2 *h5, TH2 *h6, string histo_name[6], string h_axis[2]){
 
   c = new TCanvas((objname).c_str(), "", 1190, 757);
   int n1 = h1->GetEntries();
   int n2 = h2->GetEntries();
   int n3 = h3->GetEntries();
   int n4 = h4->GetEntries();
   int n5 = h5->GetEntries();
   int n6 = h6->GetEntries();
   h1->GetXaxis()->SetTitle((h_axis[0]).c_str()); h1->GetYaxis()->SetTitle((h_axis[1]).c_str());
   h2->GetXaxis()->SetTitle((h_axis[0]).c_str()); h2->GetYaxis()->SetTitle((h_axis[1]).c_str());
   h3->GetXaxis()->SetTitle((h_axis[0]).c_str()); h3->GetYaxis()->SetTitle((h_axis[1]).c_str());
   h4->GetXaxis()->SetTitle((h_axis[0]).c_str()); h4->GetYaxis()->SetTitle((h_axis[1]).c_str());
   h5->GetXaxis()->SetTitle((h_axis[0]).c_str()); h5->GetYaxis()->SetTitle((h_axis[1]).c_str());
   h6->GetXaxis()->SetTitle((h_axis[0]).c_str()); h6->GetYaxis()->SetTitle((h_axis[1]).c_str());
   h1->SetMarkerColor(9); h2->SetMarkerColor(46);  h3->SetMarkerColor(4);  h4->SetMarkerColor(12);                         h6->SetMarkerColor(3); 
   h1->SetMarkerStyle(20); h2->SetMarkerStyle(20); h3->SetMarkerStyle(38); h4->SetMarkerStyle(22); h5->SetMarkerStyle(23); h6->SetMarkerStyle(21);
   TLegend *legenda= new TLegend(0.7, 0.9, 0.9, 0.7);    
   legenda->AddEntry(h1,(histo_name[0]+" N. entries "+std::to_string(n1)).c_str()); 
   legenda->AddEntry(h2,(histo_name[1]+" N. entries "+std::to_string(n2)).c_str());
   legenda->AddEntry(h3,(histo_name[2]+" N. entries "+std::to_string(n3)).c_str());
   legenda->AddEntry(h4,(histo_name[3]+" N. entries "+std::to_string(n4)).c_str());
   legenda->AddEntry(h5,(histo_name[4]+" N. entries "+std::to_string(n5)).c_str());
   legenda->AddEntry(h5,(histo_name[5]+" N. entries "+std::to_string(n5)).c_str());
   h6->Draw();
   h5->Draw("SAME");
   h4->Draw("SAME");
   h3->Draw("SAME");
   h2->Draw("SAME");
   h1->Draw("SAME");
   legenda->Draw();

} 

   void Vert3(TCanvas *c,TH2 *h1, TH2 *h2, TH2 *h3, string histo_name1[3], string h_axis1[2], TH2 *h4, TH2 *h5, TH2 *h6, string histo_name2[3], string h_axis2[2]){
   gStyle->SetOptStat("emr");
   c = new TCanvas("c", "", 1190, 757);
   c->Divide(2, 1);
   int n1 = h1->GetEntries();
   int n2 = h2->GetEntries();
   int n3 = h3->GetEntries();
   int n4 = h4->GetEntries();
   int n5 = h5->GetEntries();
   int n6 = h6->GetEntries();
   c->cd(1);
   h1->GetXaxis()->SetTitle((h_axis1[0]).c_str()); h1->GetYaxis()->SetTitle((h_axis1[1]).c_str());
   h2->GetXaxis()->SetTitle((h_axis1[0]).c_str()); h2->GetYaxis()->SetTitle((h_axis1[1]).c_str());
   h3->GetXaxis()->SetTitle((h_axis1[0]).c_str()); h3->GetYaxis()->SetTitle((h_axis1[1]).c_str());
   h1->SetMarkerColor(9); h2->SetMarkerColor(46);
   h1->SetMarkerStyle(20); h2->SetMarkerStyle(20); h3->SetMarkerStyle(38);
   TLegend *legenda1= new TLegend(0.7, 0.9, 0.9, 0.7);    
   legenda1->AddEntry(h1,(histo_name1[0]+" N. entries "+std::to_string(n1)).c_str()); 
   legenda1->AddEntry(h2,(histo_name1[1]+" N. entries "+std::to_string(n2)).c_str());
   legenda1->AddEntry(h3,(histo_name1[2]+" N. entries "+std::to_string(n3)).c_str());
   h3->Draw();
   h2->Draw("SAME");
   h1->Draw("SAME");
   legenda1->Draw();
   c->cd(2);
   h4->GetXaxis()->SetTitle((h_axis2[0]).c_str()); h4->GetYaxis()->SetTitle((h_axis2[1]).c_str());
   h5->GetXaxis()->SetTitle((h_axis2[0]).c_str()); h5->GetYaxis()->SetTitle((h_axis2[1]).c_str());
   h6->GetXaxis()->SetTitle((h_axis2[0]).c_str()); h6->GetYaxis()->SetTitle((h_axis2[1]).c_str());
   h4->SetMarkerColor(9); h5->SetMarkerColor(46);
   h4->SetMarkerStyle(20); h5->SetMarkerStyle(20); h6->SetMarkerStyle(38);
   TLegend *legenda2= new TLegend(0.7, 0.9, 0.9, 0.7);    
   legenda2->AddEntry(h4,(histo_name2[0]+" N. entries "+std::to_string(n1)).c_str()); 
   legenda2->AddEntry(h5,(histo_name2[1]+" N. entries "+std::to_string(n2)).c_str());
   legenda2->AddEntry(h6,(histo_name2[2]+" N. entries "+std::to_string(n3)).c_str());
   h6->Draw();
   h5->Draw("SAME");
   h4->Draw("SAME");
   legenda2->Draw();
} 
