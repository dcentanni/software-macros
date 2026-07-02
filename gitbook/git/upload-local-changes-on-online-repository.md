# Upload local changes on online repository

When working within a project one needs to update files with changes on a specified repository.

As first thing one has to **update its local repository** with the last changes made to the remote one following [these](download-online-changes-to-local-repository.md) steps

Then, you are ready to upload you changes to the online repository:

```
git add <file(s)>
git commit -m "<commit_message>"
git push <remote> <branch>
```

{% hint style="info" %}
Before pushing your changes, one can add/commit multiple times obtaining different uploads with different commits
{% endhint %}

Then git credentials will be requested in order to finalize the upload.
