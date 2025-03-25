import logging
import os
from PySide6.QtWidgets import QMessageBox

def show_save_message(text_msg):
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Icon.Information)
    msg.setWindowTitle("Success")
    msg.setText(text_msg)
    msg.setStandardButtons(QMessageBox.StandardButton.Ok)
    msg.exec()

log_dir = os.path.join(os.path.expanduser("~"), ".vpx_settings_editor")
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

log_file = os.path.join(log_dir, "application.log")

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_file, encoding="utf-8"),  
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("VPX_SETTINGS_EDITOR")