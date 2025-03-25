from utils import show_save_message, logger
from config.vpinball_ini import VPinballINI

ini = VPinballINI()

# Class for handling this in another way?
PUP_OPTIONS = [
    "PUPCapture", "PUPPlugin", "PUPWindows", "PUPTopperScreen", "PUPTopperWindow", "PUPTopperWindowX",
    "PUPTopperWindowY", "PUPTopperWindowWidth", "PUPTopperWindowHeight", "PUPTopperWindowRotation",
    "PUPBackglassScreen", "PUPBackglassWindow", "PUPBackglassWindowX", "PUPBackglassWindowY",
    "PUPBackglassWindowWidth", "PUPBackglassWindowHeight", "PUPBackglassWindowRotation", "PUPDMDScreen",
    "PUPDMDWindow", "PUPDMDWindowX", "PUPDMDWindowY", "PUPDMDWindowWidth", "PUPDMDWindowHeight",
    "PUPDMDWindowRotation", "PUPPlayfieldScreen", "PUPPlayfieldWindow", "PUPPlayfieldWindowX",
    "PUPPlayfieldWindowY", "PUPPlayfieldWindowWidth", "PUPPlayfieldWindowHeight", "PUPPlayfieldWindowRotation",
    "PUPFullDMDScreen", "PUPFullDMDWindow", "PUPFullDMDWindowX", "PUPFullDMDWindowY", "PUPFullDMDWindowWidth",
    "PUPFullDMDWindowHeight", "PUPFullDMDWindowRotation"
]

def load_pup_config(main_window):
    """Load PUP configuration from VPinballX.ini"""
    logger.info("=== Loading PUP Options ===")
    
    widgets = {option: getattr(main_window.ui, option, None) for option in PUP_OPTIONS}
    values = ini.get_section_subset("Standalone", PUP_OPTIONS)
    
    for key, widget in widgets.items():
        if not widget:
            logger.warning(f"Widget {key} not found in UI")
            continue
        
        value = values.get(key, "0")
        if key in ["PUPCapture", "PUPPlugin"]:
            widget.setChecked(value == "1")
        else:
            widget.setText(value)
        logger.info(f"Loading {key}: {value}")
    
    logger.info("=== PUP Options loaded ===")

def save_pup_options(main_window):
    """Save PUP options on VPinballX.ini"""
    logger.info("=== Saving PUP Options ===")    
    widgets = {option: getattr(main_window.ui, option, None) for option in PUP_OPTIONS}
    updates = {}
    
    for key, widget in widgets.items():
        if not widget:
            logger.warning(f"Widget {key} not found in UI")
            continue
        
        if key in ["PUPCapture", "PUPPlugin"]:
            updates[key] = "1" if widget.isChecked() else "0"
        else:
            updates[key] = widget.text()
        logger.info(f"Saving {key}: {updates[key]}")
    
    ini.update_section_subset("Standalone", updates)
    
    try:
        ini.save()
        logger.info("=== PUP Options saved ===")
        show_save_message("PUP Options saved")
    except Exception as e:
        logger.error(f"Error saving PUP Options: \n {e}")
        show_save_message("Error saving PUP Options")
