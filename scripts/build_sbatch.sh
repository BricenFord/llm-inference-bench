#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

source config/base.config

for exp in config/experiments/*.config; do
  source "$exp"

  : "${EXP_NAME:?EXP_NAME not set in $exp}"
  : "${ENGINE:?ENGINE not set in $exp}"

  ENGINE_CONFIG="config/engines/${ENGINE}.config"
  SBATCH_TEMPLATE="templates/sbatch.${ENGINE}.template"

  [ -f "$ENGINE_CONFIG" ] || { echo "Missing engine config: $ENGINE_CONFIG" >&2; exit 1; }
  [ -f "$SBATCH_TEMPLATE" ] || { echo "Missing sbatch template: $SBATCH_TEMPLATE" >&2; exit 1; }

  source "$ENGINE_CONFIG"

  out_dir="generated/sbatch/${ENGINE}/${EXP_NAME}"
  mkdir -p "$out_dir"

  client_path="$ROOT/generated/sbatch/${ENGINE}/${EXP_NAME}/${EXP_NAME}.client.py"
  sbatch_out="$out_dir/${EXP_NAME}.sbatch"

  content="$(cat "$SBATCH_TEMPLATE")"

  for var in PARTITION NODES NTASKS CPUS_PER_TASK MEM TIME MAIL_USER MAIL_TYPE MODULE_CUDA MODULE_PYTHON RUNS_DIR LOGS_DIR VENV_DIR REQUIREMENTS_FILE; do
    val="${!var}"
    content="${content//\{\{$var\}\}/$val}"
  done

  content="${content//\{\{EXP_NAME\}\}/${EXP_NAME}}"
  content="${content//\{\{CONTAINER_IMAGE\}\}/${CONTAINER_IMAGE}}"
  content="${content//\{\{MODEL_PATH\}\}/${MODEL_PATH}}"
  content="${content//\{\{PORT\}\}/${PORT}}"
  content="${content//\{\{OLLAMA_STARTUP_SLEEP\}\}/${OLLAMA_STARTUP_SLEEP}}"
  content="${content//\{\{INSTANCE_NAME_PREFIX\}\}/${INSTANCE_NAME_PREFIX}}"
  content="${content//\{\{CLIENT_PATH\}\}/${client_path}}"

  printf '%s\n' "$content" > "$sbatch_out"
  chmod +x "$sbatch_out"

  echo "Built sbatch: $sbatch_out"
done