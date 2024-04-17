#!/usr/bin/env bash

if [[ $# -eq 0 ]]; then
  exit 1
fi

input_path=$1
output_directory=$2
name=$3

echo "Outputting cumulative report to $output_directory"
pdflatex --halt-on-error -interaction=batchmode -output-directory="${output_directory}" "${input_path}"
pdflatex --halt-on-error -interaction=batchmode -output-directory="${output_directory}" "${input_path}"

rm "${output_directory}/report.log"
rm "${output_directory}/report.aux"
mv "report.pdf" "$name"
