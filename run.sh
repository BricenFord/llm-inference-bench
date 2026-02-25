#!/usr/bin/env bash
set -euo pipefail

mkdir -p results/runs results/logs

for f in generated/sbatch/*.sbatch; do
  echo "Submitting $f"
  sbatch "$f"
done
