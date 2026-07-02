---
description: >-
  This page will show some of features of git and some useful commands found on
  the internet
---

# Git base commads

Git is a useful software _designed to handle everything from small to very large projects with speed and efficiency._

### Commands

The following is a list of base commands mostly used in everyday usage.

`git init`  Initializes git in the repository you are in.

`git status` Displays the status of all the changes made to tracked files and untracked files.

`git add <file>` Makes git track the file and all of its changes, it also "put the file in pipeline" ready to be uploaded to the remote.

{% hint style="info" %}
With `git add .` , all tracked files are put in "pipeline".
{% endhint %}

`git commit` Commits all the changes you've done to the previously added files.

{% hint style="info" %}
With `git commit -m` "`<commit message>"` you directly commit the changes specifying the commit message.
{% endhint %}

`git push <remote> <branch>` Pushes on remote/branch the committed changes you made to the tracked files.

`git checkout <remote>/<branch>` Allows to switch between remotes/branches.

{% hint style="info" %}
With `git checkout -b <branchname>` you create a new branch.
{% endhint %}

`git remote add <remote> <remoteaddress>` Adds a new remote from address.

{% hint style="info" %}
`git remote -v` shows for every remote the URLs at which they are pointing.
{% endhint %}

`git branch -vv` Shows your local active branches, which remote they belong to and their last commits.

### Update branch from master

In order to update a branch with the latest updates from the master branch:

```
git checkout b1
git merge origin/master
```

Then resolve all conflict if present and make a new commit and push changes.

### Author commit with differen user

To do this you can just specify it at the time of the commit:

```
git commit --author="Name <email>" -m "commit message"
```
