import os
import configparser
import sys
import emoji

CONFIG_PATH = os.path.expanduser("~/.config/vpx_settings_editor.cfg")

DEFAULT_CONFIG = """
[Paths]
vpx_ini_path = /path/to/VPinballX.ini
vpx_binary_path = /path/to/VPinballX_GL or /path/to/VPinballX_BGFX
"""

def load_config():
    if not os.path.exists(CONFIG_PATH):
        show_config_error("Configuration file not found.\n")
    
    config = configparser.ConfigParser()
    config.read(CONFIG_PATH)

    return config

def show_config_error(reason):
    print(emoji.emojize(':cross_mark:' f"{reason}"))
    print(emoji.emojize(':pencil:' f"Please create the configuration file {CONFIG_PATH} with the following data:\n"))
    print(f"{DEFAULT_CONFIG.strip()}\n")
    sys.exit(1)

def show_missing_files_error(missing_paths):
    print(emoji.emojize(':cross_mark: Configured file(s) do not exist:\n'))
    for path in missing_paths:
        print(f"Check the correct path of: {path}")
    sys.exit(1)

def validate_config():
    try:
        config = load_config()

        # Check if section exists
        if "Paths" not in config:
            show_config_error("Missing section [Paths] in the configuration file.")

        # Check mandatory keys
        if "vpx_ini_path" not in config["Paths"] or "vpx_binary_path" not in config["Paths"]:
            show_config_error("Missing mandatory keys 'vpx_ini_path' or 'vpx_binary_path' in the configuration file.")

        # Check if the files exist
        ini_path = config["Paths"]["vpx_ini_path"]
        binary_path = config["Paths"]["vpx_binary_path"]

        missing = []
        if not os.path.isfile(ini_path):
            missing.append(ini_path)
        if not os.path.isfile(binary_path):
            missing.append(binary_path)

        if missing:
            show_missing_files_error(missing)

        return ini_path, binary_path

    except Exception as e:
        show_config_error(f"Error while reading configuration")

def get_vpx_ini_path():
    ini_path, _ = validate_config()
    return ini_path

def get_vpx_binary_path():
    _, binary_path = validate_config()
    return binary_path
