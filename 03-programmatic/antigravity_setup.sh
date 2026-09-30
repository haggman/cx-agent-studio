#!/usr/bin/env bash
# M3 slides 22-24: Antigravity CLI (agy) + the CX Agent Studio MCP server + the CXAS agent skills, in Cloud Shell.
# Run once per project (tonight), from anywhere:   bash ~/cymbal/03-programmatic/antigravity_setup.sh
# Checked Sep 27, 2026 against: CX Agent Studio MCP docs (endpoint https://ces.googleapis.com/mcp, scope .../auth/ces,
# enabled with the ces API), Antigravity CLI docs (serverUrl + authProviderType, ~/.gemini/config/mcp_config.json,
# workspace skills in .agents/skills), and cxas-scrapi 1.9.1 (`cxas init` installs skills into .agents/skills).
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
export PATH="$HOME/.local/bin:$PATH"

echo "== 1. Antigravity CLI"
command -v agy >/dev/null || { echo "agy not found: curl -fsSL https://antigravity.google/cli/install.sh | bash"; exit 1; }
agy --version 2>/dev/null || true

echo "== 2. Park Cloud Shell's preinstalled Vertex plugin if an earlier import brought it in (its MCP server crashes on start)"
if [ -d ~/.gemini/antigravity-cli/plugins/vertex ]; then
  mv ~/.gemini/antigravity-cli/plugins/vertex ~/vertex-plugin-disabled-$(date +%s) && echo "   moved vertex plugin out of the way"
else
  echo "   no vertex plugin: nothing to do"
fi

echo "== 3. Make sure Antigravity can reach the CX Agent Studio MCP server"
if grep -rqs "ces.googleapis.com/mcp" ~/.gemini/antigravity-cli/plugins; then
  echo "   already provided by an imported plugin: $(grep -rls 'ces.googleapis.com/mcp' ~/.gemini/antigravity-cli/plugins | head -1)"
else
  python3 - "$PROJECT_ID" <<'PY'
import json, os, sys, time
path = os.path.expanduser("~/.gemini/config/mcp_config.json")
os.makedirs(os.path.dirname(path), exist_ok=True)
cfg = {}
if os.path.exists(path):
    raw = open(path).read().strip()
    if raw:
        try:
            cfg = json.loads(raw)
        except ValueError:
            backup = path + ".bad-" + str(int(time.time()))
            os.rename(path, backup)
            print("   existing mcp_config.json was not valid JSON; saved it as", backup)
servers = cfg.setdefault("mcpServers", {})
if any("ces.googleapis.com/mcp" in json.dumps(v) for v in servers.values()):
    print("   already in", path)
else:
    servers["cx-agent-studio"] = {
        "serverUrl": "https://ces.googleapis.com/mcp",
        "authProviderType": "google_credentials",
        "headers": {"x-goog-user-project": sys.argv[1]},
    }
    json.dump(cfg, open(path, "w"), indent=2)
    print("   added cx-agent-studio to", path)
PY
fi

echo "== 4. CXAS agent skills in their own workspace (Antigravity reads .agents/skills in the folder you start agy in)"
mkdir -p ~/cymbal-skills && cd ~/cymbal-skills
pip install --quiet --user -r "$HERE/requirements.txt" uv
# `cxas init` looks for its bundled skills under sys.prefix (/usr/share/...), but a --user install puts them in
# ~/.local/share/cxas-scrapi/skills, so copy them from there (same files cxas init would copy).
SKILLS_SRC="$(python3 -c 'import site; print(site.USER_BASE)')/share/cxas-scrapi/skills"
if [ -d "$SKILLS_SRC" ]; then
  cp -r "$SKILLS_SRC/." ~/cymbal-skills/ && echo "   copied CXAS skills from $SKILLS_SRC"
else
  cxas init --force || echo "   could not find the bundled skills; see the planning guide section 6"
fi
APP_NAME=$(python3 - <<'PY' 2>/dev/null
import subprocess, warnings
warnings.filterwarnings("ignore")
from cxas_scrapi import Apps
p = subprocess.run(["gcloud", "config", "get-value", "project"], capture_output=True, text=True).stdout.strip()
a = Apps(project_id=p, location="us").get_app_by_display_name("Cymbal Energy Care")
print(a.name if a else "")
PY
)
if [ -n "$APP_NAME" ]; then DEPLOYED="\"$APP_NAME\""; else DEPLOYED=null; fi
cat > gecx-config.json <<JSON
{
  "gcp_project_id": "${PROJECT_ID}",
  "location": "us",
  "app_name": "Cymbal Energy Care",
  "deployed_app_id": ${DEPLOYED},
  "model": "gemini-3.5-flash",
  "modality": "text"
}
JSON
echo "   skills:"; ls .agents/skills
echo "   gecx-config.json:"; cat gecx-config.json

echo
echo "Done. For the demo:  cd ~/cymbal/03-programmatic && agy        (MCP only, no skills: keeps the demo predictable)"
echo "Optional skills:     cd ~/cymbal-skills && agy                   (adds /cxas-agent-foundry and the other CXAS skills)"
echo "First agy launch in Cloud Shell prints a sign-in URL: open it, sign in, paste the code back."
