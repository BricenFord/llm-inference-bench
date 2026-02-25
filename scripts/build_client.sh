#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

source config/base.config

for exp in config/experiments/*.config; do
  echo "Processing experiment: $exp"
  source "$exp"

  : "${EXP_NAME:?EXP_NAME not set in $exp}"
  : "${ENGINE:?ENGINE not set in $exp}"

  ENGINE_CONFIG="config/engines/${ENGINE}.config"
  CLIENT_TEMPLATE="templates/client.${ENGINE}.py.template"

  [ -f "$ENGINE_CONFIG" ] || { echo "Missing engine config: $ENGINE_CONFIG" >&2; exit 1; }
  [ -f "$CLIENT_TEMPLATE" ] || { echo "Missing client template: $CLIENT_TEMPLATE" >&2; exit 1; }

  source "$ENGINE_CONFIG"

  out_dir="generated/sbatch/${ENGINE}/${EXP_NAME}"
  mkdir -p "$out_dir"

  client_out="${out_dir}/${EXP_NAME}.client.py"

  content="$(cat "$CLIENT_TEMPLATE")"
  content="${content//\{\{HOST\}\}/${HOST}}"
  content="${content//\{\{MODEL_NAME\}\}/${MODEL_NAME}}"
  content="${content//\{\{CSV_FILE\}\}/${CSV_FILE}}"
  content="${content//\{\{TIMEOUT_S\}\}/${TIMEOUT_S}}"
  content="${content//\{\{LOG_QA\}\}/${LOG_QUESTION_AND_ANSWER}}"
  content="${content//\{\{MAX_QUESTIONS\}\}/${MAX_QUESTIONS}}"

  printf '%s\n' "$content" > "$client_out"
  chmod +x "$client_out"

  echo "Built client: $client_out"
done