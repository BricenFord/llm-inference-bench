#!/usr/bin/env bash
set -euo pipefail

TEMPLATE="templates/sbatch.template"
OUT_DIR="generated/sbatch/ollama"

# Load private configs
source "secrets/base.config"
source "secrets/ollama.config"

# Required variables check
: "${PARTITION:?}"
: "${CPUS_PER_TASK:?}"
: "${MEM:?}"
: "${TIME:?}"
: "${MAIL_USER:?}"
: "${MAIL_TYPE:?}"
: "${MODULE_CUDA:?}"
: "${MODULE_PYTHON:?}"

: "${JOB_NAME:?}"
: "${CONTAINER_IMAGE:?}"
: "${MODEL_PATH:?}"
: "${PORT:?}"
: "${OLLAMA_STARTUP_SLEEP:?}"
: "${CLIENT_SCRIPT:?}"

mkdir -p "${OUT_DIR}"
mkdir -p "results/runs"

OUT_FILE="${OUT_DIR}/${JOB_NAME}.sbatch"

render() {
  local content
  content="$(cat "$TEMPLATE")"

  keys=(
    PARTITION CPUS_PER_TASK MEM TIME MAIL_USER MAIL_TYPE MODULE_CUDA MODULE_PYTHON
    JOB_NAME CONTAINER_IMAGE MODEL_PATH PORT OLLAMA_STARTUP_SLEEP CLIENT_SCRIPT
  )

  for k in "${keys[@]}"; do
    v="${!k}"
    v="${v//\\/\\\\}"
    v="${v//&/\\&}"
    v="${v//\//\\/}"
    content="$(printf '%s' "$content" | sed "s/{{${k}}}/${v}/g")"
  done

  printf '%s\n' "$content" > "$OUT_FILE"
}

render
chmod +x "$OUT_FILE"

echo "Built: $OUT_FILE"