#!/usr/bin/env bash
# M6 slides 17-18: talk to the deployed agent over the API (runSession). Run in Cloud Shell.
# Fill in APP_ID and DEPLOYMENT_ID from the console (Deploy > your channel shows the full deployment name).
#   bash api_demo.sh APP_ID DEPLOYMENT_ID            (two turns: greeting, verified outage check)
#   bash api_demo.sh APP_ID DEPLOYMENT_ID escalate   (adds a third turn asking for a person; M6 slide 41)
set -euo pipefail
PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
LOCATION=us
APP_ID=${1:?usage: bash api_demo.sh APP_ID DEPLOYMENT_ID}
DEPLOYMENT_ID=${2:?usage: bash api_demo.sh APP_ID DEPLOYMENT_ID}
SESSION_ID="api-demo-$(date +%H%M%S)"
APP="projects/${PROJECT_ID}/locations/${LOCATION}/apps/${APP_ID}"
URL="https://ces.googleapis.com/v1/${APP}/sessions/${SESSION_ID}:runSession"

say() {
  echo; echo "USER:  $1"
  curl -s -X POST \
    -H "Authorization: Bearer $(gcloud auth print-access-token)" \
    -H "Content-Type: application/json; charset=utf-8" \
    -d "{\"config\":{\"session\":\"${APP}/sessions/${SESSION_ID}\",\"deployment\":\"${APP}/deployments/${DEPLOYMENT_ID}\"},\"inputs\":[{\"text\":\"$1\"}]}" \
    "${URL}" | tee "/tmp/${SESSION_ID}-last.json" \
    | jq -r '.outputs[]? | (.text // empty), (if .endSession then "END SESSION: " + (.endSession|tostring) else empty end)' \
    | sed 's/^/AGENT: /'
}

say "Hi"
say "My account is 100234 and my ZIP is 39567. Is my power out?"
if [[ "${3:-}" == "escalate" ]]; then say "I want to talk to a real person."; fi
echo; echo "Full JSON of the last turn: /tmp/${SESSION_ID}-last.json"
