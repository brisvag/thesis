#!/bin/sh

# exclude papers (or should we fix them too?)
FILES=$(fd --glob "*.tex")

echo === Checking for TODO-style comments
rg --vimgrep 'TODO' $FILES
rg --vimgrep 'CITE' $FILES
rg --vimgrep 'FIG' $FILES
rg --vimgrep 'NOTE' $FILES
rg --vimgrep 'FIXME' $FILES
rg --vimgrep 'XXX' $FILES
echo

echo === Checking for cryo-em/cryo-et variations
rg --vimgrep 'cryoem|cryo_em|cryoet|cryo_et' $FILES
rg --vimgrep -s '(C|c)ryo-(em|et)' $FILES
rg --vimgrep -s '\w\W+Cryo-(EM|ET)' $FILES
echo

echo === Checking for space before \\cite commands
rg --vimgrep ' \\cite\{' $FILES
echo

echo === checking capitalization ===
rg --vimgrep -s 'fourier' $FILES

echo === open-source without hyphen ===
rg --vimgrep -s '(O|o)pen source' $FILES

echo === captions missing title or empty ===
rg --vimgrep -s '^    \\caption\{' $FILES
rg --vimgrep -s '\\titledcaption\{' $FILES
rg --vimgrep -s '\\caption\{\}' $FILES

echo === italicized in vitro etc ===
rg --vimgrep -s '[^\{]in vitro' $FILES
rg --vimgrep -s '[^\{]in situ' $FILES
rg --vimgrep -s '[^\{]in vivo' $FILES
rg --vimgrep -s '[^\{]in cellulo' $FILES
rg --vimgrep -s '[^\{]in silico' $FILES
rg --vimgrep -s 'radiodurans[^\}]' $FILES

echo === temporary stuff ===
rg --vimgrep 'sloppy' $FILES

# echo === Style checking with Vale
# vale --output vale_template.tmpl $FILES
# vale --output line $FILES
