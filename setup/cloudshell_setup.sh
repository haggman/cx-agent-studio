#!/usr/bin/env bash
# Cymbal Energy demo: APIs + bucket. Normally run for you by ~/cymbal/setup.sh.
# Safe to run any number of times: enabling an enabled API is a no-op, the bucket is created only if missing,
# and the copy just refreshes the same five files.
set -euo pipefail
cd "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/.."
PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
BUCKET="gs://${PROJECT_ID}-cymbal-energy"
echo "   project ${PROJECT_ID}   bucket ${BUCKET}"

gcloud services enable ces.googleapis.com discoveryengine.googleapis.com dlp.googleapis.com --quiet

if gcloud storage buckets describe "${BUCKET}" >/dev/null 2>&1; then
  echo "   ✓ bucket exists"
else
  gcloud storage buckets create "${BUCKET}" --location=us --quiet && echo "   + bucket created"
fi
gcloud storage cp --quiet 04-knowledge/policies/*.pdf "${BUCKET}/cymbal-energy/policies/"
gcloud storage cp --quiet 04-knowledge/faq/cymbal_energy_faq.csv "${BUCKET}/cymbal-energy/faq/"
sed "s#gs://BUCKET#${BUCKET}#g" 04-knowledge/metadata/policies_metadata.jsonl > /tmp/policies_metadata.jsonl
gcloud storage cp --quiet /tmp/policies_metadata.jsonl "${BUCKET}/cymbal-energy/metadata/"
echo "   ✓ $(gcloud storage ls -r "${BUCKET}/cymbal-energy/" | grep -c '[^/]$') files in ${BUCKET}/cymbal-energy/"
