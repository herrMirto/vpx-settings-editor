from PySide6.QtWidgets import QCheckBox, QLineEdit, QLabel, QComboBox, QColorDialog
from PySide6.QtGui import QColor, QPalette
from utils import logger
from config.vpinball_ini import VPinballINI

ini = VPinballINI()

class WidgetOptionManager:
    def __init__(self, main_window):
        self.main_window = main_window

    def load_options(self, section, option_list, checkbox_options=None, color_labels=None, defaults=None, default_colors=None):
        logger.info(f"=== Loading {section} Options ===")

        widgets = {option: getattr(self.main_window.ui, option, None) for option in option_list}
        values = ini.get_section_subset(section, option_list)

        for key, widget in widgets.items():
            if not widget:
                logger.warning(f"Widget {key} not found in UI")
                continue

            value = values.get(key, str(defaults.get(key, "0")) if defaults else "0")

            if checkbox_options and key in checkbox_options and isinstance(widget, QCheckBox):
                widget.setChecked(value == "1")
            elif color_labels and key in color_labels and isinstance(widget, QLabel):
                if not value or value == "0":
                    value = default_colors.get(key, "000000") if default_colors else "000000"
                    logger.info(f"Using default value for {key}: {value}")
                widget.setStyleSheet(f"background-color: #{value}; border: 1px solid black;")
                palette = widget.palette()
                palette.setColor(QPalette.ColorRole.Window, QColor(f"{value}"))
            elif isinstance(widget, QLineEdit):
                widget.setText(value)
            elif isinstance(widget, QComboBox):
                widget.setCurrentIndex(int(value) if value.isdigit() else 0)

            logger.info(f"Loading {key}: {value}")

        logger.info(f"=== {section} Options loaded ===")
        return widgets

    def prepare_updates(self, section, option_list, checkbox_options=None, color_labels=None):
        updates = {section: {}}
        for option in option_list:
            widget = getattr(self.main_window.ui, option, None)
            if not widget:
                continue

            if checkbox_options and option in checkbox_options and isinstance(widget, QCheckBox):
                updates[section][option] = "1" if widget.isChecked() else "0"
            elif color_labels and option in color_labels and isinstance(widget, QLabel):
                style = widget.styleSheet()
                if "background-color:" in style:
                    updates[section][option] = style.split("background-color:")[-1].split(";")[0].strip().replace("#", "")
                else:
                    logger.warning(f"Color not found for Widget {option}. Skipping.")
            elif isinstance(widget, QLineEdit):
                updates[section][option] = widget.text()
            elif isinstance(widget, QComboBox):
                updates[section][option] = str(widget.currentIndex())

        return updates


DEFAULTS = {"Units": 0}
DEFAULT_COLORS = {
    "DefaultMaterialColor": "FF66B2",
    "ElementSelectColor": "0000FF",
    "ElementSelectLockedColor": "666699",
    "FillColor": "AABB99",
    "BackgroundColor": "888888"
}

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
