import os
import hashlib
import json
import configparser
from difflib import SequenceMatcher
from urllib.request import urlopen
import subprocess
from config_utils import get_tables_path, get_vpxtool_path
from utils import logger
import re

INDEX_FILE = os.path.expanduser("~/.vpx_settings_editor/tables_index.ini")
VPS_DB_URL = "https://virtualpinballspreadsheet.github.io/vps-db/db/vpsdb.json"
VPS_LAST_UPDATED_URL = "https://virtualpinballspreadsheet.github.io/vps-db/lastUpdated.json"
LOCAL_DB_FILE = os.path.expanduser("~/.vpx_settings_editor/vpsdb.json")
PATCH_HASHES_URL = "https://raw.githubusercontent.com/jsm174/vpx-standalone-scripts/master/hashes.json"


def compute_sha256(filepath):
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256_hash.update(chunk)
    return sha256_hash.hexdigest()


def fetch_json(url):
    with urlopen(url) as resp:
        return json.loads(resp.read().decode())


def load_patch_hashes():
    """Return a map of script SHA256 to patched file URL."""
    try:
        data = fetch_json(PATCH_HASHES_URL)
    except Exception as e:
        logger.error(f"Failed to fetch patch hashes: {e}")
        return {}

    patches = {}

    if isinstance(data, dict):
        entries = data.values()
    elif isinstance(data, list):
        entries = data
    else:
        entries = []

    for entry in entries:
        if not isinstance(entry, dict):
            continue
        file_info = entry.get("file", {})
        patched_info = entry.get("patched", {})

        sha = None
        if isinstance(file_info, dict):
            sha = file_info.get("sha256")
        elif isinstance(entry.get("sha256"), str):
            sha = entry.get("sha256")

        url = None
        if isinstance(patched_info, dict):
            url = patched_info.get("url")

        if sha and url:
            patches[sha] = url

    return patches


def ensure_vpsdb(existing_ts=None):
    remote_ts = None
    try:
        data = fetch_json(VPS_LAST_UPDATED_URL)
        remote_ts = data.get("lastUpdated", "")
    except Exception as e:
        logger.error(f"Failed to fetch lastUpdated: {e}")

    db_data = None
    if not os.path.exists(LOCAL_DB_FILE) or (remote_ts and remote_ts != existing_ts):
        try:
            db_data = fetch_json(VPS_DB_URL)
            os.makedirs(os.path.dirname(LOCAL_DB_FILE), exist_ok=True)
            with open(LOCAL_DB_FILE, "w", encoding="utf-8") as f:
                json.dump(db_data, f)
            existing_ts = remote_ts or existing_ts
        except Exception as e:
            logger.error(f"Failed to download VPS DB: {e}")
    if db_data is None and os.path.exists(LOCAL_DB_FILE):
        with open(LOCAL_DB_FILE, "r", encoding="utf-8") as f:
            db_data = json.load(f)
    return db_data or [], existing_ts


def find_vps_id(name, db_entries, threshold=0.85):
    best_ratio = 0.0
    best_id = None
    base = os.path.splitext(name)[0]
    for entry in db_entries:
        entry_name = str(entry.get("name", ""))
        ratio = SequenceMatcher(None, base.lower(), entry_name.lower()).ratio()
        if ratio > best_ratio:
            best_ratio = ratio
            best_id = entry.get("id")
    if best_ratio >= threshold:
        return str(best_id)
    return ""


def scan_tables(db_entries):
    tables_path = get_tables_path()
    digests = {}
    ids = {}
    scripts = {}
    tool_path = get_vpxtool_path()
    for root, dirs, files in os.walk(tables_path):
        for name in files:
            if name.lower().endswith(".vpx"):
                full = os.path.join(root, name)
                try:
                    digest = compute_sha256(full)
                    digests[full] = digest
                    # Extract VBS script
                    subprocess.run([tool_path, "extractvbs", full], check=False)
                    vbs_file = os.path.splitext(full)[0] + ".vbs"
                    if os.path.exists(vbs_file):
                        scripts[full] = compute_sha256(vbs_file)
                    if db_entries:
                        dir_name = os.path.basename(root)
                        clean_dir_name = re.sub(r"\s*\([^)]*\)\s*$", "", dir_name)
                        ids[full] = find_vps_id(clean_dir_name, db_entries)
                except Exception as e:
                    logger.error(f"Error hashing {full}: {e}")
    return digests, ids, scripts



def load_tables_index():
    if not os.path.exists(INDEX_FILE):
        return {}, {}, {}, {}, None
    parser = configparser.ConfigParser()
    parser.read(INDEX_FILE)
    tables = {}
    ids = {}
    scripts = {}
    patched = {}
    if parser.has_section("Tables"):
        for path, digest in parser["Tables"].items():
            tables[path] = digest
    if parser.has_section("IDs"):
        for path, table_id in parser["IDs"].items():
            ids[path] = table_id
    if parser.has_section("Scripts"):
        for path, sdigest in parser["Scripts"].items():
            scripts[path] = sdigest
    if parser.has_section("Patched"):
        for path, value in parser["Patched"].items():
            patched[path] = value
    ts = parser.get("Meta", "vpsdb_timestamp", fallback=None)
    return tables, ids, scripts, patched, ts


def save_tables_index(tables, ids, scripts, patched, timestamp=None):
    parser = configparser.ConfigParser()
    parser["Tables"] = tables
    parser["IDs"] = ids
    parser["Scripts"] = scripts
    parser["Patched"] = patched
    if timestamp:
        parser["Meta"] = {"vpsdb_timestamp": timestamp}
    os.makedirs(os.path.dirname(INDEX_FILE), exist_ok=True)
    with open(INDEX_FILE, "w") as f:
        parser.write(f)
    logger.info("Tables index saved")

