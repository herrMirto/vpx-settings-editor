from PySide6.QtWidgets import QCheckBox, QComboBox, QLineEdit

def setup_stereo3d_logic(
    stereo_combo: QComboBox,
    fake3d_checkbox: QCheckBox,
    eye_separation_edit: QLineEdit,
    anaglyph_filter_combo: QComboBox,
    anaglyph_brightness_edit: QLineEdit,
    anaglyph_saturation_edit: QLineEdit,
    stereo3d_zpd: QLineEdit,
    stereo3f_offset: QLineEdit,

):
    def update_stereo_fields():
        index = stereo_combo.currentIndex()

        if index == 0:
            # Disable all
            fake3d_checkbox.setEnabled(False)
            eye_separation_edit.setEnabled(False)
            anaglyph_filter_combo.setEnabled(False)
            anaglyph_brightness_edit.setEnabled(False)
            anaglyph_saturation_edit.setEnabled(False)
            stereo3d_zpd.setEnabled(False)
            stereo3f_offset.setEnabled(False)
        elif 1 <= index <= 4:
            # Enable basic 3D
            fake3d_checkbox.setEnabled(True)
            eye_separation_edit.setEnabled(True)
            anaglyph_filter_combo.setEnabled(False)
            anaglyph_brightness_edit.setEnabled(False)
            anaglyph_saturation_edit.setEnabled(False)
            stereo3d_zpd.setEnabled(False)
            stereo3f_offset.setEnabled(False)
        elif 5 <= index <= 14:
            # Enable full anaglyph config
            fake3d_checkbox.setEnabled(True)
            eye_separation_edit.setEnabled(True)
            anaglyph_filter_combo.setEnabled(True)
            anaglyph_brightness_edit.setEnabled(True)
            anaglyph_saturation_edit.setEnabled(True)
            stereo3d_zpd.setEnabled(False)
            stereo3f_offset.setEnabled(False)
        else:
            # Safe fallback
            fake3d_checkbox.setEnabled(False)
            eye_separation_edit.setEnabled(False)
            anaglyph_filter_combo.setEnabled(False)
            anaglyph_brightness_edit.setEnabled(False)
            anaglyph_saturation_edit.setEnabled(False)
            stereo3d_zpd.setEnabled(False)
            stereo3f_offset.setEnabled(False)

    # Connect signal
    stereo_combo.currentIndexChanged.connect(update_stereo_fields)

    # Trigger once at startup
    update_stereo_fields()
