#!/usr/bin/env bash
# M7 slides 29-30: the Sensitive Data Protection templates used for redaction, in "us" and "global".
# Safe to run any number of times: it only creates templates that don't exist yet.
set -euo pipefail
PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
python3 "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/../stages/stage_helpers.py" ensure-dlp
echo
echo "Paste these into Settings > Advanced > Logging > Enable redaction (use the location the page accepts):"
echo "  Inspect:     projects/${PROJECT_ID}/locations/us/inspectTemplates/cymbal-inspect"
echo "  De-identify: projects/${PROJECT_ID}/locations/us/deidentifyTemplates/cymbal-deidentify"
