---
description: This page shows some of useful bash commands found on the internet
---

# Useful snippets for coding

## Text coloring

Bash supports text coloring in scripts, on can specify the coloring variables with:

```bash
RED=$'\033[0;31m' #Red coloring
NC=$'\033[0m' #No coloring
```

Then in a script, to start coloring the text just add `${RED}`&#x20;

## Automatically acquire filename in directory

Bash can automatically assign to a variable the complete name of the file you want in a directory:

```bash
FILE=$(ls <startoffilename*.ext>)
```

## Check the existence of file in a directory

This single command will check the existence of the variable `$FILE` and returns true if it does:

```bash
[ ! -d "$FILE" ] && echo "$FILE exists!"
```

or alternatively, using if statement:

```bash
if [ ! -f "$FILE" ]
    then
        echo "$FILE doesn't exist !"
    else
        echo "$FILE exists !"
fi
```

## Comparing integer variable with if statement

This will help to compare to integers, one from command line (or simply as variable) and the other as assigned:

```bash
$INTEGER=$1
if [[ "$INTEGER" == "1" ]]
    then
        echo "They are the same"
    else
        echo "They are different"
fi
```

## Ask user to confirm with y/n reply

The following snippet will show how to ask for confirmation without pressing enter:

```bash
echo "Will you reply my question ?"
read -p "Please confirm (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]
    then
	return
fi
echo "You answered yes!"
```

If the reply is "y" the script will continue otherwise it will return and close the script execution.
