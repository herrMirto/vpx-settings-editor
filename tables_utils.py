import os
import hashlib
import json
import configparser
from difflib import SequenceMatcher
from urllib.request import urlopen
from config_utils import get_tables_path
from utils import logger
import re

INDEX_FILE = os.path.expanduser("~/.vpx_settings_editor/tables_index.ini")
VPS_DB_URL = "https://virtualpinballspreadsheet.github.io/vps-db/db/vpsdb.json"
VPS_LAST_UPDATED_URL = "https://virtualpinballspreadsheet.github.io/vps-db/lastUpdated.json"
LOCAL_DB_FILE = os.path.expanduser("~/.vpx_settings_editor/vpsdb.json")


def compute_sha256(filepath):
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256_hash.update(chunk)
    return sha256_hash.hexdigest()


def fetch_json(url):
    with urlopen(url) as resp:
        return json.loads(resp.read().decode())


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
    for root, dirs, files in os.walk(tables_path):
        for name in files:
            if name.lower().endswith(".vpx"):
                full = os.path.join(root, name)
                try:
                    digest = compute_sha256(full)
                    digests[full] = digest
                    if db_entries:
                        dir_name = os.path.basename(root)
                        clean_dir_name = re.sub(r"\s*\([^)]*\)\s*$", "", dir_name)
                        print(clean_dir_name)
                        ids[full] = find_vps_id(clean_dir_name, db_entries)
                except Exception as e:
                    logger.error(f"Error hashing {full}: {e}")
    return digests, ids



def load_tables_index():
    if not os.path.exists(INDEX_FILE):
        return {}, {}, None
    parser = configparser.ConfigParser()
    parser.read(INDEX_FILE)
    tables = {}
    ids = {}
    if parser.has_section("Tables"):
        for path, digest in parser["Tables"].items():
            tables[path] = digest
    if parser.has_section("IDs"):
        for path, table_id in parser["IDs"].items():
            ids[path] = table_id
    ts = parser.get("Meta", "vpsdb_timestamp", fallback=None)
    return tables, ids, ts


def save_tables_index(tables, ids, timestamp=None):
    parser = configparser.ConfigParser()
    parser["Tables"] = tables
    parser["IDs"] = ids
    if timestamp:
        parser["Meta"] = {"vpsdb_timestamp": timestamp}
    os.makedirs(os.path.dirname(INDEX_FILE), exist_ok=True)
    with open(INDEX_FILE, "w") as f:
        parser.write(f)
    logger.info("Tables index saved")

