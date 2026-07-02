# PyROOT

This page will present some useful code snippets that can be used in PyROOT in everyday work codes.

## Compute Ratio plot

This is function already implemented in PyROOT but it doesn't allow you to compute a ratio plot between two histograms with different number of bins, the following snippet provides a `TGraphErrors` object which include the ratio of the bin content of the input `TH1`'s as point. The X position of each point is given by the bin center of the first histogram.

> **NOTE**: the following code can be applied only if the bin width of the two input histograms is the same. Indeed, the code takes into account the minimum range given by the number of bin of the two histograms.

Here's the code:

```python
def ComputeRatioPlot(h1, h2, title, compl=False):
    from array import array
    first1, last1 = h1.GetBinLowEdge(1), h1.GetBinLowEdge(h1.GetNbinsX()+1)
    first2, last2 = h2.GetBinLowEdge(1), h2.GetBinLowEdge(h2.GetNbinsX()+1)
    binwidth1, binwidth2 = float((last1-first1)/h1.GetNbinsX()),
                           float((last2-first2)/h2.GetNbinsX())
    if h1.GetNbinsX() != h2.GetNbinsX() and binwidth1 != binwidth2:
        print("N. of bins is different, not able to compute ratio")
        return
    else:
        lastbin = min(h1.GetNbinsX(), h2.GetNbinsX())
        rp = ROOT.TGraphErrors(lastbin)
        rp.SetTitle(title)
        rp.SetName('Ratio_'+title)
        #xsigma = array('d', [binwidth1 for i in range(lastbin)])
        for ibin in range(1, lastbin+1):
            bincontent1 = h1.GetBinContent(ibin)
            bincontent2 = h2.GetBinContent(ibin)
            #ratio = 0
            if bincontent2 ==0: continue
            if compl:
                if bincontent1==0: ratio = 1
                else: ratio = 1-float(bincontent1/bincontent2)
            else: ratio = float(bincontent1/bincontent2)
            bincenter = h1.GetBinCenter(ibin)
            print(ratio, bincenter)
            rp.SetPoint(ibin-1, bincenter, ratio)
            rp.SetPointError(ibin-1, binwidth1/2., 0)
        return rp
```

## Load histograms from ROOT file

The following snippet is a useful tool which can provide a list of all the histograms contained in a `.root` file. The function returns a Python dictionary with names of histograms as keys and `TH1` objects as values.

> **NOTE**: for now it works for the `TH1` class (and `TH2`) only, so `TGraph` and `TGraphErrors` objects are excluded.

Here's the code:

```python
def load_hists(histfile, query=None):
    f = ROOT.TFile.Open(histfile)
    histlist = {}
    keylist = f.GetListOfKeys()
    for key in keylist:
        if query is not None and key.GetName() not in query:
            continue
        hist = f.Get(key.GetName())
        # check if histogram is readable
        try:
            hist.SetDirectory(ROOT.gROOT)
        except:
            print('### WARNING ###: key "'+str(key.GetName())+'" does not correspond to valid hist.')
            continue
        hist.SetName(key.GetName())
        histlist[key.GetName()] = hist
    if len(histlist) == 0: raise Exception('ERROR: histlist is empty!')
    f.Close()
    return histlist
```

The function includes the query argument as well which allows to select specific histograms from the input file, specifying `query` as a Python list.

## Load single histogram from multiple root files

The following code snippet is a useful tool which allows to extract histograms (a `TH1` ROOT object), given the object name, from different files.

This can be useful when having different files
