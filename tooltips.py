TOOLTIPS = {
    "LabelMSAA": (
        "<b>MSAA - Multisample Anti-Aliasing</b><br>"
        "Reduces jagged edges in 3D rendering.<br><br>"
        "<u>Recommended:</u> 4x or 8x for modern GPUs."
    ),
    "LabelFXAA": (
        "<b>FXAA - Fast Approximate Anti-Aliasing</b><br>"
        "Applies a fast post-processing filter to smooth edges.<br>"
        "Good alternative for weaker GPUs."
    ),
    "LabelAAFactor": (
        "<b>AAFactor</b><br>"
        "Scales internal rendering resolution to increase sharpness. "
        "Values above 100% improve quality but reduce performance."
    ),
    "Player_Sound3D_5": (
        "7.1 Surround Sound Feedback (SSF): This exaggerates the positional feel of the playfield\n"
        "sound effects when played in a cabinet with exciter pairs positioned at each end of the cabinet."
    ),
    "B2SHideGrill": (
        "Uncheck to show grill (if it exists), check to hide grill"
    ),
    "B2SHideB2SDMD": ( 
        "Uncheck to show extra DMD frame (if it exists), check to hide extra DMD frame"
    ),
    "B2SHideB2SBackglass": (
        "Uncheck to show backglass, check to hide backglass"
    ),
    "Player_PlayMusic": (
        "Unchecking this to disable Music from being played, checked enables Music\n "
        "Music sounds are those routed through SoundDeviceBG and includes \n "
        "not only music but backglass sounds plus PinMAME and PUP audio"
    ),
    "PBWEnabled": (
        "PBWEnabled: This enables analog nudging from hardware acceleration sensors,\n"
        "both from purpose-built controllers like the KL25Z-based Pinscape or from video game console\n"
        "controllers like the Playstation 4 Dualshock. Setting this to 0 disables the acceleration sensor, 1 enables it (the default)."
    ),
    "BGSet": (
        "Desktop (default)\n"
        "Fullscreen: Gives you a top-down view on the playfield when playing on an actual virtual pinball cabinet.\n"
        "You can also use Fullscreen in a multi-window setup on your desktop\n"
        "Full Single Screen (FSS): Tries to show the whole machine including backglass\n "
        "if set up by the table designer. Otherwise it falls back to Desktop view"
    )
}


def apply_tooltips(main_window, tooltips_dict): 
    for widget_name, tooltip_text in tooltips_dict.items():
        widget = getattr(main_window.ui, widget_name, None)
        if widget:
            widget.setToolTip(tooltip_text)
        else:
            print(f"⚠️ Tooltip target '{widget_name}' not found.")
