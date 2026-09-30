#!/usr/bin/env bash
# Catch the demo up before teaching a module:  bash ~/cymbal/catch_up.sh <module you are about to teach, 2-7>
#   bash ~/cymbal/catch_up.sh 2   -> loads the end of M1 (Start with AI result), version v1-start-with-ai
#   bash ~/cymbal/catch_up.sh 5   -> loads the end of M4 (knowledge added),       version v4-knowledge
# Overwrites the "Cymbal Energy Care" app, saves the version, then you refresh the console. About 1-2 minutes.
# "bash ~/cymbal/catch_up.sh done" loads the finished app (end of M7).
set -euo pipefail
M="${1:?usage: bash catch_up.sh <module you are about to teach: 2-7, or done>}"
[ "$M" = "done" ] && M=8
case "$M" in 2|3|4|5|6|7|8) ;; *) echo "Module must be 2-7 (or done)"; exit 1;; esac
exec bash "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/stages/load_stage.sh" "$((M - 1))"
