"""SCRAPI tour of the Cymbal Energy app (M3 slide 15). Run in Cloud Shell from this folder:
     pip install --quiet --user -r requirements.txt
     python3 scrapi_demo.py
Written against cxas-scrapi 1.9.1 (see requirements.txt).
"""
import subprocess
import warnings

# SCRAPI pulls in pydub for audio sessions; we only use text, so silence its "no ffmpeg" warning.
warnings.filterwarnings("ignore", message=".*ffmpeg.*")

from cxas_scrapi import Apps, Agents, Tools, Sessions  # noqa: E402

PROJECT = subprocess.run(["gcloud", "config", "get-value", "project"], capture_output=True, text=True).stdout.strip()
LOCATION = "us"
APP_DISPLAY_NAME = "Cymbal Energy Care"

print(f"\n== 1. Apps in {PROJECT} / {LOCATION}")
apps = Apps(project_id=PROJECT, location=LOCATION)
for name, display in apps.get_apps_map().items():
    print(f"   {display}  ->  {name}")
app = apps.get_app_by_display_name(APP_DISPLAY_NAME)
if app is None:
    raise SystemExit(f"No app named '{APP_DISPLAY_NAME}' in {PROJECT}/{LOCATION}")

print(f"\n== 2. Agents in {APP_DISPLAY_NAME}")
for agent in Agents(app_name=app.name).list_agents():
    print(f"   {agent.display_name}")

print(f"\n== 3. Tools in {APP_DISPLAY_NAME}")
for name, display in Tools(app_name=app.name).get_tools_map().items():
    print(f"   {display}")

print("\n== 4. A scripted conversation against the draft (this is how you unit-test an agent from CI)")
sessions = Sessions(app_name=app.name)
session_id = sessions.create_session_id()
for turn in ["Hi, is there a power outage in 39567?",
             "How long has it been out?"]:
    print()
    sessions.parse_result(sessions.run(session_id=session_id, text=turn))
