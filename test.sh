#!/usr/bin/env bash

if [[ $# -eq 0 ]]; then
  exit 1
fi

input_path=$1

touch "$input_path"