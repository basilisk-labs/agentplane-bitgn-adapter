#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

existing_BITGN_HOST="${BITGN_HOST-}"
existing_BENCHMARK_ID="${BENCHMARK_ID-}"
existing_BENCH_ID="${BENCH_ID-}"
existing_BITGN_RUNTIME="${BITGN_RUNTIME-}"
existing_BITGN_API_KEY="${BITGN_API_KEY-}"
existing_MODEL_ID="${MODEL_ID-}"
has_BITGN_HOST=0; [ "${BITGN_HOST+x}" ] && has_BITGN_HOST=1
has_BENCHMARK_ID=0; [ "${BENCHMARK_ID+x}" ] && has_BENCHMARK_ID=1
has_BENCH_ID=0; [ "${BENCH_ID+x}" ] && has_BENCH_ID=1
has_BITGN_RUNTIME=0; [ "${BITGN_RUNTIME+x}" ] && has_BITGN_RUNTIME=1
has_BITGN_API_KEY=0; [ "${BITGN_API_KEY+x}" ] && has_BITGN_API_KEY=1
has_MODEL_ID=0; [ "${MODEL_ID+x}" ] && has_MODEL_ID=1

for env_file in ".env" ".env.local"; do
  if [ -f "$env_file" ]; then
    set -a
    # shellcheck disable=SC1090
    source "$env_file"
    set +a
  fi
done

if [ "$has_BITGN_HOST" -eq 1 ]; then export BITGN_HOST="$existing_BITGN_HOST"; fi
if [ "$has_BENCHMARK_ID" -eq 1 ]; then export BENCHMARK_ID="$existing_BENCHMARK_ID"; fi
if [ "$has_BENCH_ID" -eq 1 ]; then export BENCH_ID="$existing_BENCH_ID"; fi
if [ "$has_BITGN_RUNTIME" -eq 1 ]; then export BITGN_RUNTIME="$existing_BITGN_RUNTIME"; fi
if [ "$has_BITGN_API_KEY" -eq 1 ]; then export BITGN_API_KEY="$existing_BITGN_API_KEY"; fi
if [ "$has_MODEL_ID" -eq 1 ]; then export MODEL_ID="$existing_MODEL_ID"; fi

uv run agentplane-bitgn "$@"
