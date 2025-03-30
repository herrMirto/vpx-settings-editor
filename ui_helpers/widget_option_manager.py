from PySide6.QtWidgets import QCheckBox, QLineEdit
from utils import logger
from config.vpinball_ini import VPinballINI

ini = VPinballINI()

class WidgetOptionManager:
    def __init__(self, main_window):
        self.main_window = main_window

    def load_options(self, section, option_list, checkbox_options=None):
        logger.info(f"=== Loading {section} Options ===")

        widgets = {option: getattr(self.main_window.ui, option, None) for option in option_list}
        values = ini.get_section_subset(section, option_list)

        for key, widget in widgets.items():
            if not widget:
                logger.warning(f"Widget {key} not found in UI")
                continue

            value = values.get(key, "0")
            if checkbox_options and key in checkbox_options and isinstance(widget, QCheckBox):
                widget.setChecked(value == "1")
            elif isinstance(widget, QLineEdit):
                widget.setText(value)

            logger.info(f"Loading {key}: {value}")

        logger.info(f"=== {section} Options loaded ===")
        return widgets

    def prepare_updates(self, section, option_list, checkbox_options=None):
        updates = {section: {}}
        for option in option_list:
            widget = getattr(self.main_window.ui, option, None)
            if not widget:
                continue

            if checkbox_options and option in checkbox_options and isinstance(widget, QCheckBox):
                updates[section][option] = "1" if widget.isChecked() else "0"
            elif isinstance(widget, QLineEdit):
                updates[section][option] = widget.text()

        return updates
