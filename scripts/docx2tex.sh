#!/bin/zsh

set -e

input=$1
output=${1%.*}.tex

pandoc -f docx -t latex --wrap preserve $input -o $output
sed -i 's/^\\textbf{\(.*\)}/\\section{\1}/g' $output
sed -i 's/^\\emph{\\textbf{\(.*\)}}/\\subsection{\1}/g' $output
sed -i 's/paragraph/subsection/g' $output
sed -i 's/\\texorpdfstring{\\textbf{\(.*\)}}{.*/\1}/g' $output

sed -i 's/emph{\([^ ]\+\) /textit{\1~/g' $output
sed -i 's/Fig\. /Fig.~/g' $output
sed -i 's/\. /.\n/g' $output
sed -i 's/~/ /g' $output

sed -i 's/\\textsuperscript{\([^ ]\+\)}/~\\cite{\1}/g' $output
sed -i 's/(Figure \(.*\))/(\\autoref{\1})/g' $output

echo 'fix nm, ±, textasciitilde, etc to use \sim'
echo 'fix some cite(-1) which should actually be exponents'
echo 'lowercase sections'
echo 'fix \`...single-quote (also double!)'  # %s/``\(.*\)''/"\1"/g  and  %s/`\(.*\)'/"\1"/g
