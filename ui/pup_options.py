from ui_helpers.widget_diffs import show_diff_table
from config.vpinball_ini import VPinballINI
from ui_helpers.widget_option_manager import WidgetOptionManager  

ini = VPinballINI()

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

def load_pup_options(main_window):
    manager = WidgetOptionManager(main_window)
    return manager.load_options("Standalone", PUP_OPTIONS)

def prepare_pup_updates(main_window):
    manager = WidgetOptionManager(main_window)
    return manager.prepare_updates("Standalone", PUP_OPTIONS)

def on_save_pup_clicked(main_window):
    updates = prepare_pup_updates(main_window)
    if show_diff_table(ini, updates, parent=main_window):
        for section, values in updates.items():
            ini.update_section_subset(section, values)
        ini.save()

