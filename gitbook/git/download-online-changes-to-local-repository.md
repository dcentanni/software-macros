# Download online changes to local repository

When working within a project one needs to download latest changes on tracked files from online repository on the local one.

In order to achieve this one can first **update the local with the latest changes**:

```
git fetch <remote> <branch>
```

Then one can merge the online changes with the local repository by:

```
git merge <remote>/<branch>
```

A merge commit file opens with _nano_, for example, one can simply close the file without writing any word and then the merge is complete.

Alternatively one can use:

```
git pull <remote> <branch>
```
