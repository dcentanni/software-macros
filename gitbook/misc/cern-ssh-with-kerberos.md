# CERN ssh with Kerberos

This page shows how to set up SSH authentication using CERN Kerberos tickets.

First check for `krb5` installation by running for instance:

```bash
klist -V
```

If krb5 is not installed, run (for Ubuntu):

```bash
sudo apt install krb5-user
```

{% hint style="info" %}
For MacOS users, Kerberos should be already provided, realms and password are managed by the utility app called **Ticket Viewer.**
{% endhint %}

Once `krb5` has been installed overwrite (if possible) the `krb5.conf` file located in `/etc/` with the following one: [krb5.conf](https://github.com/dcentanni/software-macros/blob/main/Misc/krb5.conf).

Next thing to do is to edit the ssh config file located in `~/.ssh/config` adding the following lines:

```
# Allow short host names
# You can add further CERN hosts to the next line
Host !*.cern.ch lxplus* aisplus*
   CanonicalizeHostname yes
   CanonicalDomains cern.ch

Host *.cern.ch
   User USERNAME
   ForwardX11 yes
   # Allow login per Kerberos
   GSSAPIAuthentication yes
   # Transmit AFS token
   GSSAPIDelegateCredentials yes
   # Needed for non FQDNs
   GSSAPITrustDNS yes

# lxplus is a cluster with a shared private ssh key
# stop it from flodding your known_hosts and asking
# every time to check the private key
Host lxplus*.cern.ch aisplus*.cern.ch
   HostKeyAlias cernlxpluskey
   UserKnownHostsFile ~/.ssh/known_hosts.lxplus
```

Now ssh should be configured to use Kerberos ticket for access.

In order to create a ticket one can launch the following command:

```bash
kinit -l 24h00m username@REALM.TOP
```

This will create a ticket lasting for 24 hour.

In order to see all of the current tickets just type

```bash
klist -A
```

If you want to erase all of the active tickets you can write

```bash
kdestroy -A
```

#### References

{% embed url="https://linux.web.cern.ch/docs/kerberos-access/" %}
Guide
{% endembed %}

{% embed url="https://twiki.cern.ch/twiki/bin/view/Main/Kerberos" %}
Guide
{% endembed %}
