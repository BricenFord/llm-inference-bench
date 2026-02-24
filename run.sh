#!/usr/bin/env bash
set -euo pipefail

# Submit all generated sbatch files under generated/sbatch/**
if [[ ! -d "generated/sbatch" ]]; then
  echo "ERROR: generated/sbatch not found. Run ./build.sh first."
  exit 1
fi

# Ensure results dir exists (sbatch writes stdout/stderr here)
mkdir -p results/runs

find generated/sbatch -type f -name "*.sbatch" -print0 | sort -z | while IFS= read -r -d '' f; do
  echo "Submitting: $f"
  sbatch "$f"
done