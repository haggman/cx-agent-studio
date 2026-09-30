"""Helpers for load_stage.sh (Cymbal Energy Care stages). Written against cxas-scrapi 1.9.1.
   python3 stage_helpers.py find-app                         -> prints the app resource name (or nothing)
   python3 stage_helpers.py datastores                       -> prints POLICIES=<name> and FAQ=<name> (or nothing found)
   python3 stage_helpers.py fill <dir> KEY=VALUE ...         -> replaces __KEY__ placeholders in every file under <dir>
   python3 stage_helpers.py web-channel <app> <version-name> -> creates/updates the cymbal-web web widget channel
   python3 stage_helpers.py save-version <app> <name> <hash> -> saves the version once per stage content (see save_version)
   python3 stage_helpers.py ensure-datastores                -> creates cymbal-policies / cymbal-faq and imports once
   python3 stage_helpers.py ensure-dlp                       -> creates the cymbal-inspect / cymbal-deidentify templates
Every ensure-* command checks first and only creates what is missing, so it is safe to run any number of times.
"""
import json, os, subprocess, sys, urllib.error, urllib.request, warnings

warnings.filterwarnings("ignore")
LOCATION = "us"
APP_DISPLAY_NAME = "Cymbal Energy Care"


def project():
    return subprocess.run(["gcloud", "config", "get-value", "project"], capture_output=True, text=True).stdout.strip()


def token():
    return subprocess.run(["gcloud", "auth", "print-access-token"], capture_output=True, text=True).stdout.strip()


def find_app():
    from cxas_scrapi import Apps
    app = Apps(project_id=project(), location=LOCATION).get_app_by_display_name(APP_DISPLAY_NAME)
    print(app.name if app else "")


def list_datastores():
    p, t, found = project(), token(), []
    for loc, host in (("us", "us-discoveryengine.googleapis.com"), ("global", "discoveryengine.googleapis.com")):
        url = f"https://{host}/v1/projects/{p}/locations/{loc}/collections/default_collection/dataStores?pageSize=100"
        req = urllib.request.Request(url, headers={"Authorization": f"Bearer {t}", "x-goog-user-project": p})
        try:
            data = json.load(urllib.request.urlopen(req, timeout=30))
        except Exception:
            continue
        found += data.get("dataStores", [])
    return found


def datastores():
    stores = list_datastores()
    exact = lambda i: next((d["name"] for d in stores if d["name"].endswith("/dataStores/" + i)), "")
    # anything else that looks right (e.g. the dry run's), but never the one made during the M4 cooking-show demo
    pick = lambda words: next((d["name"] for d in stores if "live" not in (d.get("displayName", "") + d["name"]).lower()
                               and any(w in (d.get("displayName", "") + d["name"]).lower() for w in words)), "")
    pol = os.environ.get("POLICIES_DATASTORE") or exact("cymbal-policies") or pick(["polic"])
    faq = os.environ.get("FAQ_DATASTORE") or exact("cymbal-faq") or pick(["faq"])
    print(f"POLICIES={pol}")
    print(f"FAQ={faq}")
    if not (pol and faq):
        print("# data stores found in this project:", file=sys.stderr)
        for d in stores:
            print(f"#   {d.get('displayName')}  ->  {d['name']}", file=sys.stderr)


def fill(root, pairs):
    subs = dict(p.split("=", 1) for p in pairs)
    for dirpath, _, files in os.walk(root):
        for fn in files:
            path = os.path.join(dirpath, fn)
            text = open(path).read()
            new = text
            for k, v in subs.items():
                new = new.replace(f"__{k}__", v)
            if new != text:
                open(path, "w").write(new)


def web_channel(app_name, version_display_name):
    from cxas_scrapi import Deployments, Versions
    versions = Versions(app_name=app_name)
    match = [v for v in versions.list_versions() if v.display_name == version_display_name]
    if not match:
        sys.exit(f"version {version_display_name} not found")
    version = sorted(match, key=lambda v: v.create_time)[-1].name
    deps = Deployments(app_name=app_name)
    existing = {d.display_name: d for d in deps.list_deployments()}
    if "cymbal-web" in existing:
        dep_id = existing["cymbal-web"].name.split("/")[-1]
        d = deps.update_deployment(dep_id, app_version=version)
    else:
        d = deps.create_deployment(deployment_id="cymbal-web", display_name="cymbal-web", app_version=version,
                                   channel_type="WEB_UI", modality="CHAT_ONLY", theme="LIGHT",
                                   web_widget_title="Cymbal Energy virtual assistant")
    print(d.name)


# ---------------------------------------------------------------- idempotent infrastructure
def rest(method, url, body=None, ok404=False, quiet=False):
    p = project()
    req = urllib.request.Request(url, method=method, data=json.dumps(body).encode() if body is not None else None,
                                 headers={"Authorization": f"Bearer {token()}", "Content-Type": "application/json",
                                          "x-goog-user-project": p})
    try:
        return json.load(urllib.request.urlopen(req, timeout=60))
    except urllib.error.HTTPError as e:
        if (ok404 and e.code == 404) or quiet:
            return None
        raise SystemExit(f"{method} {url} -> HTTP {e.code}: {e.read().decode()[:500]}")


DE = "https://us-discoveryengine.googleapis.com/v1/projects/{p}/locations/us/collections/default_collection/dataStores"
STORES = [  # id, contentConfig, source (relative to the bucket), import dataSchema, extra import options
    ("cymbal-policies", "CONTENT_REQUIRED", "cymbal-energy/policies/*.pdf", "content", {"reconciliationMode": "INCREMENTAL"}),
    # CSV rows carry no document ID: without autoGenerateIds every row fails with "Custom Document Id (_id) was not found".
    # FULL reconciliation is what the API recommends with generated IDs (a re-import replaces instead of duplicating).
    ("cymbal-faq", "NO_CONTENT", "cymbal-energy/faq/cymbal_energy_faq.csv", "csv", {"reconciliationMode": "FULL", "autoGenerateIds": True}),
]


def ensure_datastores():
    import time
    p = project()
    base = DE.format(p=p)
    for ds_id, content, src, schema, options in STORES:
        url = f"{base}/{ds_id}"
        if rest("GET", url, ok404=True):
            print(f"   ✓ data store {ds_id} exists")
        else:
            rest("POST", f"{base}?dataStoreId={ds_id}", {"displayName": ds_id, "industryVertical": "GENERIC",
                                                         "solutionTypes": ["SOLUTION_TYPE_CHAT"], "contentConfig": content})
            for _ in range(30):
                if rest("GET", url, ok404=True):
                    break
                time.sleep(5)
            print(f"   + data store {ds_id} created")
        branch = f"{url}/branches/default_branch"
        docs = rest("GET", f"{branch}/documents?pageSize=1", ok404=True) or {}
        ops = rest("GET", f"{branch}/operations", quiet=True) or {}  # best effort: only used to avoid a double import
        running = [o for o in ops.get("operations", []) if not o.get("done")]
        if docs.get("documents"):
            print(f"   ✓ {ds_id} already has documents (no re-import)")
        elif running:
            print(f"   ✓ {ds_id} import already running (no re-import)")
        else:
            rest("POST", f"{branch}/documents:import", {
                "gcsSource": {"inputUris": [f"gs://{p}-cymbal-energy/{src}"], "dataSchema": schema}, **options})
            print(f"   + {ds_id} import started (indexing takes about 15 minutes; a store whose last import failed is retried here)")


DLP = "https://dlp.googleapis.com/v2/projects/{p}/locations/{loc}"
TEMPLATES = [
    ("inspectTemplates", "cymbal-inspect", "inspectTemplate", {"displayName": "Cymbal: find cards, SSNs, phones",
        "inspectConfig": {"infoTypes": [{"name": "CREDIT_CARD_NUMBER"}, {"name": "US_SOCIAL_SECURITY_NUMBER"}, {"name": "PHONE_NUMBER"}]}}),
    ("deidentifyTemplates", "cymbal-deidentify", "deidentifyTemplate", {"displayName": "Cymbal: replace with infoType name",
        "deidentifyConfig": {"infoTypeTransformations": {"transformations": [{"primitiveTransformation": {"replaceWithInfoTypeConfig": {}}}]}}}),
]


def ensure_dlp():
    p = project()
    for loc in ("us", "global"):
        for kind, tid, field, body in TEMPLATES:
            url = f"{DLP.format(p=p, loc=loc)}/{kind}"
            if rest("GET", f"{url}/{tid}", ok404=True):
                print(f"   ✓ {loc}/{tid} exists")
            else:
                rest("POST", url, {"templateId": tid, field: body})
                print(f"   + {loc}/{tid} created")


def save_version(app_name, display_name, content_hash, stage):
    """One version per name and stage content. Same name + same content hash: nothing to do. A version this loader
    saved from older stage files (different hash): replaced. A version you saved yourself in class: kept."""
    from cxas_scrapi import Versions
    ours = "Loaded by load_stage.sh"
    versions = Versions(app_name=app_name)
    same = [v for v in versions.list_versions() if v.display_name == display_name]
    if any(("#" + content_hash) in (v.description or "") for v in same):
        print(f"   ✓ version {display_name} already saved from these stage files")
        return
    for v in [v for v in same if (v.description or "").startswith(ours)]:
        try:
            versions.delete_version(v.name.split("/")[-1])
            print(f"   - removed {display_name} saved from older stage files")
            same.remove(v)
        except Exception as e:  # e.g. still used by a deployment: keep it, the new one is newer
            print(f"   (kept older {display_name}: {str(e)[:120]})")
            same.remove(v)
    if same:
        print(f"   ✓ keeping the {display_name} you saved in class (not replaced)")
        return
    v = versions.create_version(display_name=display_name, description=f"{ours} from stages/{stage} #{content_hash}")
    print(f"   + version {display_name} saved: {v.name}")


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "find-app":
        find_app()
    elif cmd == "datastores":
        datastores()
    elif cmd == "fill":
        fill(sys.argv[2], sys.argv[3:])
    elif cmd == "web-channel":
        web_channel(sys.argv[2], sys.argv[3])
    elif cmd == "save-version":
        save_version(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
    elif cmd == "ensure-datastores":
        ensure_datastores()
    elif cmd == "ensure-dlp":
        ensure_dlp()
    else:
        sys.exit(f"unknown command {cmd}")
