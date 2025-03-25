# This Python file uses the following encoding: utf-8
import os
import sys
import re
import subprocess
import platform
from PySide6.QtWidgets import QApplication, QWidget, QLabel
from PySide6.QtGui import QIcon
from utils import logger
from tooltips import TOOLTIPS,apply_tooltips
from config.vpinball_bin import VPinballBin

# Important:
# You need to run the following command to generate the ui_form.py file
#     pyside6-uic form.ui -o ui_form.py, or
#     pyside2-uic form.ui -o ui_form.py
import assets_rc
from ui_form import Ui_Widget
from ui.audio_options import load_audio_config, save_audio_options
from ui.buttons_options import load_buttons_options, save_buttons_options
from ui.editor_options import change_color, load_editor_options, save_editor_options
from ui.global_options import load_global_options, save_global_options
from ui.nudge_and_dof_options import load_nudge_dof_options, save_nudge_dof_options
from ui.pup_options import load_pup_config, save_pup_options
from ui.screens_options import load_screen_options, save_screen_options
from ui.video_options import save_video_options, load_video_options
from ui.vr_options import load_vr_options, save_vr_options
from ui_helpers.stereo_3d import setup_stereo3d_logic
from ui_helpers.setup_windowed_resolutions import setup_aspect_ratio_logic, get_playfield_mode
from ui_helpers.video_resolutions import get_display_resolutions, load_playfield_resolution

class Widget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        app_icon = QIcon(":/icon.png")
        app.setWindowIcon(app_icon)
        self.ui = Ui_Widget()
        self.ui.setupUi(self)

         ## Audio Slider
        self.ui.Player_SoundVolume.valueChanged.connect(self.update_snd_playfield_label)
        self.ui.Player_MusicVolume.valueChanged.connect(self.update_snd_backglass_label)

        vpx_path = VPinballBin().get_filepath()

        # Get available sound devices
        self.vpx_snd_output = subprocess.run(f"{vpx_path} -listsnd", shell=True, capture_output=True)
        self.snd_pattern = r'name=([^,]+)'
        self.audio_devices = re.findall(self.snd_pattern, str(self.vpx_snd_output.stdout))
        # Populate Sound Devices
        self.ui.Player_SoundDevice.addItems(self.audio_devices)
        self.ui.Player_SoundDeviceBG.addItems(self.audio_devices)

        # Disable Window Mode on MacOS
        if platform.system() == 'Darwin':
            self.ui.WindowMode.setDisabled(True)

        # Load configurations
        self.audio_widgets = load_audio_config(self)
        self.buttons_options = load_buttons_options(self)
        self.editor_options = load_editor_options(self)
        self.global_options = load_global_options(self)
        self.pup_config = load_pup_config(self)
        self.screen_options = load_screen_options(self)
        self.nudge_options = load_nudge_dof_options(self)
        self.vr_options = load_vr_options(self)
        self.editor_options = load_editor_options(self)
        self.video_options = load_video_options(self)

        self.setup_color_labels()
        setup_stereo3d_logic(
            self.ui.Stereo3D,
            self.ui.Stereo3DFake,
            self.ui.Stereo3DEyeSeparation,
            self.ui.Anaglyph6Filter,
            self.ui.Stereo3DBrightness,
            self.ui.Stereo3DSaturation,
            self.ui.Stereo3DZPD,
            self.ui.Stereo3DOffset,
        )

        # Debug
        self.ui.ShowLogButton.clicked.connect(self.load_log)
        self.ui.ClearLogButton.clicked.connect(self.clear_logs)
        self.ui.ShowAppLogButton.clicked.connect(self.load_app_log)

        # Logic for video options
        self.ui.radio_Fullscreen.toggled.connect(self.toggleWidgets)
        self.ui.WindowMode.toggled.connect(self.toggleWidgets)

        self.ui.radio_Fullscreen.setChecked(True)
        self.ui.video_opts_widget.setCurrentIndex(0)

        # Get VPX Version
        self.vpx_version = subprocess.run(f"{vpx_path} -v", shell=True, capture_output=True)
        self.vpx_version_pattern = r'(Visual Pinball.*\))'
        self.vpx_version_res = re.search(self.vpx_version_pattern, str(self.vpx_version.stdout))
        if self.vpx_version_res:
            self.ui.vpxVersion.setText(str(self.vpx_version_res.group(1)))
        else:
            self.ui.vpxVersion.setText(str("Unknown version"))

        # Get available displays
        self.displays_info = get_display_resolutions()
        self.ui.ComboBox_displays_list.addItems(self.displays_info.keys())
        self.ui.ComboBox_displays_list.currentIndexChanged.connect(self.update_display_info)
        self.update_display_info()
        load_playfield_resolution(resolution_widget=self.ui.TextBox_display_resolutions, available_resolutions=self.displays_info)

        # Populate Window Mode Combobox
        def populate_window_mode(self):
            defined_ratios = [
                "Free",
                "4:3 (Landscape)",
                "16:10 (Landscape)",
                "16:9 (Landscape)",
                "21:10 (Landscape)",
                "21:9 (Landscape)",
                "4:3 (Portrait)", 
                "16:10 (Portrait)",
                "16:9 (Portrait)",
                "21:10 (Portrait)",
                "21:9 (Portrait)"
            ]
            self.ui.AspectRatio.addItems(defined_ratios)
        populate_window_mode(self)
        setup_aspect_ratio_logic(
            self.ui.AspectRatio,
            self.ui.PlayfieldWidth_Windowed,
            self.ui.PlayfieldHeight_Windowed
        )
        # Save Audio config button
        self.ButtonSaveAudioOptions = self.ui.ButtonSaveAudioOptions
        self.ButtonSaveAudioOptions.clicked.connect(lambda: save_audio_options(self))

        # Save Buttons Options
        self.ButtonSaveButtonsOptions = self.ui.ButtonSaveButtonsOptions
        self.ButtonSaveButtonsOptions.clicked.connect(lambda: save_buttons_options(self))

        # Save Global Options
        self.ButtonSaveGlobalOptions = self.ui.ButtonSaveGlobalOptions
        self.ButtonSaveGlobalOptions.clicked.connect(lambda: save_global_options(self))

        # Save Nudge and DOF Options
        self.ButtonSaveNudgeDOFOptions = self.ui.ButtonSaveNudgeDOFOptions
        self.ButtonSaveNudgeDOFOptions.clicked.connect(lambda: save_nudge_dof_options(self))

         # Save Editor button
        self.ButtonSaveEditorOptions = self.ui.ButtonSaveEditorOptions
        self.ButtonSaveEditorOptions.clicked.connect(lambda: save_editor_options(self))

        # Save PUP config button
        self.ButtonSavePUPOptions = self.ui.ButtonSavePUPOptions
        self.ButtonSavePUPOptions.clicked.connect(lambda: save_pup_options(self))

        # Save Screen Configurations
        self.SaveScreenOptionsButton = self.ui.SaveScreenOptions_Button
        self.SaveScreenOptionsButton.clicked.connect(lambda: save_screen_options(self))

        # Save Video Options button
        self.ButtonSaveVideoOptions = self.ui.ButtonSaveVideoOptions
        self.ButtonSaveVideoOptions.clicked.connect(lambda: save_video_options(self))

        # Save VR config button
        self.ButtonSaveVROptions = self.ui.ButtonSaveVROptions
        self.ButtonSaveVROptions.clicked.connect(lambda: save_vr_options(self))

        self.window_index = get_playfield_mode()
        if self.window_index:
            logger.info(f"Ratio resolution: {self.window_index}")
            self.ui.WindowMode.setChecked(True)
            self.ui.AspectRatio.setCurrentIndex(int(self.window_index))
            logger.info("Window Mode Enabled for Playfield")

        # Tooltips
        apply_tooltips(self, TOOLTIPS)


    def toggleWidgets(self):
        if self.ui.radio_Fullscreen.isChecked():
            self.ui.video_opts_widget.setCurrentIndex(0)
        else:
            self.ui.video_opts_widget.setCurrentIndex(1) if platform.system() != 'Darwin' else self.ui.WindowMode.setDisabled(True)

    def update_display_info(self):
        selected_display = self.ui.ComboBox_displays_list.currentText()
        resolutions = self.displays_info.get(selected_display, [])
        self.ui.TextBox_display_resolutions.clear()
        self.ui.TextBox_display_resolutions.addItems(resolutions)
        self.ui.TextBox_display_resolutions.setCurrentRow(0)

    
    # Handle colours from the editor
    def setup_color_labels(self):
        color_labels = [
            "DefaultMaterialColor",
            "ElementSelectColor",
            "ElementSelectLockedColor",
            "FillColor",
            "BackgroundColor"
        ]

        for label_name in color_labels:
            label_widget = getattr(self.ui, label_name, None)
            if isinstance(label_widget, QLabel):
                label_widget.mousePressEvent = lambda event, lbl=label_name: change_color(self, lbl)


    def update_snd_playfield_label(self, value):
        self.ui.playfld_snd_label.setText(str(value))

    def update_snd_backglass_label(self, value):
        self.ui.backglass_snd_label.setText(str(value))

    def load_log(self):
        log_path = os.path.expanduser("~/.vpinball/vpinball.log")
        if os.path.exists(log_path):
            with open(log_path, "r", encoding="utf-8", errors="replace") as file:
                log_content = file.read()
                self.ui.LogtextBrowser.setPlainText(log_content)
        else:
            logger.error("Log file not found.")
            self.ui.LogtextBrowser.setPlainText("Log file not found.")

    def load_app_log(self):
        log_path = os.path.expanduser("~/.vpx_settings_editor/application.log")
        if os.path.exists(log_path):
            with open(log_path, "r", encoding="utf-8", errors="replace") as file:
                log_content = file.read()
                self.ui.LogtextBrowser.setPlainText(log_content)
        else:
            logger.error("Log file not found.")
            self.ui.LogtextBrowser.setPlainText("Log file not found.")

    def clear_logs(self):
        self.ui.LogtextBrowser.setPlainText("")

    

if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = Widget()
    widget.show()
    sys.exit(app.exec())
