"""
Utils for diff between original tab values and new values
"""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QDialogButtonBox,
                               QTableWidget, QTableWidgetItem,
                               QLabel, QSizePolicy)

def show_diff_table(original_ini, updates, parent=None):
    """ Display a dialog showing the differences between the original INI and the updates. """
    dialog = QDialog(parent)
    dialog.setWindowTitle("Configuration Changes Preview")
    dialog.resize(800, 600)
    layout = QVBoxLayout(dialog)

    label = QLabel("The following settings will be changed:")
    layout.addWidget(label)

    table = QTableWidget()
    table.setColumnCount(3)
    table.setHorizontalHeaderLabels(["Option", "Current Value", "New Value"])
    table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    diff_rows = []

    for section, options in updates.items():
        if not isinstance(options, dict):
            continue

        for key, new_value in options.items():
            current_value = original_ini.get_section_value(section, key, fallback="")

            current_value = str(current_value).strip()
            new_value = str(new_value).strip()

            if current_value == new_value:
                continue
            if (not current_value and new_value == "0") or (current_value == "0" and not new_value):
                continue

            diff_rows.append((f"{section}.{key}", current_value, new_value))

    table.setRowCount(len(diff_rows))
    for row, (option, current, new) in enumerate(diff_rows):
        for col, value in enumerate([option, current, new]):
            item = QTableWidgetItem(value)
            item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            table.setItem(row, col, item)

    table.resizeColumnsToContents()
    layout.addWidget(table)

    buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
    buttons.accepted.connect(dialog.accept)
    buttons.rejected.connect(dialog.reject)
    layout.addWidget(buttons)

    return dialog.exec() == QDialog.Accepted