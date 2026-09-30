#!/usr/bin/env bash
# Rebuild everything generated in this repo from src/ (run from anywhere):
#   the module folders' source documents (PDFs, FAQ CSV, metadata), stages/m1-end ... m7-end,
#   docs/ teleprompter (Word + Markdown) and planning guide, and the Cloud Shell zip.
# Needs: python3 + reportlab (requirements-dev.txt), node + docx (npm install).
set -euo pipefail
cd "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/.."
python3 src/make_docs.py
python3 src/make_stages.py
node src/teleprompter.js "docs/TELEPROMPTER - CX Agent Studio - Cymbal Energy.docx"
node src/teleprompter_md.js docs/TELEPROMPTER.md
node src/guide.js "docs/PLANNING GUIDE - CX Agent Studio - Cymbal Energy.docx"
find . -name __pycache__ -prune -exec rm -rf {} +
rm -f cymbal-energy-demo-pack.zip
# the zip holds exactly what Cloud Shell needs at ~/cx-agent-studio (no docs/, src/ or repo files)
zip -qr cymbal-energy-demo-pack.zip setup.sh catch_up.sh setup 0*-* stages -x '*.DS_Store' '*/__pycache__/*'
echo "built: module folders, stages/, docs/, cymbal-energy-demo-pack.zip"
