import re
import platform
from PySide6.QtWidgets import QCheckBox, QComboBox, QLineEdit, QSlider
from PySide6.QtGui import QGuiApplication
from config.vpinball_ini import VPinballINI
from config.vpinball_bin import VPinballBin
from ui_helpers.setup_windowed_resolutions import get_aspect_ratio_index_from_resolution
from utils import show_save_message, logger

ini = VPinballINI()
vpx_path = VPinballBin().get_filepath()

VIDEO_OPTIONS = [
    "AltColor",
    "BGSet",
    "SyncMode",
    "MaxFramerate",
    "MaxPrerenderedFrames",
    "FXAA",
    "Sharpen",
    "ScaleFXDMD",
    "SSRefl",
    "PFReflection",
    "MaxTexDimension",
    "AAFactor",
    "MSAASamples",
    "UseNVidiaAPI",
    "ForceBloomOff",
    "ForceAnisotropicFiltering",
    "CompressTextures",
    "SoftwareVertexProcessing",
    "GfxBackend",
    "Stereo3D",
    #"Stereo3DEnabled",
    "Stereo3DFake",
    "Stereo3DBrightness",
    "Stereo3DSaturation",
    #"Stereo3DDefocus",
    "Stereo3DEyeSeparation",
    #"Stereo3DYAxis",
    "Stereo3DOffset",
    #"Stereo3DMaxSeparation",
    "Stereo3DZPD",
    "DisableLightingForBalls",
    "BallAntiStretch",
    "OverwriteBallImage",
    "BallImage",
    "DecalImage",
    "BallTrail",
    "BallTrailStrength",
    "OverrideTableEmissionScale",
    "EmissionScale",
    "DynamicDayNight",
    "Latitude",
    "Longitude",
    "NudgeStrength",
    "AlphaRampAccuracy",
    #"NumberOfTimesToShowTouchMessage",
    #"TouchOverlay",
    #"CacheMode",
    "ScreenWidth",
    "ScreenHeight",
    "ScreenInclination",
    "ScreenPlayerX",
    "ScreenPlayerY",
    "ScreenPlayerZ",
    "BAMHeadTracking",
    "MaxAmbientOcclusion"
]

MSAA_MAPPING = {
    0: "0",
    1: "4",
    2: "6",
    3: "8",
}

AAFACTOR_MAPPING_SAVING = {
    0: "1.000000",
    1: "0.500000", #50%",
    2: "0.750000", #75%",
    3: "1.250000", #125%",
    4: "1.330000", #133%",
    5: "1.500000", #150%",
    6: "1.750000", #175%",
    7: "2.000000", #200%
}

AAFACTOR_MAPPING_LOADING = {
    "1.000000": 0,
    "0.500000": 1, 
    "0.750000": 2, 
    "1.250000": 3, 
    "1.330000": 4, 
    "1.500000": 5, 
    "1.750000": 6, 
    "2.000000": 7
} 


DEFAULTS = {
    "SyncMode": 3,
    "BGSet": 0,
    "SyncMode": 3,
    "MaxTexDimension": 0,
    "MaxReflectionMode": 0,
    "MSAASamples": 1,
    "AAFactor": 1,
    "FXAA": 2,
    "Sharpen": 0,
    "MaxAmbientOcclusion": 2,
    "NvidiaAPI": 0,
}

def save_video_options(main_window):
    display_value = main_window.ui.ComboBox_displays_list.currentText()
    resolution_value = [item.text() for item in main_window.ui.TextBox_display_resolutions.selectedItems()]
    display_id = display_value.split(" ")[1]
    num_screens = main_window.ui.ComboBox_displays_list.count()

    if main_window.ui.WindowMode.isChecked():
        # Window Mode
        aspect_ratio = main_window.ui.AspectRatio.currentText()
        logger.info(aspect_ratio)
        playfield_width = main_window.ui.PlayfieldWidth_Windowed.text()
        playfield_height = main_window.ui.PlayfieldHeight_Windowed.text()
        playfield_fullscreen = 0
        playfield_refresh_rate = ini.get_section_value("Player", "PlayfieldRefreshRate")
        playfield_color_depth = ini.get_section_value("Player", "PlayfieldColor")
        if num_screens == 1:
            display_idx = 0
    else:
        pattern = r'(\d+)\s*x\s*(\d+)\s*\((\d+(?:\.\d+)?)\s*Hz.*depth=(\d+)\)'
        match = re.search(pattern, resolution_value[0])
        playfield_width = match.group(1)
        playfield_height = match.group(2)
        playfield_refresh_rate = match.group(3)
        playfield_color_depth = match.group(4)
        playfield_fullscreen = 1
        if num_screens == 1:
            display_idx = 0
    
    logger.info(f"Selected display: {display_id}")
    screens = QGuiApplication.screens()

    dpi_scale = screens[int(display_idx)].devicePixelRatio()

    if dpi_scale >= 2.0:
        playfield_width = int(playfield_width) // 2
        playfield_height = int(playfield_height) // 2

    if platform.system() == "Darwin":
        playfield_fullscreen = 0

    PLAYFIELD_OPTIONS = {
        "PlayfieldFullScreen": playfield_fullscreen,
        "PlayfieldDisplay": display_id,
        "PlayfieldWidth": playfield_width,
        "PlayfieldHeight": playfield_height,
        "PlayfieldColorDepth": playfield_color_depth,
        "PlayfieldRefreshRate": playfield_refresh_rate
    }

    # The Playfield options are not part of the GUI at the moment
    for playfield_opt in PLAYFIELD_OPTIONS:
        ini.update_section_subset("Player", {playfield_opt: str(PLAYFIELD_OPTIONS[playfield_opt])})
        logger.info(f"Saving {playfield_opt}: {PLAYFIELD_OPTIONS[playfield_opt]}")

    video_widgets = {}
    for option in VIDEO_OPTIONS:
        video_widgets[option] = getattr(main_window.ui, option)

    for widget in video_widgets:
        widget_element = video_widgets[widget]

        if isinstance(widget_element, QCheckBox): 
            widget_value = "1" if widget_element.isChecked() else "0"
            ini.update_section_subset("Player", {widget: widget_value})
            logger.info(f"Saving {widget}: {widget_value}")

        elif isinstance(widget_element, QComboBox):  
            selected_text = widget_element.currentIndex()

            if widget == "MaxTexDimension":
                selected_value = widget_element.currentText()
                if selected_value == "Unlimited":
                    ini.update_section_subset("Player", {widget: "0"})
                else:
                    ini.update_section_subset("Player", {widget: selected_value})
                logger.info(f"Saving {widget}: {selected_value}")

            elif widget == "AAFactor":
                aa_factor_value = AAFACTOR_MAPPING_SAVING[(widget_element.currentIndex())]
                ini.update_section_subset("Player", {widget: aa_factor_value})
                logger.info(f"Saving {widget}: {aa_factor_value}")

            elif widget == "Stereo3D":
                stero_3d_combo_value = widget_element.currentText()
                if stero_3d_combo_value != 'Disabled':
                    ini.update_section_subset("Player", {"Stereo3DEnabled": "1"})
                    logger.info(f"Saving Stereo3DEnabled: 1")
                else:
                    ini.update_section_subset("Player", {"Stereo3DEnabled": "0"})
                    logger.info(f"Saving Stereo3DEnabled: 0")

            elif widget == "MaxAmbientOcclusion":
                logger.info(f"Selected MaxAmbientOcclusion: {selected_text}")
                selected_value = widget_element.currentIndex()
                logger.info(f"Selected MaxAmbientOcclusion: {selected_value}")
                if selected_value == 0:  
                    ini.update_section_subset("Player", {"DynamicAO": "1"})
                    ini.update_section_subset("Player", {"DisableAO": "0"})
                    logger.info("Saving DynamicAO: 1")
                    logger.info("Saving DisableAO: 0")
                elif selected_value == 1:  
                    ini.update_section_subset("Player", {"DisableAO": "1"})
                    ini.update_section_subset("Player", {"DynamicAO": "0"})
                    logger.info("Saving DisableAO: 1")
                    logger.info("Saving DynamicAO: 0")
                elif selected_value == 2: 
                    ini.update_section_subset("Player", {"DisableAO": "0"})
                    ini.update_section_subset("Player", {"DynamicAO": "0"})
                    logger.info("Saving DisableAO: 0")
                    logger.info("Saving DynamicAO: 0")
            else:
                widget_value = widget_element.currentIndex()
                ini.update_section_subset("Player", {widget: widget_value})
                logger.info(f"Saving {widget}: {widget_value}")

        elif isinstance(widget_element, QLineEdit):
            widget_value = widget_element.text()
            ini.update_section_subset("Player", {widget: widget_value})
            logger.info(f"Saving {widget}: {widget_value}")
        elif isinstance(widget_element, QSlider):
            widget_value = widget_element.value()
            ini.update_section_subset("Player", {widget: widget_value})
            logger.info(f"Saving {widget}: {widget_value}")
    try:
        ini.save()
        logger.info("=== Video Options Saved ===")
        show_save_message("Video Options Saved")
    except Exception as save_audio_options_error:
        logger.error(f"Video saving Audio Options: \n {save_audio_options_error}")
        show_save_message("Error saving Video Options")

def load_video_options(main_window):
    
    """Load Video Options from VPinballX.ini"""
    logger.info("=== Loading Video Options ===")
    
    values_player = ini.get_section_subset("Player", VIDEO_OPTIONS)

    for option in VIDEO_OPTIONS:
        widget = getattr(main_window.ui, option, None)
        if not widget:
            continue

        value = values_player.get(option, str(DEFAULTS.get(option, "0")))

        if isinstance(widget, QCheckBox):
            widget.setChecked(value == "1")

        elif isinstance(widget, QSlider):
            if option in ["EmissionScale"]:
                if not value.isdigit():
                    value = 0

            if option in ["AlphaRampAccuracy"]:
                if not value.isdigit():
                    value = 10

            widget.setValue(int(value))

        elif isinstance(widget, QComboBox):
            if option == "AAFactor":
                value = values_player.get('AAFactor')
                index_value = AAFACTOR_MAPPING_LOADING[value] if value.isdigit() else 0
                widget.setCurrentIndex(index_value)
            elif option == "FXAA":
                value = values_player.get("FXAA")
                value = 2 if not value else value
                widget.setCurrentIndex(int(value))
            elif option == "SyncMode":
                value = values_player.get("SyncMode")
                logger.info(value)
                value = 3 if not value else value
                widget.setCurrentIndex(int(value))
            else:
                widget.setCurrentIndex(int(value) if value.isdigit() else 0)

        elif isinstance(widget, QLineEdit):
            widget.setText(value)

        logger.info(f"Loading {option}: {value}")
    ao_widget = getattr(main_window.ui, "MaxAmbientOcclusion", None)
    dynamic = ini.get_section_value("Player", "DynamicAO")
    disable = ini.get_section_value("Player", "DisableAO")
    if not dynamic and not disable:
        logger.info("DisableAO and DinamycAO not set. Assuming default StaticAO")
        ao_widget.setCurrentIndex(2)
    elif dynamic == "0" and disable == "0":
        logger.info("DisableAO and DinamycAO set to 0. Using StaticAO")
        ao_widget.setCurrentIndex(2)
    elif dynamic == "1" and not disable or disable == "0":
        logger.info(f"Dynamic is set: disable: {disable}, dynamic: {dynamic}")
        ao_widget.setCurrentIndex(0)
    elif disable == "1" and not dynamic or dynamic == "0":
        logger.info(f"Disable is set: disable: {disable}, dynamic: {dynamic}")
        ao_widget.setCurrentIndex(1)
    

    logger.info("=== Video Options loaded ===")
