#!/usr/bin/env bash
# Cymbal Energy demo: EVERYTHING that isn't a lesson, in one command. Run in Cloud Shell after unzipping the pack:
#   unzip -o ~/cymbal-energy-demo-pack.zip -d ~/cymbal && bash ~/cymbal/setup.sh
# Safe to run any number of times (tonight, again in the morning, after a Cloud Shell reset): every step checks
# first and only creates what's missing. Lines start with ✓ (already there) or + (created now).
set -euo pipefail
PACK="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export PATH="$HOME/.local/bin:$PATH"
PROJECT_ID="$(gcloud config get-value project 2>/dev/null)"
[ -n "$PROJECT_ID" ] || { echo "No project set. Run: gcloud config set project <class-project-id>"; exit 1; }
trap 'echo; echo "setup.sh stopped (line $LINENO). Fix what the message above says and run it again: finished steps are skipped."' ERR

echo "== 1/6 APIs and bucket"
bash "$PACK/setup/cloudshell_setup.sh"

echo "== 2/6 SCRAPI"
WANT="$(sed -n 's/^cxas-scrapi==//p' "$PACK/03-programmatic/requirements.txt")"
HAVE="$(python3 -m pip show cxas-scrapi 2>/dev/null | sed -n 's/^Version: //p')"
if [ "$HAVE" = "$WANT" ] && command -v cxas >/dev/null; then
  echo "   ✓ cxas-scrapi $HAVE"
else
  python3 -m pip install --quiet --user --disable-pip-version-check -r "$PACK/03-programmatic/requirements.txt"
  echo "   + cxas-scrapi $WANT installed"
fi

echo "== 3/6 M4 data stores (pre-built so the M4 demo never waits on indexing)"
python3 "$PACK/stages/stage_helpers.py" ensure-datastores

echo "== 4/6 M7 redaction templates"
python3 "$PACK/stages/stage_helpers.py" ensure-dlp

echo "== 5/6 M3 Antigravity CLI: CX Agent Studio MCP server + CXAS skills"
if command -v agy >/dev/null; then
  bash "$PACK/03-programmatic/antigravity_setup.sh" 2>&1 | sed 's/^/   /' || echo "   (Antigravity step reported a problem; the M3 demo can skip it)"
else
  echo "   agy not installed in this Cloud Shell: skipped (M3 block 12 is optional)"
fi

echo "== 6/6 The app"
APP="$(python3 "$PACK/stages/stage_helpers.py" find-app)"
if [ -n "$APP" ]; then echo "   ✓ \"Cymbal Energy Care\" exists: $APP"; else echo "   (no \"Cymbal Energy Care\" app yet: M1 creates it live, or run: bash ~/cymbal/catch_up.sh 2)"; fi

echo
echo "Setup complete. Between modules:  bash ~/cymbal/catch_up.sh <module you are about to teach>"
