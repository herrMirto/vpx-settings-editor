import os
import configparser

CONFIG_PATH = os.path.expanduser("~/.config/vpx_settings_editor.cfg")

def get_vpx_ini_path():
    config = configparser.ConfigParser()
    config.read(CONFIG_PATH)

    try:
        return config["Paths"]["vpx_ini_path"]
    except KeyError:
        raise FileNotFoundError(f"'vpx_ini_path' not found in {CONFIG_PATH}")
    
def get_vpx_binary_path():
    config = configparser.ConfigParser()
    config.read(CONFIG_PATH)

    try:
        return config["Paths"]["vpx_binary_path"]
    except KeyError:
        raise FileNotFoundError(f"'vpx_binary_path' not found in {CONFIG_PATH}")
