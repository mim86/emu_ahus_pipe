#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -ne 2 ]; then
  echo "Usage: $0 <main_folder> <output_folder>"
  exit 1
fi

main_folder="$1"
output_folder="$2"

if [ ! -d "$main_folder" ]; then
  echo "Error: The main folder '$main_folder' does not exist."
  exit 1
fi

mkdir -p "$output_folder"

shopt -s nullglob

folders=()
if compgen -G "$main_folder/barcode*" >/dev/null; then
  folders+=( "$main_folder"/barcode* )
fi
if [ -d "$main_folder/unclassified" ]; then
  folders+=( "$main_folder/unclassified" )
fi

# Fallback to all subfolders if no barcode/unclassified
if [ "${#folders[@]}" -eq 0 ]; then
  for d in "$main_folder"/*/; do
    [ -d "$d" ] && folders+=( "$d" )
  done
fi

if [ "${#folders[@]}" -eq 0 ]; then
  echo "No subfolders found in '$main_folder'. Nothing to do."
  exit 0
fi

for folder in "${folders[@]}"; do
  folder="${folder%/}"
  [ -d "$folder" ] || continue
  folder_name="$(basename "$folder")"

  gz_files=( "$folder"/*.fastq.gz "$folder"/*.fq.gz )
  plain_files=( "$folder"/*.fastq "$folder"/*.fq )

  out="$output_folder/${folder_name}.fastq.gz"

  if [ "${#gz_files[@]}" -gt 0 ] && [ "${#plain_files[@]}" -eq 0 ]; then
    # Only gzipped files — just concat them directly
    cat "${gz_files[@]}" > "$out"
    echo "Concatenated ${#gz_files[@]} gzipped files -> '$out'"
  elif [ "${#gz_files[@]}" -eq 0 ] && [ "${#plain_files[@]}" -gt 0 ]; then
    # Only plain FASTQ files — compress on the fly
    cat "${plain_files[@]}" | gzip -c > "$out"
    echo "Concatenated and gzipped ${#plain_files[@]} plain files -> '$out'"
  elif [ "${#gz_files[@]}" -gt 0 ] && [ "${#plain_files[@]}" -gt 0 ]; then
    # Mixed gzipped and plain — decompress and re-compress
    { zcat "${gz_files[@]}" 2>/dev/null || gunzip -c "${gz_files[@]}" 2>/dev/null; } | cat - "${plain_files[@]}" | gzip -c > "$out"
    echo "Mixed input: concatenated ${#gz_files[@]} gz and ${#plain_files[@]} plain -> '$out'"
  else
    echo "No FASTQ files found in '$folder' — skipping."
  fi
done

echo "Done."

