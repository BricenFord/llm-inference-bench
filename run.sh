#!/usr/bin/env bash
# Configure per inference engine (generated/)
# Submits all generated SBATCH jobs for the selected engine.

set -euo pipefail

mkdir -p results/runs results/logs

cd generated/ollama

for f in *.sbatch; do
  echo "Submitting $f"
  sbatch "$f"
done