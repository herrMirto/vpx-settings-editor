import re
from PySide6.QtWidgets import QCheckBox, QComboBox, QLineEdit, QLabel, QColorDialog
from PySide6.QtGui import QColor, QPalette
from config.vpinball_ini import VPinballINI
from utils import show_save_message, logger

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
    """Load Editor options from VPinballX.ini"""
    logger.info("=== Loading Editor Options ===")
    
    values = ini.get_section_subset("Editor", EDITOR_OPTIONS)
    
    for option in EDITOR_OPTIONS:
        widget = getattr(main_window.ui, option, None)
        if not widget:
            continue
        
        value = values.get(option, str(DEFAULTS.get(option, "0")))
        if isinstance(widget, QCheckBox):
            widget.setChecked(value == "1")
            logger.info(f"Loading {option}: {value}")
        elif isinstance(widget, QComboBox):
            widget.setCurrentIndex(int(value) if value.isdigit() else 0)
            logger.info(f"Loading {option}: {value}")
        elif isinstance(widget, QLineEdit):
            widget.setText(value)
            logger.info(f"Loading {option}: {value}")
        elif isinstance(widget, QLabel) and option in COLOR_LABELS:
            if not value or value == "0":
                value = DEFAULT_COLORS[option]
                logger.info(f"Using default value for {option}: {value}")
            widget.setStyleSheet(f"background-color: #{value}; border: 1px solid black;")
            #widget.setAutoFillBackground(True)
            palette = widget.palette()
            palette.setColor(QPalette.ColorRole.Window, QColor(f"{value}"))
            #widget.setPalette(palette)
            logger.info(f"Loading {option}: {value}")
    
    logger.info("=== Editor Options loaded ===")

def save_editor_options(main_window):
    """Save Editor options on VPinballX.ini"""
    logger.info("=== Saving Editor Options ===")    
    updates = {}
    
    for option in EDITOR_OPTIONS:
        widget = getattr(main_window.ui, option, None)
        if not widget:
            continue
        
        if isinstance(widget, QCheckBox):
            updates[option] = "1" if widget.isChecked() else "0"
            logger.info(f"Saving {option}: {updates[option]}")
        elif isinstance(widget, QComboBox):
            updates[option] = str(widget.currentIndex())
            logger.info(f"Saving {option}: {updates[option]}")
        elif isinstance(widget, QLineEdit):
            updates[option] = widget.text()
            logger.info(f"Saving {option}: {updates[option]}")
        elif isinstance(widget, QLabel) and option in COLOR_LABELS:
            style = widget.styleSheet()
            if "background-color:" in style:
                updates[option] = style.split("background-color:")[-1].split(";")[0].strip().replace("#", "")
                logger.info(f"Saving {option}: {updates[option]}")
            else:
                logger.warning(f"Color not found for Widget {option}. Skipping.")
    
    ini.update_section_subset("Editor", updates)
    try:
        ini.save()
        logger.info("=== Editor Options Saved ===")
        show_save_message("Editor Options Saved")
    except Exception as e:
        logger.error(f"Error saving Editor Options: \n {e}")
        show_save_message("Error saving Editor Options")


def change_color(main_window, label_name):
    """Changes color after clicking on QLabel."""
    widget = getattr(main_window.ui, label_name, None)
    if not widget:
        return

    style = widget.styleSheet()
    match = re.search(r"background-color:\s*#([0-9A-Fa-f]{6})", style)
    hex_color = match.group(1) if match else DEFAULT_COLORS.get(label_name, "000000")

    current_color = QColor(f"#{hex_color}")
    new_color = QColorDialog.getColor(current_color, main_window)

    if new_color.isValid():
        widget.setStyleSheet(f"background-color: {new_color.name()}; border: 1px solid black;")
