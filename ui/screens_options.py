from PySide6.QtWidgets import QCheckBox, QLineEdit
from config.vpinball_ini import VPinballINI
from utils import show_save_message, logger

ini = VPinballINI()

SCREEN_OPTIONS = {
    "PINMAME": ["PinMAMEWindow", "PinMAMEWindowX", "PinMAMEWindowY", "PinMAMEWindowWidth", "PinMAMEWindowHeight", "PinMAMEWindowRotation"],
    "FLEXDMD": ["FlexDMDWindow", "FlexDMDWindowX", "FlexDMDWindowY", "FlexDMDWindowWidth", "FlexDMDWindowHeight", "FlexDMDWindowRotation"],
    "B2SDMD": [
        "B2SHideGrill", "B2SHideB2SDMD", "B2SHideB2SBackglass", "B2SHideDMD", "B2SDualMode", "B2SWindows",
        "B2SBackglassX", "B2SBackglassY", "B2SBackglassWidth", "B2SBackglassHeight", "B2SBackglassRotation",
        "B2SDMDX", "B2SDMDY", "B2SDMDWidth", "B2SDMDHeight", "B2SDMDRotation", "B2SDMDFlipY", "B2SPlugins"
    ],
    "ZEDMD": ["ZeDMD", "ZeDMDDevice", "ZeDMDDebug", "ZeDMDBrightness", "ZeDMDWiFi", "ZeDMDWiFiAddr"],
    "PIXELCADE": ["Pixelcade","PixelcadeDevice"]
}

CHECKBOX_OPTIONS = {
    "B2SHideGrill", 
    "B2SHideB2SDMD", 
    "B2SHideB2SBackglass", 
    "B2SHideDMD", 
    "B2SDualMode", 
    "B2SDMDFlipY",
    "B2SPlugins",
    "ZeDMD", 
    "ZeDMDDebug", 
    "Pixelcade"
}

def load_screen_options(main_window):
    """Load Screens/DMDs options from VPinballX.ini"""
    all_options = {opt for group in SCREEN_OPTIONS.values() for opt in group}
    values = ini.get_section_subset("Standalone", all_options)
    
    for option in all_options:
        widget = getattr(main_window.ui, option, None)
        if not widget:
            continue
        
        value = values.get(option, "0")
        if option in CHECKBOX_OPTIONS and isinstance(widget, QCheckBox):
            widget.setChecked(value == "1")
        elif isinstance(widget, QLineEdit):
            widget.setText(value)
        logger.info(f"Loading {option}: {value}")

def save_screen_options(main_window):
    """Save Screens/DMDs options on VPinballX.ini"""
    updates = {}
    
    all_options = {opt for group in SCREEN_OPTIONS.values() for opt in group}
    
    for option in all_options:
        widget = getattr(main_window.ui, option, None)
        if not widget:
            continue
        
        if option in CHECKBOX_OPTIONS and isinstance(widget, QCheckBox):
            updates[option] = "1" if widget.isChecked() else "0"
            logger.info(f"Saving {option}: {updates[option]}")
        elif isinstance(widget, QLineEdit):
            updates[option] = widget.text()
            logger.info(f"Saving {option}: {widget.text()}")

    ini.update_section_subset("Standalone", updates)
    
    try:
        ini.save()
        logger.info("=== Screen Options saved ===")
        show_save_message("Screen Options saved")
    except Exception as e:
        logger.error(f"Error saving Screen Options: \n {e}")
        show_save_message("Error saving Screen Options")
    ini.save()
