#!/usr/bin/env bash
set -euo pipefail

command -v codex >/dev/null
codex login status
