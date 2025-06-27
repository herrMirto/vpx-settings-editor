import os
import json
import re
import logging
from vpxparser import VPXParser
from config_utils import get_tables_path
from difflib import SequenceMatcher
from urllib.request import urlopen


logger = logging.getLogger("tables_meta")

INDEX_FILE = os.path.expanduser("~/.vpx_settings_editor/tables_meta.json")
VPS_DB_URL = "https://virtualpinballspreadsheet.github.io/vps-db/db/vpsdb.json"
VPS_LAST_UPDATED_URL = "https://virtualpinballspreadsheet.github.io/vps-db/lastUpdated.json"
LOCAL_DB_FILE = os.path.expanduser("~/.vpx_settings_editor/vpsdb.json")
PATCH_HASHES_URL = "https://raw.githubusercontent.com/jsm174/vpx-standalone-scripts/master/hashes.json"


def fetch_json(url):
    with urlopen(url) as resp:
        if resp.status != 200:
            raise Exception(f"Failed to fetch {url}: {resp.status} {resp.reason}")
        content = resp.read().decode()
        return json.loads(content)
    
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

def load_patch_hashes():
    """
    Return a dict: vbs_sha256 -> { url, patched_sha256 }, based on hashes.json
    """
    try:
        data = fetch_json(PATCH_HASHES_URL)
    except Exception as e:
        logger.error(f"Failed to fetch patch hashes: {e}")
        return {}

    if not isinstance(data, list):
        logger.error("Unexpected patch data format (expected list of entries).")
        return {}

    patch_map = {}
    for entry in data:
        if not isinstance(entry, dict):
            continue
        orig_sha = entry.get("sha256")
        patched = entry.get("patched", {})
        patched_url = patched.get("url")
        patched_sha = patched.get("sha256")
        if orig_sha and patched_url:
            patch_map[orig_sha.strip()] = {
                "url": patched_url,
                "patched_sha256": patched_sha.strip() if isinstance(patched_sha, str) else None
            }

    logger.debug(f"Loaded patch_map with {len(patch_map)} entries.")
    return patch_map

def build_tables_meta(db_entries=None):
    tables_path = get_tables_path()
    meta = {}
    patch_map = load_patch_hashes()
    logger.debug(f"Loaded {len(patch_map)} patch entries.")

    parser = VPXParser()

    for root, _, files in os.walk(tables_path):
        for name in files:
            if not name.lower().endswith(".vpx"):
                continue

            try:
                full_path = os.path.join(root, name)
                values = parser.singleFileExtract(full_path)
                if not values:
                    continue

                code_sha = values.get("codeSha256Hash")
                file_sha = values.get("fileHash")

                # Patch logic
                patch_entry = patch_map.get(code_sha)
                base_name = os.path.basename(full_path)
                logger.debug(f"[{base_name}] vbs_sha256: {code_sha}")
                if patch_entry:
                    logger.debug(f"[{base_name}] PATCH FOUND: {patch_entry.get('url')}")
                else:
                    logger.debug(f"[{base_name}] No patch for this hash.")
                    
                vbs_patch = "yes" if patch_entry else "no"
                vbs_patch_applied = "no"
                if patch_entry and patch_entry.get("patched_sha256") == code_sha:
                    vbs_patch_applied = "yes"

                # Derive ID
                dir_name = os.path.basename(root)
                clean_dir_name = re.sub(r"\s*\([^)]*\)\s*$", "", dir_name)
                vps_id = find_vps_id(clean_dir_name, db_entries)

                # Monta entrada
                base_name = os.path.basename(full_path)
                entry = {
                    "path": full_path,
                    "sha256": file_sha,
                    "vps_id": vps_id,
                    "vbs_sha256": code_sha,
                    "vbs_patch": vbs_patch,
                    "vbs_patch_applied": vbs_patch_applied
                }

                # Extras úteis
                for extra in [
                    "rom", "detectNfozzy", "detectLut", "detectScorebit",
                    "detectFleep", "detectSSF", "detectFastflips", "detectFlex"
                ]:
                    if extra in values:
                        entry[extra] = values[extra]

                meta[base_name] = entry

            except Exception as e:
                logger.error(f"Error processing {name}: {e}")

    # Save file
    try:
        with open(INDEX_FILE, "w", encoding="utf-8") as f:
            json.dump({"tables": meta}, f, indent=2, ensure_ascii=False)
        logger.info("tables_meta.json written successfully.")
    except Exception as e:
        logger.error(f"Failed to save tables_meta.json: {e}")
