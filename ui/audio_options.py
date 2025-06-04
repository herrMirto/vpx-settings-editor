from ui_helpers.widget_option_manager import WidgetOptionManager
from ui_helpers.widget_diffs import show_diff_table
from config.vpinball_ini import VPinballINI
from utils import logger, show_save_message

ini = VPinballINI()

AUDIO_OPTIONS = {
    "Player": [
        "PlayMusic",
        "PlaySound",
        "SoundDevice",
        "SoundDeviceBG"
    ],
    "Standalone": [
        "AltSound"
    ]
}

def load_audio_options(main_window):
    manager = WidgetOptionManager(main_window)
    for section, options in AUDIO_OPTIONS.items():
        manager.load_options(section, options)

    # Carregar Sound3D (lista de checkboxes)
    values = ini.get_section_subset("Player", ["Sound3D"])
    index_value = values.get("Sound3D", "0")
    try:
        index = int(index_value)
    except (TypeError, ValueError):
        index = 0

    if hasattr(main_window.ui, f"Player_Sound3D_{index}"):
        getattr(main_window.ui, f"Player_Sound3D_{index}").setChecked(True)

    # Carregar Sliders
    #sound_volume = ini.get_section_value("Player", "SoundVolume", "100")
    sound_volume = ini.get_section_value("Player", "SoundVolume") or "0"
    music_volume = ini.get_section_value("Player", "MusicVolume") or "0"


    #music_volume = ini.get_section_value("Player", "MusicVolume", "100")

    main_window.ui.Player_SoundVolume.setValue(int(sound_volume))
    main_window.ui.Player_MusicVolume.setValue(int(music_volume))
    main_window.ui.LabelSoundVolumeNumber.setText(sound_volume)
    main_window.ui.LabelMusicVolumeNumber.setText(music_volume)

    logger.info("=== Audio Options loaded ===")

def prepare_audio_updates(main_window):
    manager = WidgetOptionManager(main_window)
    updates = {}

    for section, options in AUDIO_OPTIONS.items():
        updates.update(manager.prepare_updates(section, options))

    # Preparar Sound3D
    sound3d_buttons = [
        main_window.ui.Player_Sound3D_0,
        main_window.ui.Player_Sound3D_1,
        main_window.ui.Player_Sound3D_2,
        main_window.ui.Player_Sound3D_3,
        main_window.ui.Player_Sound3D_4,
        main_window.ui.Player_Sound3D_5
    ]
    index = next((i for i, btn in enumerate(sound3d_buttons) if btn.isChecked()), 0)
    updates["Player"] = updates.get("Player", {})
    updates["Player"]["Sound3D"] = str(index)

    # Preparar Sliders
    updates["Player"]["SoundVolume"] = str(main_window.ui.Player_SoundVolume.value())
    updates["Player"]["MusicVolume"] = str(main_window.ui.Player_MusicVolume.value())

    return updates

def on_save_audio_clicked(main_window):
    updates = prepare_audio_updates(main_window)
    if show_diff_table(ini, updates, parent=main_window):
        for section, values in updates.items():
            ini.update_section_subset(section, values)
        try:
            ini.save()
            logger.info("=== Audio Options Saved ===")
            show_save_message("Audio Options Saved")
        except Exception as e:
            logger.error(f"Error saving Audio Options: {e}")
            show_save_message("Error saving Audio Options")


#from utils import show_save_message, logger
#from config.vpinball_ini import VPinballINI
#from PySide6.QtWidgets import QCheckBox, QComboBox, QLineEdit, QSlider
#
#ini = VPinballINI()
#
#def load_audio_config(main_window):
#    """Load Audio options from VPinballX.ini"""
#    logger.info("=== Loading Audio Options ===")
#
#    widgets = {
#        "Player": {
#            "SoundDevice": main_window.ui.Player_SoundDevice,
#            "SoundDeviceBG": main_window.ui.Player_SoundDeviceBG,
#            "PlayMusic": main_window.ui.Player_PlayMusic,
#            "MusicVolume": main_window.ui.Player_MusicVolume,
#            "PlaySound": main_window.ui.Player_PlaySound,
#            "SoundVolume": main_window.ui.Player_SoundVolume,
#            "Sound3D": [
#                main_window.ui.Player_Sound3D_0,
#                main_window.ui.Player_Sound3D_1,
#                main_window.ui.Player_Sound3D_2,
#                main_window.ui.Player_Sound3D_3,
#                main_window.ui.Player_Sound3D_4,
#                main_window.ui.Player_Sound3D_5
#            ]
#        },
#        "Standalone": {
#            "AltSound": main_window.ui.Standalone_AltSound
#        }
#    }
#
#    for section, options in widgets.items():
#        values = ini.get_section_subset(section, options.keys())
#
#        for key, widget in options.items():
#            value = values.get(key, "0")  
#            if isinstance(widget, list):  
#                index = int(value) if value.isdigit() else 0
#                widget[index].setChecked(True)
#            elif isinstance(widget, QCheckBox):
#                widget.setChecked(value == "1")
#            elif isinstance(widget, QComboBox):
#                widget.setCurrentText(value) if value else None
#            elif isinstance(widget, QSlider):
#                if not value:
#                    value = 100
#                widget.setValue(int(value))
#            elif isinstance(widget, QLineEdit):
#                widget.setText(value)
#            logger.info(f"Loading {key}: {value}")
#
#
#    # Atualiza os labels com os valores corretos
#    main_window.ui.LabelSoundVolumeNumber.setText(str(ini.get_section_subset("Player", ["SoundVolume"]).get("SoundVolume", "100")))
#    main_window.ui.LabelMusicVolumeNumber.setText(str(ini.get_section_subset("Player", ["MusicVolume"]).get("MusicVolume", "100")))
#
#    logger.info("=== Audio Options loaded ===")
#
#def save_audio_options(main_window):
#    """Save Audio options on VPinballX.ini"""
#    logger.info("=== Saving Audio Options ===")
#
#    widgets = {
#        "Player": {
#            "PlayMusic": main_window.ui.Player_PlayMusic,
#            "PlaySound": main_window.ui.Player_PlaySound,
#            "SoundDevice": main_window.ui.Player_SoundDevice,
#            "SoundDeviceBG": main_window.ui.Player_SoundDeviceBG,
#            "SoundVolume": main_window.ui.Player_SoundVolume,
#            "MusicVolume": main_window.ui.Player_MusicVolume,
#            "Sound3D": [
#                main_window.ui.Player_Sound3D_0,
#                main_window.ui.Player_Sound3D_1,
#                main_window.ui.Player_Sound3D_2,
#                main_window.ui.Player_Sound3D_3,
#                main_window.ui.Player_Sound3D_4,
#                main_window.ui.Player_Sound3D_5
#            ]
#        },
#        "Standalone": {
#            "AltSound": main_window.ui.Standalone_AltSound
#        }
#    }
#
#    updates = {}
#
#    for section, options in widgets.items():
#        updates[section] = {}
#
#        for key, widget in options.items():
#            if isinstance(widget, list):  
#                value = str(next(i for i, btn in enumerate(widget) if btn.isChecked()))
#            elif isinstance(widget, QCheckBox):
#                value = "1" if widget.isChecked() else "0"
#            elif isinstance(widget, QComboBox):
#                value = widget.currentText() if widget.currentText() else "Default"
#            elif isinstance(widget, QSlider):
#                value = str(widget.value())
#            elif isinstance(widget, QLineEdit):
#                value = widget.text()
#            updates[section][key] = value
#            logger.info(f"Saving {key}: {value}")
#
#
#    for section, values in updates.items():
#        ini.update_section_subset(section, values)
#
#    try:
#        ini.save()
#        logger.info("=== Audio Options Saved ===")
#        show_save_message("Audio Options Saved")
#    except Exception as e:
#        logger.error(f"Error saving Audio Options: \n {e}")
#        show_save_message("Error saving Audio Options")
#

