import ROOT as r
import sys

fname = sys.argv[1]
if len(sys.argv) > 2: volname = sys.argv[2]
else: volname= ''

if fname == '':
	raise Exception("No filename provided!")

r.gGeoManager.Import(str(fname))
if volname == '':
	print('No volname provided, drawing top volume')
	r.gGeoManager.GetTopVolume().Draw("ogl")
else:
	r.gGeoManager.GetVolume(str(volname)).Draw("ogl")
