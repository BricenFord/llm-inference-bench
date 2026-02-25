#!/usr/bin/env bash
# Configure per inference engine (e.g., ollama, ray, etc.)
# Submits all generated SBATCH jobs for the selected engine.

set -euo pipefail

ENGINE_DIR="generated/ollama"

mkdir -p results/runs results/logs

shopt -s nullglob

for f in "$ENGINE_DIR"/*.sbatch; do
  echo "Submitting $f"
  sbatch "$f"
done