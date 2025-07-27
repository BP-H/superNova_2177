#!/usr/bin/env bash
set -euo pipefail

if command -v pipx >/dev/null 2>&1; then
    pipx install supernova-2177
else
    pip install supernova-2177
fi

