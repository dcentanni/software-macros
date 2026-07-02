---
description: This page will show some notes on .sh and .sub files for HTCondor scripts
---

# HTCondor .sh & .sub files

## Recipe for building .sh files

First of all you can use ProcID and ClusterID HTCondor variables as coding for your error/log/output files once added the shebang `#! /bin/bash`:

```bash
ClusterId=$1
ProcId=$2
```

Now in **SNDSW** one needs to instanciate the environment, you can do it by writing (in my case) **(OUTDATED)**:

```bash
SNDLHC_mymaster=/afs/cern.ch/user/d/dannc/
export ALIBUILD_WORK_DIR=$SNDLHC_mymaster/sw #for alienv
echo "SETUP"
source /cvmfs/sndlhc.cern.ch/latest/setUp.sh
eval `alienv load sndsw/latest`
```

### (FIX) HTCondor failing sndsw environment

The following line fixes the issue related to HTCondor not loading the `sndsw` environment:

```bash
# Set up SND environment
SNDBUILD_DIR=/afs/cern.ch/user/d/dannc/sw
source /cvmfs/sndlhc.cern.ch/SNDLHC-2022/June10/setUp.sh
eval `alienv load -w $SNDBUILD_DIR --no-refresh sndsw/latest`
```

The `--no-refresh` option seems to fix the problem in which the system was trying to remove things from the `BUILD` directory.

## Recipe for building .sub files

### Base ingredients

HTCondor offers a wide variety of options to build .sub files depending on different needs. Nevertheless a “must-have” ingredient for `.sub` files is the part where executable, error, log and output files are specified, as in the following:

```
executable            = <pathToExecutableFile>
arguments             = <arguments needed by the .sh> 
output                = <pathAtYourChoice>/output/<filename>.$(ClusterId).$(ProcId).out
error                 = <pathAtYourChoice>/error/<filename>.$(ClusterId).$(ProcId).err
log                   = <pathAtYourChoice>/log/<filename>.$(ClusterId).log
```

{% hint style="info" %}
Usually arguments used by (my) .sh files are $(ClusterId) and $(ProcId) which are very useful for indexing the processes and iterations.
{% endhint %}

Then the `.sub` file proceeds with some of instructions to be given to the batch system, for example, in my case:

```
getenv = false
notification = Error
notify_user = name.lastname@cern.ch
should_transfer_files = YES
```

### Failed jobs relaunching

Useful instructions to **automatically relaunch** jobs that exit with error codes can be added:

```
on_exit_remove = (ExitBySignal == False) && (ExitCode == 0)
max_retries = 3
```

### Job Flavours

The accounting group can be specified, `+AccountingGroup = "group_u_SNDLHC.users"` and the `JobFlavour`, here's the list from HTCondor:

```
+JobFlavour    = "espresso"         #20 minutes
+JobFlavour    = "microcentury"     #1 hour
+JobFlavour    = "longlunch         #2 hours
+JobFlavour    = "workday           #8 hours
+JobFlavour    = "tomorrow          #1 day
+JobFlavour    = "testmatch         #3 days
+JobFlavour    = "nextweek          #1 week
```

### Queue options

In the end, always remeber to launch the `queue` command to submit jobs, it can be followed by simply a number which specifies how many jobs will be submitted to the batch system or even a list of variables in a list as in the following:

```
queue Item from Jobs
```

Where `Jobs` is a file containing numbers or filenames which `queue` loops on.

{% hint style="info" %}
`Item` can also be used in the previous instructions to help the parallelization or some other things, it can be accessed by `$(Item)`
{% endhint %}

Next will show how to build .sh files for **simulation launching** and **analysis scripts launching**.
