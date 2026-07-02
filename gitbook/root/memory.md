# Memory

## Memory checking

ROOT framework offers classes which allow for memory checking of the running script.

One can retrieve informations of the memory being used and add it to a `TGraph` for instance.

All of the following command are performed in PyROOT.

After importing ROOT in the python script we retrieve the memory information through:

```python
mymemory = ROOT.MemInfo_t()
```

And create a graph in which we store the memory information with respect to the event numbers to see how it changes.

```python
memgraph = ROOT.TGraph()
```

Then within the event loop:

```python
ROOT.gSystem.GetMemInfo(mymemory)
memgraph.AddPoint(i_event, mymemory.fMemUsed)
```

In particular we are requiring to fiil the `TGraph` above with the value of the memory used, which is in MB.
