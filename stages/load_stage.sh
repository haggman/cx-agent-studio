#!/usr/bin/env bash
# Load Cymbal Energy Care as it should look at the END of a module, and save the matching version.
#   bash ~/cx-agent-studio/stages/load_stage.sh 3        # end of M3 -> ready for the M4 demos
# (Easier to remember: bash ~/cx-agent-studio/catch_up.sh 4  = "get me ready to teach module 4".)
# It overwrites the app named "Cymbal Energy Care" (creating it if missing) with stages/m<N>-end,
# using `cxas push --overwrite` and then SCRAPI Versions.create_version (cxas-scrapi 1.9.1).
# Safe in a brand-new Cloud Shell and safe to re-run: it enables the APIs and installs SCRAPI itself, from stage 3 on
# it creates the bucket and the two data stores only if they are missing, and it saves each version name only once.
set -euo pipefail
N="${1:?usage: bash load_stage.sh <1-7>}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PACK="$(cd "$HERE/.." && pwd)"
export PATH="$HOME/.local/bin:$PATH"
PROJECT_ID="$(gcloud config get-value project 2>/dev/null)"
[ -n "$PROJECT_ID" ] || { echo "No project set. Run: gcloud config set project <class-project-id>"; exit 1; }
VERSIONS=(unused v1-start-with-ai v2-multi-agent v3-day1 v4-knowledge v5-evaluated v6-escalation v7-launch-ready)
VERSION="${VERSIONS[$N]:?stage must be 1-7}"
SRC="$HERE/m${N}-end"
[ -d "$SRC" ] || { echo "No stage folder $SRC"; exit 1; }
trap 'echo; echo "load_stage.sh $N stopped (line $LINENO). Copy everything above this line when asking for help."' ERR

echo "== Project $PROJECT_ID: APIs (a few seconds when already on)"
gcloud services enable ces.googleapis.com discoveryengine.googleapis.com dlp.googleapis.com --quiet

WANT="$(sed -n 's/^cxas-scrapi==//p' "$PACK/03-programmatic/requirements.txt")"
HAVE="$(python3 -m pip show cxas-scrapi 2>/dev/null | sed -n 's/^Version: //p')"
if [ "$HAVE" != "$WANT" ] || ! command -v cxas >/dev/null; then
  echo "== Installing SCRAPI (cxas-scrapi $WANT, about a minute the first time)"
  python3 -m pip install --quiet --user --disable-pip-version-check -r "$PACK/03-programmatic/requirements.txt"
fi
echo "   cxas-scrapi $(python3 -m pip show cxas-scrapi 2>/dev/null | sed -n 's/^Version: //p')"

WORK="$(mktemp -d)/cymbal_energy_care"
cp -r "$SRC" "$WORK"
FILL=("PROJECT_ID=$PROJECT_ID")

if [ "$N" -ge 3 ]; then  # from the end of M3 on, the app carries the data store tools (pre-built for the M4 demo)
  echo "== Bucket and data stores (only creates what's missing)"
  (cd "$PACK" && bash setup/cloudshell_setup.sh | grep -v "^   project")
  python3 "$HERE/stage_helpers.py" ensure-datastores
  eval "$(python3 "$HERE/stage_helpers.py" datastores)"
  if [ -z "${POLICIES:-}" ] || [ -z "${FAQ:-}" ]; then
    echo "Couldn't find the two data stores. Name them explicitly:"
    echo "  POLICIES_DATASTORE=projects/.../dataStores/ID FAQ_DATASTORE=projects/.../dataStores/ID bash $0 $N"
    exit 1
  fi
  echo "   policies: $POLICIES"; echo "   faq:      $FAQ"
  FILL+=("POLICIES_DATASTORE=$POLICIES" "FAQ_DATASTORE=$FAQ")
fi

if [ "$N" -ge 7 ]; then
  echo "== Redaction templates (only creates what's missing)"
  python3 "$HERE/stage_helpers.py" ensure-dlp
fi

python3 "$HERE/stage_helpers.py" fill "$WORK" "${FILL[@]}"

APP="$(python3 "$HERE/stage_helpers.py" find-app)"
echo "== Pushing stage $N (m${N}-end)"
if [ -n "$APP" ]; then
  cxas push --app-dir "$WORK" --to "$APP" --project-id "$PROJECT_ID" --location us --overwrite
else
  cxas push --app-dir "$WORK" --display-name "Cymbal Energy Care" --project-id "$PROJECT_ID" --location us
  APP="$(python3 "$HERE/stage_helpers.py" find-app)"
fi
# One version per name and stage content: reruns skip it, stage files changed since last time replace it,
# and a version you saved yourself in class is kept.
HASH="$(cd "$SRC" && find . -type f | LC_ALL=C sort | xargs cat | sha256sum | cut -c1-8)"
python3 "$HERE/stage_helpers.py" save-version "$APP" "$VERSION" "$HASH" "m${N}-end"

if [ "$N" -ge 6 ]; then
  echo "== Web widget channel cymbal-web -> $VERSION"
  python3 "$HERE/stage_helpers.py" web-channel "$APP" "$VERSION" || echo "   (channel step failed: create it in Deploy > New channel, M6 block 21)"
fi
echo
echo "Done: $APP is at the end of module $N (version $VERSION). In the console: refresh, then Preview > Start new conversation."
