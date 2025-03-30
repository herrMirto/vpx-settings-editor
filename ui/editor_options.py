from ui_helpers.widget_option_manager import WidgetOptionManager
from ui_helpers.widget_diffs import show_diff_table
from config.vpinball_ini import VPinballINI
from utils import logger, show_save_message

ini = VPinballINI()

EDITOR_OPTIONS = [
    "SelectTableOnStart", "SelectTableOnPlayerClose", "ShowDragPoints", "DrawLightCenters", "GridSize",
    "BackgroundColor", "FillColor", "ElementSelectColor", "ElementSelectLockedColor", "DefaultMaterialColor",
    "GroupElementsInCollection", "Units", "AutoSaveOn", "AutoSaveTime", "ThrowBallsAlwaysOn", "ThrowBallSize",
    "ThrowBallMass", "BallControlAlwaysOn", "EnableLog", "LogScriptOutput", "AlwaysViewScript"
]

COLOR_LABELS = [
    "DefaultMaterialColor", "ElementSelectColor", "ElementSelectLockedColor", "FillColor", "BackgroundColor"
]

DEFAULTS = {"Units": 0}
DEFAULT_COLORS = {
    "DefaultMaterialColor": "FF66B2",
    "ElementSelectColor": "0000FF",
    "ElementSelectLockedColor": "666699",
    "FillColor": "AABB99",
    "BackgroundColor": "888888"
}

def load_editor_options(main_window):
    manager = WidgetOptionManager(main_window)
    return manager.load_options(
        "Editor",
        EDITOR_OPTIONS,
        color_labels=COLOR_LABELS,
        defaults=DEFAULTS,
        default_colors=DEFAULT_COLORS
    )

def prepare_editor_updates(main_window):
    manager = WidgetOptionManager(main_window)
    return manager.prepare_updates(
        "Editor",
        EDITOR_OPTIONS,
        color_labels=COLOR_LABELS
    )

def on_save_editor_clicked(main_window):
    updates = prepare_editor_updates(main_window)
    if show_diff_table(ini, updates, parent=main_window):
        for section, values in updates.items():
            ini.update_section_subset(section, values)
        try:
            ini.save()
            logger.info("=== Editor Options saved ===")
            show_save_message("Editor Options saved")
        except Exception as e:
            logger.error(f"Error saving Editor Options: {e}")
            show_save_message("Error saving Editor Options")
