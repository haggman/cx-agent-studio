#!/usr/bin/env bash
# Build every restore point in order: v1 ... v7 on the app "Cymbal Energy Care".
# After this, the teleprompter's reset boxes ("Versions > vN > Restore") all work.
# Stages 4-7 need the two data stores; load_stage.sh creates them if missing.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
for N in 1 2 3 4 5 6 7; do
  echo; echo "################ stage $N"
  bash "$HERE/load_stage.sh" "$N" || { echo "Stopped at stage $N (see the message above). Earlier versions are saved."; exit 1; }
done
echo; echo "All seven versions saved. The app is left at the end of module 7; restore any vN from Versions."
