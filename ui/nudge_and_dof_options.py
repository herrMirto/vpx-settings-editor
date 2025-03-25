from PySide6.QtWidgets import QCheckBox, QComboBox, QLineEdit
from utils import show_save_message, logger
from config.vpinball_ini import VPinballINI

ini = VPinballINI()

DEFAULTS = {
    "LRAxis": 1,  
    "UDAxis": 2,
    "PlungerAxis": 3,
    "InputApi": 0,
    "Button": 0,
    "JoyPMBuyIn": 0, 
    "JoyPMCoin3": 0, 
    "JoyPMCoin4": 0, 
    "JoyPMCoinDoor": 0,
    "JoyPMCancel": 0,
    "JoyPMDown": 0,
    "JoyPMUp": 0,
    "JoyPMEnter": 0,
    "RumbleMode": 0,
    "PlungerSpeedAxis": 0,
}

DOF_DEFAULTS = {
    "DOFContactors": 2,
    "DOFKnocker": 2,
    "DOFChimes": 2,
    "DOFBell": 2,
    "DOFGear": 2,
    "DOFShaker": 2,
    "DOFFlippers": 2,
    "DOFTargets": 2,
    "DOFDroptargets": 2
}

NUDGE_OPTIONS = [
    "LRAxis",
    "LRAxisFlip",
    "UDAxis",
    "UDAxisFlip",
    "PBWEnabled",
    "PBWNormalMount",
    "PBWRotationCB",
    "PBWRotationvalue",
    "PBWAccelGainX",
    "PBWAccelGainY",
    "PBWAccelMaxX",
    "PBWAccelMaxY",
    "EnableNudgeFilter",
    "EnableLegacyNudge",
    "LegacyNudgeStrength", 
    "AccelVelocityInput", 
    "TiltSensCB",
    "TiltSensValue",
    "PlungerAxis",
    "PlungerSpeedScale",
    "ReversePlungerAxis", 
    "DeadZone",
    "PlungerRetract",
    "EnableMouseInPlayer",
    "EnableCameraModeFlyAround",
    "InputApi",
    "RumbleMode",
    "JoyPMBuyIn",
    "JoyPMCoin3", 
    "JoyPMCoin4", 
    "JoyPMCoinDoor",
    "JoyPMCancel",
    "JoyPMDown",
    "JoyPMUp",
    "JoyPMEnter",
]

DOF_OPTIONS = [
    "ForceDisableB2S",
    "DOFContactors", 
    "DOFKnocker",
    "DOFChimes", 
    "DOFBell", 
    "DOFGear",
    "DOFShaker", 
    "DOFFlippers", 
    "DOFTargets",
    "DOFDroptargets",
    "DOFPlugin" 
]

NUDGE_DOF_OPTIONS = {
    "Player": NUDGE_OPTIONS,
    "Controller": DOF_OPTIONS,
    "Standalone": ["DOFPlugin"]
}

def load_nudge_dof_options(main_window):
    """Load Nudge and DOF options from VPinballX.ini"""
    logger.info("=== Loading Nudge and DOF Options ===")
    widgets = {}
    for section, options in NUDGE_DOF_OPTIONS.items():
        for option in options:
            widget = getattr(main_window.ui, option, None)
            if not widget:
                logger.error(f"Unknown widget: {option}")
                continue
            
            default_value = DEFAULTS.get(option, DOF_DEFAULTS.get(option, "0"))
            value = ini.get_section_subset(section, [option]).get(option, str(default_value))
            
            if isinstance(widget, QCheckBox):
                widget.setChecked(value == "1")
                #logger.info(f"Loading {option}: {value}")
            elif isinstance(widget, QComboBox):
                widget.setCurrentIndex(int(value) if value.isdigit() else int(default_value))
                #logger.info(f"Loading {option}: {value}")
            elif isinstance(widget, QLineEdit):
                widget.setText(value)
                #logger.info(f"Loading {option}: {value}")
            
            widgets[option] = widget
            logger.info(f"Loading {option}: {value}")
    
    return widgets

def save_nudge_dof_options(main_window):
    """Save Nudge and DOF options on VPinballX.ini"""
    logger.info("=== Saving Nudge and DOF == === == == Options ===")
    updates = {"Player": {}, "Controller": {}, "Standalone": {}}
    
    for section, options in NUDGE_DOF_OPTIONS.items():
        for widget in options:
            gui_element = getattr(main_window.ui, widget, None)
            if not gui_element:
                logger.error(f"Unknown/Unsupported widget: {widget}")
                continue
            
            if isinstance(gui_element, QCheckBox):
                updates[section][widget] = "1" if gui_element.isChecked() else "0"
            elif isinstance(gui_element, QComboBox):
                updates[section][widget] = str(gui_element.currentIndex())
            elif isinstance(gui_element, QLineEdit):
                updates[section][widget] = gui_element.text()
            logger.info(f"Saving {widget}: {updates[section][widget]}")
    
    for section, values in updates.items():
        ini.update_section_subset(section, values)
    
    try:
        ini.save()
        logger.info("=== Nudge and DOF Options Saved ===")
        show_save_message("Nudge and DOF Options Saved")
    except Exception as e:
        logger.error(f"Error saving Nudge and DOF Options: \n {e}")
        show_save_message("Error saving Nudge and DOF Options")

    