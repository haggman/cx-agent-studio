#!/usr/bin/env bash
# Create the two M4 data stores with the Discovery Engine API (us multi-region) and import their files once:
#   cymbal-policies  unstructured, the 3 policy PDFs        cymbal-faq  FAQ, question/answer CSV
# Safe to run any number of times: it creates only what's missing and never re-imports a store that already has
# documents or an import in progress. Needs the bucket loaded first (setup/cloudshell_setup.sh; setup.sh does both).
set -euo pipefail
export PATH="$HOME/.local/bin:$PATH"
python3 "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/stage_helpers.py" ensure-datastores
