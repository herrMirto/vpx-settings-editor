from PySide6.QtWidgets import QCheckBox, QComboBox
from config.vpinball_ini import VPinballINI
from utils import show_save_message, logger

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
    "DisableESC": 0,
    "PBWDefaultLayout": 0
}



def load_buttons_options(main_window):
    """Load Buttons options from VPinballX.ini"""
    logger.info("=== Loading Buttons Options ===")
    
    widgets = {option: getattr(main_window.ui, option, None) for option in DEFAULTS.keys()}
    values = ini.get_section_subset("Player", DEFAULTS.keys())
    
    for key, widget in widgets.items():
        if not widget:
            logger.warning(f"Widget {key} not found in UI")
            continue
        
        value = values.get(key, str(DEFAULTS[key]))
        if isinstance(widget, QCheckBox):
            widget.setChecked(value == "1")
        elif isinstance(widget, QComboBox):
            widget.setCurrentIndex(int(value) if value.isdigit() else 0)
        logger.info(f"Loading {key}: {value}")
    
    logger.info("=== Buttons Options loaded ===")

def save_buttons_options(main_window):
    """Save Buttons options on VPinballX.ini"""
    logger.info("=== Saving Buttons Options ===")    
    widgets = {option: getattr(main_window.ui, option, None) for option in DEFAULTS.keys()}
    updates = {}
    
    for key, widget in widgets.items():
        if not widget:
            logger.warning(f"Widget {key} not found in UI")
            continue
        
        if isinstance(widget, QCheckBox):
            updates[key] = "1" if widget.isChecked() else "0"
        elif isinstance(widget, QComboBox):
            updates[key] = str(widget.currentIndex())
        logger.info(f"Saving {key}: {updates[key]}")
    
    ini.update_section_subset("Player", updates)
    
    try:
        ini.save()
        logger.info("=== Buttons Options Saved ===")
        show_save_message("Buttons Options Saved")
    except Exception as e:
        logger.error(f"Error saving Buttons Options: \n {e}")
        show_save_message("Error saving Buttons Options")
