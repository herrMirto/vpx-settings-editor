"""
Manages the buttons options
"""

from ui_helpers.widget_option_manager import WidgetOptionManager
from ui_helpers.widget_diffs import show_diff_table
from config.vpinball_ini import VPinballINI
from utils import logger, show_save_message

ini = VPinballINI()

DEFAULTS = {
    "JoyLFlipKey": 0,
    "JoyRFlipKey": 0,
    "JoyStagedLFlipKey": 0,
    "JoyStagedRFlipKey": 0,
    "JoyPlungerKey": 0,
    "JoyAddCreditKey": 0,
    "JoyAddCredit2Key": 0,
    "JoyLMagnaSave": 0,
    "JoyRMagnaSave": 0,
    "JoyStartGameKey": 0,
    "JoyExitGameKey": 0,
    "JoyVolumeUp": 0,
    "JoyVolumeDown": 0,
    "JoyLTiltKey": 0,
    "JoyCTiltKey": 0,
    "JoyRTiltKey": 0,
    "JoyMechTiltKey": 0,
    "JoyDebugKey": 0,
    "JoyDebuggerKey": 0,
    "JoyCustom1": 0,
    "JoyCustom2": 0,
    "JoyCustom3": 0,
    "JoyCustom4": 0,
    "JoyLockbarKey": 0,
    "JoyPauseKey": 0,
    "JoyTweakKey": 0,
    "JoyEscapeKey": 0,
    "JoyEnable3DKey": 0,
    "DisableESC": 0,
    "PBWDefaultLayout": 0
}

BUTTONS_OPTIONS = list(DEFAULTS.keys())
CHECKBOX_OPTIONS = {
    "DisableESC",
    "PBWDefaultLayout"
}

def load_buttons_options(main_window): 
    manager = WidgetOptionManager(main_window)
    return manager.load_options(
        "Player",
        BUTTONS_OPTIONS,
        checkbox_options=CHECKBOX_OPTIONS,
        defaults=DEFAULTS
    )

def prepare_buttons_updates(main_window):
    manager = WidgetOptionManager(main_window)
    return manager.prepare_updates(
        "Player",
        BUTTONS_OPTIONS,
        checkbox_options=CHECKBOX_OPTIONS,
    )

def on_save_buttons_clicked(main_window):
    updates = prepare_buttons_updates(main_window)
    if show_diff_table(ini, updates, parent=main_window):
        for section, values in updates.items():
            ini.update_section_subset(section, values)
        try:
            ini.save()
            logger.info("=== Buttons Options saved ===")
            show_save_message("Buttons Options saved")
        except Exception as e:
            logger.error(f"Error saving Buttons Options")
