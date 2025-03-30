# -*- coding: utf-8 -*-
from config.vpinball_ini import VPinballINI
from utils import show_save_message, logger
from ui_helpers.widget_diffs import show_diff_table
from ui_helpers.widget_option_manager import WidgetOptionManager

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
    all_options = {opt for group in SCREEN_OPTIONS.values() for opt in group}
    manager = WidgetOptionManager(main_window)
    return manager.load_options("Standalone", all_options, CHECKBOX_OPTIONS)

def prepare_screen_updates(main_window):
    all_options = {opt for group in SCREEN_OPTIONS.values() for opt in group}
    manager = WidgetOptionManager(main_window)
    return manager.prepare_updates("Standalone", all_options, CHECKBOX_OPTIONS)

def on_save_screen_clicked(main_window):
    updates = prepare_screen_updates(main_window)
    if show_diff_table(ini, updates, parent=main_window):
        for section, values in updates.items():
            ini.update_section_subset(section, values)
        try:
            ini.save()
            logger.info("=== Screen Options saved ===")
            show_save_message("Screen Options saved")
        except Exception as e:
            logger.error(f"Error saving Screen Options: {e}")
            show_save_message("Error saving Screen Options")
