# Run PyROOT in batch mode

When running in batch mode, PyROOT does not display any graphics. You can activate the batch mode as follows:

1. Pass `-b` as a command line argument, for example, `python -b <yourscript.py>`. For this work you must set `ROOT.PyConfig.IgnoreCommandLineOptions = False` inside the PyROOT script.
2.  Call `gROOT.SetBatch` in the PyROOT script **right after** importing ROOT



    ```python
     import ROOT
     ROOT.gROOT.SetBatch(True)
    ```
