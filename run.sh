#!/usr/bin/env bash
# Submits all generated SBATCH jobs for the selected engine.

set -euo pipefail

mkdir -p results/runs results/logs

cd generated/ollama # Configure per inference engine (generated/(engine))

for f in *.sbatch; do
  echo "Submitting $f"
  sbatch "$f"
done