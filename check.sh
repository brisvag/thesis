#!/bin/sh

# exclude papers (or should we fix them too?)
FILES=$(fd --exclude "*_paper*" --glob "*.tex")

echo === Checking for TODO comments
rg --vimgrep 'TODO' $FILES
rg --vimgrep 'CITE' $FILES
rg --vimgrep 'FIG' $FILES
echo

echo === Checking for cryo-em/cryo-et variations
rg --vimgrep 'cryoem|cryo_em|cryoet|cryo_et' $FILES
rg --vimgrep -s '(C|c)ryo-(em|et)' $FILES
rg --vimgrep -s '\w\W+Cryo-(EM|ET)' $FILES
echo

echo === Checking for space before \\cite commands
rg --vimgrep ' \\cite\{' $FILES
echo

# echo === Style checking with Vale
# vale --output vale_template.tmpl $FILES
# vale --output line $FILES
