---
description: In this page most used command in HTCondor will be shown.
---

# HTCondor main commands

## Launching a job with HTCondor

The most common command used in HTCondor allows you to launch jobs:&#x20;

```bash
condor_submit <subfile.sub>
```

## Monitoring a job

The second most common command used in HTCondor allows you to monitor the cluster of jobs you launched, this can be done by typing:

```
condor_q <clusterID> [optional]
```

Such a command che be used as standalone showing you all of the clusters submitted by the user.

### In runtime:

In order to see which job are running within a cluster one can type:

```
condor_q -run <clusterID>
```

Which shows which jobs are running from that cluster.

### Output monitoring

If one wants to look at the output of the jobs that are running, one can type:

```
condor_tail <clusterID.jobID>
```

### User priority

If one wants to give a look at the assigned priority from HTCondor, the command will show all of the users from HTCondor and their assigned priority:

```
condor_userprio | grep <USERNAME>
```

#### References:

{% embed url="https://www.recas-bari.it/images/manuali/ITAManualeHTCondor.pdf" %}
Italian guide found on the internet
{% endembed %}
