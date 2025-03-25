from PySide6.QtWidgets import QComboBox, QLineEdit
from utils import logger
from config.vpinball_ini import VPinballINI

def setup_aspect_ratio_logic(aspect_combo: QComboBox, width_edit: QLineEdit, height_edit: QLineEdit):

            BASE_WIDTH = 1920
            BASE_HEIGHT = 1920

            # Index-based aspect ratios (same order as in your combo)
            aspect_ratios = {
                1: (4, 3),
                2: (16, 10),
                3: (16, 9),
                4: (21, 10),
                5: (21, 9),
                6: (4, 3),
                7: (16, 10),
                8: (16, 9),
                9: (21, 10),
                10: (21, 9),
            }

            def update_edit_mode():
                index = aspect_combo.currentIndex()
        
                if index == 0:
                    width_edit.setEnabled(True)
                    height_edit.setEnabled(True)
                else:
                    width_edit.setEnabled(True)
                    height_edit.setEnabled(False)
        
                    # Calculate and apply width + height from base values
                    if index in aspect_ratios:
                        w_ratio, h_ratio = aspect_ratios[index]
        
                        if index >= 6:
                            # Portrait
                            height = BASE_HEIGHT
                            width = int(round(height * w_ratio / h_ratio))
                        else:
                            # Landscape
                            width = BASE_WIDTH
                            height = int(round(width * h_ratio / w_ratio))
        
                        width_edit.setText(str(width))
                        height_edit.setText(str(height))

            def update_height():
                index = aspect_combo.currentIndex()
                width_text = width_edit.text()

                if not width_text.isdigit():
                    return

                width = int(width_text)
                if index in aspect_ratios:
                    w_ratio, h_ratio = aspect_ratios[index]

                    # Flip for portrait modes
                    if index >= 6:
                        w_ratio, h_ratio = h_ratio, w_ratio

                    height = int(round(width * h_ratio / w_ratio))
                    height_edit.setText(str(height))

            # Connect signals
            aspect_combo.currentIndexChanged.connect(update_edit_mode)
            width_edit.textChanged.connect(lambda _: update_height() if aspect_combo.currentIndex() != 0 else None)

            # Trigger once on start
            update_edit_mode()

def get_aspect_ratio_index_from_resolution(width: int, height: int) -> int:
    """
    Given a width and height, return the matching aspect ratio index based on predefined aspect_ratios.
    Returns 0 if no close match is found (manual/custom mode).
    """
    if height == 0:
        return 0  # avoid division by zero

    target_ratio = round(width / height, 2)

    aspect_ratios = {
        1: (4, 3),
        2: (16, 10),
        3: (16, 9),
        4: (21, 10),
        5: (21, 9),
        6: (4, 3),
        7: (16, 10),
        8: (16, 9),
        9: (21, 10),
        10: (21, 9),
    }

    for index, (w_ratio, h_ratio) in aspect_ratios.items():
        ratio = round(w_ratio / h_ratio, 2)
        if abs(target_ratio - ratio) < 0.05:
            return index

    return 0  # fallback to "Custom"

def get_playfield_mode():
     ini = VPinballINI()
     playfield_fullscreen = ini.get_section_value("Player","PlayfieldFullScreen")
     if playfield_fullscreen == "0":
        playfield_width = int(ini.get_section_value("Player", "PlayfieldWidth"))
        playfiled_height = int(ini.get_section_value("Player","PlayfieldHeight"))
        window_index = get_aspect_ratio_index_from_resolution(playfield_width, playfiled_height)
        return window_index
     else:
        return False
