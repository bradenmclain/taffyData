#!/usr/bin/env bash

if [[ $# -eq 0 ]]; then
  exit 1
fi

input_path=$1
output_directory=$2
name=$3

echo "Outputting cumulative report to $output_directory"
pdflatex --halt-on-error -interaction=batchmode -output-directory="${output_directory}" "${input_path}.tex"
pdflatex --halt-on-error -interaction=batchmode -output-directory="${output_directory}" "${input_path}.tex"

rm "${output_directory}/${input_path}.log"
rm "${output_directory}/${input_path}.aux"
mv "${input_path}.pdf" "$name"
