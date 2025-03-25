from PySide6.QtWidgets import QCheckBox, QComboBox, QLineEdit
from config.vpinball_ini import VPinballINI
from utils import show_save_message, logger

ini = VPinballINI()

VR_OPTIONS = [
    "AskToTurnOn", "ScaleToFixedWidth", "ScaleAbsolute", "NearPlane", "EyeFBFormat", "Slope",
    "Orientation", "TableX", "TableY", "TableZ", "VRPreview", "ShrinkPreview", "PreviewWidth",
    "PreviewHeight", "JoyTableRecenterKey", "JoyTableUpKey", "JoyTableDownKey", "CaptureExternalDMD",
    "CapturePUP"
]

PLAYER_OPTIONS = {"CaptureExternalDMD": "DMDSource", "CapturePUP": "BGSource"}

DEFAULTS = {
    "AskToTurnOn": 1,
    "EyeFBFormat": 1,
    "VRPreview": 1,
    "JoyTableRecenterKey": 0,
    "JoyTableUpKey": 0,
    "JoyTableDownKey": 0,
}

def load_vr_options(main_window):
    """Load VR Options from VPinballX.ini"""
    logger.info("=== Loading VR Options ===")
    
    values_vr = ini.get_section_subset("PlayerVR", VR_OPTIONS)
    values_player = ini.get_section_subset("Player", PLAYER_OPTIONS.values())
    
    for option in VR_OPTIONS:
        widget = getattr(main_window.ui, option, None)
        if not widget:
            continue
        
        value = values_vr.get(option, str(DEFAULTS.get(option, "0")))
        if isinstance(widget, QCheckBox):
            widget.setChecked(value == "1")
        elif isinstance(widget, QComboBox):
            widget.setCurrentIndex(int(value) if value.isdigit() else 0)
        elif isinstance(widget, QLineEdit):
            widget.setText(value)
        logger.info(f"=== Loading {option}: {value}")

    
    for vr_option, player_option in PLAYER_OPTIONS.items():
        widget = getattr(main_window.ui, vr_option, None)
        if widget:
            widget.setChecked(values_player.get(player_option, "0") == "1")
    
    logger.info("=== VR Options loaded ===")

def save_vr_options(main_window):
    """Save VR Options on VPinballX.ini"""
    logger.info("=== Saving VR Options ===")
    
    updates_vr = {}
    updates_player = {}
    
    for option in VR_OPTIONS:
        widget = getattr(main_window.ui, option, None)
        if not widget:
            continue
        
        if isinstance(widget, QCheckBox):
            updates_vr[option] = "1" if widget.isChecked() else "0"
            logger.info(f"=== Saving {option}: {updates_vr[option]}")
        elif isinstance(widget, QComboBox):
            updates_vr[option] = str(widget.currentIndex())
            logger.info(f"=== Saving {option}: {updates_vr[option]}")
        elif isinstance(widget, QLineEdit):
            updates_vr[option] = widget.text()
            logger.info(f"=== Saving {option}: {updates_vr[option]}")
    
    for vr_option, player_option in PLAYER_OPTIONS.items():
        widget = getattr(main_window.ui, vr_option, None)
        if widget:
            updates_player[player_option] = "1" if widget.isChecked() else "0"
    
    ini.update_section_subset("PlayerVR", updates_vr)
    ini.update_section_subset("Player", updates_player)
    
    
    try:
        ini.save()
        logger.info("=== VR Options saved ===")
        show_save_message("VR Options saved")
    except Exception as e:
        logger.error(f"Error saving VR Options: \n {e}")
        show_save_message("Error saving VR Options")
