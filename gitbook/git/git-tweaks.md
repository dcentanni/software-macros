# Git tweaks

In the following, few commands on customisation of git functionalities will be presented.

## Disable ssh-gnome askpass

This tweak allows to disable the annoying ssh-askpass window showing up when uploading changes to an online repository, making git to ask you credentials directly by terminal.

Open `.bashrc` or `.zshrc` file in your ssh desired terminal and then add these lines:

```
[ -n "$SSH_CONNECTION" ] && unset SSH_ASKPASS
export GIT_ASKPASS=
```

Then update source files by:

```
source .bashrc
```

> NOTE: or alternatively `source .zshrc`
