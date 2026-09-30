# M3 slide 15: SCRAPI in Cloud Shell. Paste one block at a time.

# 1) Install the pinned version (about 30 seconds; already done if you ran setup step 5)
cd ~/cymbal/03-programmatic
pip install --quiet --user -r requirements.txt && export PATH="$HOME/.local/bin:$PATH"

# 2) The Python API: list apps, list agents, run a scripted two-turn conversation
python3 scrapi_demo.py

# 3) Agent-as-code: pull the whole app into files you can diff, review and commit
cxas pull "Cymbal Energy Care" --target-dir ./cymbal-care --project-id "$(gcloud config get-value project)" --location us
find ./cymbal-care -type f | head -40

# 4) Optional: lint the pulled agent (structure, schemas, instructions)
cxas lint --app-dir ./cymbal-care
