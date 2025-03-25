from utils import show_save_message, logger
from config.vpinball_ini import VPinballINI
from PySide6.QtWidgets import QCheckBox, QComboBox, QLineEdit, QSlider

ini = VPinballINI()

def load_audio_config(main_window):
    """Load Audio options from VPinballX.ini"""
    logger.info("=== Loading Audio Options ===")

    widgets = {
        "Player": {
            "SoundDevice": main_window.ui.Player_SoundDevice,
            "SoundDeviceBG": main_window.ui.Player_SoundDeviceBG,
            "PlayMusic": main_window.ui.Player_PlayMusic,
            "MusicVolume": main_window.ui.Player_MusicVolume,
            "PlaySound": main_window.ui.Player_PlaySound,
            "SoundVolume": main_window.ui.Player_SoundVolume,
            "Sound3D": [
                main_window.ui.Player_Sound3D_0,
                main_window.ui.Player_Sound3D_1,
                main_window.ui.Player_Sound3D_2,
                main_window.ui.Player_Sound3D_3,
                main_window.ui.Player_Sound3D_4,
                main_window.ui.Player_Sound3D_5
            ]
        },
        "Standalone": {
            "AltSound": main_window.ui.Standalone_AltSound
        }
    }

    for section, options in widgets.items():
        values = ini.get_section_subset(section, options.keys())

        for key, widget in options.items():
            value = values.get(key, "0")  
            if isinstance(widget, list):  
                index = int(value) if value.isdigit() else 0
                widget[index].setChecked(True)
            elif isinstance(widget, QCheckBox):
                widget.setChecked(value == "1")
            elif isinstance(widget, QComboBox):
                widget.setCurrentText(value) if value else None
            elif isinstance(widget, QSlider):
                if not value:
                    value = 0
                widget.setValue(int(value))
            elif isinstance(widget, QLineEdit):
                widget.setText(value)
            logger.info(f"Loading {key}: {value}")


    # Atualiza os labels com os valores corretos
    main_window.ui.playfld_snd_label.setText(str(ini.get_section_subset("Player", ["MusicVolume"]).get("MusicVolume", "0")))
    main_window.ui.backglass_snd_label.setText(str(ini.get_section_subset("Player", ["SoundVolume"]).get("SoundVolume", "0")))

    logger.info("=== Audio Options loaded ===")

def save_audio_options(main_window):
    """Save Audio options on VPinballX.ini"""
    logger.info("=== Saving Audio Options ===")

    widgets = {
        "Player": {
            "PlayMusic": main_window.ui.Player_PlayMusic,
            "PlaySound": main_window.ui.Player_PlaySound,
            "SoundDevice": main_window.ui.Player_SoundDevice,
            "SoundDeviceBG": main_window.ui.Player_SoundDeviceBG,
            "SoundVolume": main_window.ui.Player_SoundVolume,
            "MusicVolume": main_window.ui.Player_MusicVolume,
            "Sound3D": [
                main_window.ui.Player_Sound3D_0,
                main_window.ui.Player_Sound3D_1,
                main_window.ui.Player_Sound3D_2,
                main_window.ui.Player_Sound3D_3,
                main_window.ui.Player_Sound3D_4,
                main_window.ui.Player_Sound3D_5
            ]
        },
        "Standalone": {
            "AltSound": main_window.ui.Standalone_AltSound
        }
    }

    updates = {}

    for section, options in widgets.items():
        updates[section] = {}

        for key, widget in options.items():
            if isinstance(widget, list):  
                value = str(next(i for i, btn in enumerate(widget) if btn.isChecked()))
            elif isinstance(widget, QCheckBox):
                value = "1" if widget.isChecked() else "0"
            elif isinstance(widget, QComboBox):
                value = widget.currentText() if widget.currentText() else "Default"
            elif isinstance(widget, QSlider):
                value = str(widget.value())
            elif isinstance(widget, QLineEdit):
                value = widget.text()
            updates[section][key] = value
            logger.info(f"Saving {key}: {value}")


    for section, values in updates.items():
        ini.update_section_subset(section, values)

    try:
        ini.save()
        logger.info("=== Audio Options Saved ===")
        show_save_message("Audio Options Saved")
    except Exception as e:
        logger.error(f"Error saving Audio Options: \n {e}")
        show_save_message("Error saving Audio Options")


