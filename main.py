# This Python file uses the following encoding: utf-8
import os
import json
import sys
import re
import subprocess
import platform
from urllib.request import urlopen
from urllib.parse import urlparse
from PySide6.QtWidgets import QApplication, QWidget, QLabel, QTableWidgetItem, QTableWidget, QVBoxLayout, QPushButton
from PySide6.QtGui import QIcon, Qt
from utils import logger
from tooltips import TOOLTIPS,apply_tooltips
from config.vpinball_bin import VPinballBin
from ui_helpers.layout_editor import LayoutEditorWindow
from version import __version__

# Important:
# You need to run the following command to generate the ui_form.py file
#     pyside6-uic form.ui -o ui_form.py, or
#     pyside2-uic form.ui -o ui_form.py
import assets_rc
from ui_form import Ui_Widget
from ui.audio_options import load_audio_options, on_save_audio_clicked
from ui.buttons_options import load_buttons_options, on_save_buttons_clicked
from ui.editor_options import load_editor_options, on_save_editor_clicked
from ui.global_options import load_global_options, on_save_global_clicked
from ui.nudge_and_dof_options import load_nudge_dof_options, on_save_nudge_dof_clicked
from ui.pup_options import load_pup_options, on_save_pup_clicked
from ui.screens_options import load_screen_options, on_save_screen_clicked
from ui.video_options import save_video_options, load_video_options
from ui.vr_options import load_vr_options, on_save_vr_clicked
from ui_helpers.stereo_3d import setup_stereo3d_logic
from ui_helpers.setup_windowed_resolutions import setup_aspect_ratio_logic, get_playfield_mode
from ui_helpers.video_resolutions import get_display_resolutions, load_playfield_resolution
from ui_helpers.widget_option_manager import change_color
from tables_utils import (
    build_tables_meta,
    ensure_vpsdb,
)

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
        self.audio_widgets = load_audio_options(self)
        self.buttons_options = load_buttons_options(self)
        self.editor_options = load_editor_options(self)
        self.global_options = load_global_options(self)
        self.pup_config = load_pup_options(self)
        self.screen_options = load_screen_options(self)
        self.nudge_options = load_nudge_dof_options(self)
        self.vr_options = load_vr_options(self)
        self.editor_options = load_editor_options(self)
        self.video_options = load_video_options(self)

        # Setup Tables Tab
        self.setup_tables_tab()

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
        self.ButtonSaveAudioOptions.clicked.connect(lambda: on_save_audio_clicked(self))

        # Save Buttons Options
        self.ButtonSaveButtonsOptions = self.ui.ButtonSaveButtonsOptions
        self.ButtonSaveButtonsOptions.clicked.connect(lambda: on_save_buttons_clicked(self))

        # Save Global Options
        self.ButtonSaveGlobalOptions = self.ui.ButtonSaveGlobalOptions
        self.ButtonSaveGlobalOptions.clicked.connect(lambda: on_save_global_clicked(self))

        # Save Nudge and DOF Options
        self.ButtonSaveNudgeDOFOptions = self.ui.ButtonSaveNudgeDOFOptions
        self.ButtonSaveNudgeDOFOptions.clicked.connect(lambda: on_save_nudge_dof_clicked(self))

         # Save Editor button
        self.ButtonSaveEditorOptions = self.ui.ButtonSaveEditorOptions
        self.ButtonSaveEditorOptions.clicked.connect(lambda: on_save_editor_clicked(self))

        # Save PUP config button
        self.ButtonSavePUPOptions = self.ui.ButtonSavePUPOptions
        self.ButtonSavePUPOptions.clicked.connect(lambda: on_save_pup_clicked(self))

        # Save Screen Configurations
        self.SaveScreenOptionsButton = self.ui.SaveScreenOptions_Button
        self.SaveScreenOptionsButton.clicked.connect(lambda: on_save_screen_clicked(self))

        # Save Video Options button
        self.ButtonSaveVideoOptions = self.ui.ButtonSaveVideoOptions
        self.ButtonSaveVideoOptions.clicked.connect(lambda: save_video_options(self))

        # Save VR config button
        self.ButtonSaveVROptions = self.ui.ButtonSaveVROptions
        self.ButtonSaveVROptions.clicked.connect(lambda: on_save_vr_clicked(self))

        # Setup Low EndPC Options
        self.ButtonLowEndPCOptions = self.ui.ButtonLowEndPC
        self.ButtonLowEndPCOptions.clicked.connect(self.setup_low_end_pc)

        # Setup Low EndPC Options
        self.ButtonHighEndPCOptions = self.ui.ButtonHighEndPC
        self.ButtonHighEndPCOptions.clicked.connect(self.setup_high_end_pc)

        # Setup Screens Button
        self.ButtonSetupScreens = self.ui.ButtonSetupScreens
        self.ButtonSetupScreens.clicked.connect(self.showScreensSetup)

         # Setup Screens Button
        self.ButtonSetupPUPScreens = self.ui.ButtonSetupPUPScreens
        self.ButtonSetupPUPScreens.clicked.connect(self.showPUPScreensSetup)

        self.window_index = get_playfield_mode()
        if self.window_index:
            logger.info(f"Ratio resolution: {self.window_index}")
            self.ui.WindowMode.setChecked(True)
            self.ui.AspectRatio.setCurrentIndex(int(self.window_index))
            logger.info("Window Mode Enabled for Playfield")

        # Tooltips
        apply_tooltips(self, TOOLTIPS)
        self.ui.LabelAppVersion.setText(f"App version: {__version__}")

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
        self.ui.LabelSoundVolumeNumber.setText(str(value))

    def update_snd_backglass_label(self, value):
        self.ui.LabelMusicVolumeNumber.setText(str(value))

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

    def apply_screen_positions(self, data):
        for key, value in data.items():
            widget = self.findChild(QWidget, key)
            if widget:
                if hasattr(widget, "setText"):
                    widget.setText(str(value))
                elif hasattr(widget, "setValue"):
                    widget.setValue(int(value))
        logger.info(f"Screen positions updated: {data}")

    def setup_low_end_pc(self):
        self.ui.SyncMode.setCurrentIndex(2)
        self.ui.MaxFramerate.setText("0")
        self.ui.MaxPrerenderedFrames.setText("0")
        self.ui.FXAA.setCurrentIndex(0)
        self.ui.Sharpen.setCurrentIndex(0)
        self.ui.ScaleFXDMD.setChecked(False)
        self.ui.MaxAmbientOcclusion.setCurrentIndex(2)
        self.ui.SSRefl.setText("0")
        self.ui.PFReflection.setCurrentIndex(0)
        self.ui.MaxTexDimension.setCurrentIndex(0)
        self.ui.AAFactor.setCurrentIndex(0)
        self.ui.MSAASamples.setCurrentIndex(0)
        self.ui.UseNVidiaAPI.setChecked(True)
        self.ui.ForceBloomOff.setChecked(False)
        self.ui.ForceAnisotropicFiltering.setChecked(False)
        self.ui.CompressTextures.setChecked(False)
        self.ui.SoftwareVertexProcessing.setChecked(False)
        self.ui.AlphaRampAccuracy.setValue(5)

    def setup_high_end_pc(self):
        self.ui.SyncMode.setCurrentIndex(3)
        self.ui.MaxFramerate.setText("0")
        self.ui.MaxPrerenderedFrames.setText("0")
        self.ui.FXAA.setCurrentIndex(2)
        self.ui.Sharpen.setCurrentIndex(2)
        self.ui.ScaleFXDMD.setChecked(False)
        self.ui.MaxAmbientOcclusion.setCurrentIndex(0)
        self.ui.SSRefl.setText("1")
        self.ui.PFReflection.setCurrentIndex(2)
        self.ui.MaxTexDimension.setCurrentIndex(0)
        self.ui.AAFactor.setCurrentIndex(0)
        self.ui.MSAASamples.setCurrentIndex(0)
        self.ui.UseNVidiaAPI.setChecked(False)
        self.ui.ForceBloomOff.setChecked(False)
        self.ui.ForceAnisotropicFiltering.setChecked(True)
        self.ui.CompressTextures.setChecked(False)
        self.ui.SoftwareVertexProcessing.setChecked(False)
        self.ui.AlphaRampAccuracy.setValue(10)

    def showScreensSetup(self):
        screens = QApplication.screens()
        self.screens_setup_window = LayoutEditorWindow(screens, mode="screens", parent=self)
        self.screens_setup_window.positionsSaved.connect(self.apply_screen_positions)
        self.screens_setup_window.show()

    def showPUPScreensSetup(self):
        screens = QApplication.screens()
        self.screens_setup_window = LayoutEditorWindow(screens, mode="pup", parent=self)
        self.screens_setup_window.positionsSaved.connect(self.apply_screen_positions)
        self.screens_setup_window.show()

    # ----- Tables Tab Logic -----
    def load_tables_meta(self):
        try:
            with open("/Users/andremichi/.vpx_settings_editor/tables_meta.json", "r", encoding="utf-8") as f:
                return json.load(f).get("tables", {})
        except Exception as e:
            logger.error(f"Failed to load tables_meta.json: {e}")
            return {}
    
    def setup_tables_tab(self):
        self.tables_tab = QWidget()
        layout = QVBoxLayout(self.tables_tab)
        self.tables_table = QTableWidget()
        self.tables_table.setColumnCount(12)
        self.tables_table.setHorizontalHeaderLabels([
            "Table", "VPS ID", "Standalone Patch", "Action",  # já existentes
            "ROM", "NFozzy", "LUT", "Scorebit", "Fleep", "SSF", "FastFlips", "FlexDMD"
        ])
        layout.addWidget(self.tables_table)
        self.rescan_button = QPushButton("Re-scan Tables")
        self.rescan_button.clicked.connect(self.rescan_tables)
        layout.addWidget(self.rescan_button)
        self.ui.tabWidget.addTab(self.tables_tab, "Tables")
        self.load_tables()


    def load_tables(self):
        self.table_meta = self.load_tables_meta()

        if not self.table_meta:
            logger.info("tables_meta.json not found or empty. Rebuilding...")
            _, ts = ensure_vpsdb()
            db_entries, ts = ensure_vpsdb(ts)
            build_tables_meta(db_entries)
            self.table_meta = self.load_tables_meta()

        self.populate_tables()

    def populate_tables(self):
        self.tables_table.setRowCount(0)
        for row, (name, info) in enumerate(sorted(self.table_meta.items())):
            self.tables_table.insertRow(row)
            self.tables_table.setItem(row, 0, QTableWidgetItem(name))
            self.tables_table.setItem(row, 1, QTableWidgetItem(info.get("vps_id", "")))
    
            patch_status = "Patched" if info.get("vbs_patch_applied") == "yes" else (
                "Needs Patch" if info.get("vbs_patch") == "yes" else "N/A"
            )
            self.tables_table.setItem(row, 2, QTableWidgetItem(patch_status))
    
            if info.get("vbs_patch") == "yes" and info.get("vbs_patch_applied") != "yes":
                patch_entry = self.get_patch_entry(info.get("vbs_sha256"))
                if patch_entry:
                    btn = QPushButton("Apply Patch")
                    btn.clicked.connect(lambda _, i=info, u=patch_entry["url"]: self.apply_patch(i, u))
                    self.tables_table.setCellWidget(row, 3, btn)
                else:
                    self.tables_table.setItem(row, 3, QTableWidgetItem(""))
            else:
                self.tables_table.setItem(row, 3, QTableWidgetItem(""))
    
            # Colunas extras
            extras = [
                "rom", "detectNfozzy", "detectLut", "detectScorebit",
                "detectFleep", "detectSSF", "detectFastflips", "detectFlex"
            ]
            for col_offset, key in enumerate(extras, start=4):
                val = info.get(key, "")
                if val == "true":
                    val = "✅"
                elif val == "false":
                    val = "❌"
                self.tables_table.setItem(row, col_offset, QTableWidgetItem(val))

    def get_patch_url(self, sha256):
        from tables_utils import load_patch_hashes
        patch_map = load_patch_hashes()
        return patch_map.get(sha256)

    def rescan_tables(self):
        _, ts = ensure_vpsdb()
        db_entries, ts = ensure_vpsdb(ts)
        build_tables_meta(db_entries)  # Isso recria tables_meta.json
        self.load_tables()
    
    def get_patch_entry(self, sha256):
        from tables_utils import load_patch_hashes
        patch_map = load_patch_hashes()
        return patch_map.get(sha256)

    def apply_patch(self, table_info, patch_url):
        try:
            data = urlopen(patch_url).read()
            parsed = urlparse(patch_url)
            dest = os.path.join(os.path.dirname(table_info["path"]), os.path.basename(parsed.path))
            with open(dest, "wb") as f:
                f.write(data)

            # Atualiza tables_meta.json em memória
            name = os.path.basename(table_info["path"])
            self.table_meta[name]["vbs_patch_applied"] = "yes"

            # Salva novamente
            with open("/Users/andremichi/.vpx_settings_editor/tables_meta.json", "w", encoding="utf-8") as f:
                json.dump({"tables": self.table_meta}, f, indent=2, ensure_ascii=False)

            self.load_tables()
        except Exception as e:
            logger.error(f"Failed to apply patch: {e}")


if __name__ == "__main__":
    if "--version" in sys.argv:
        print(f"vpx-settings-editor {__version__}")
        sys.exit(0)

    app = QApplication(sys.argv)
    widget = Widget()
    widget.show()
    sys.exit(app.exec())
