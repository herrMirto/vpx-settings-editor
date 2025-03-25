import re
import subprocess
from PySide6.QtWidgets import QComboBox
from PySide6.QtGui import QGuiApplication
from utils import logger
from config.vpinball_ini import VPinballINI
from config.vpinball_bin import VPinballBin

ini = VPinballINI()

def calc_ratio(width, height):
    ratios = {
        "16:9": 16 / 9,
        "16:10": 16 / 10,
        "4:3": 4 / 3,
        "21:9": 21 / 9,
        "32:9": 32 / 9,
        "5:4": 5 / 4,
        "3:2": 3 / 2
    }
    ratio = width / height
    return min(ratios, key=lambda x: abs(ratios[x] - ratio))


def get_display_resolutions():
    vpx_path = VPinballBin().get_filepath()
    logger.info(f"VPX path: {vpx_path}")

    logger.info("=== Getting screen(s) resolutions ===")
    try:
        scr_cmd = f"{vpx_path} -listres"
        scr_cmd_result = subprocess.run(scr_cmd, shell=True, capture_output=True, text=True)
        logger.info("Resolutions list command executed")

    except Exception as get_display_resolutions_error:
        logger.error(f"Error getting screen(s) resolutions: {get_display_resolutions_error}")
   
    displays_info = {}
    screen_regex = re.compile(r"display (\d+): (\d+)x(\d+) \(depth=(\d+), refreshRate=(\d+(?:\.\d+)?)\)")

    for line in scr_cmd_result.stdout.split("\n"):
            match = screen_regex.search(line)
            if match:
                display_id = f"Display {match.group(1)}"
                width, height = int(match.group(2)), int(match.group(3))
                depth = match.group(4)
                refresh_rate = match.group(5)

                ratio = calc_ratio(width, height)
                resolution_info = f"{width} x {height} ({refresh_rate}Hz {ratio}, depth={depth})"

                if display_id not in displays_info:
                    displays_info[display_id] = []
            
                displays_info[display_id].append(resolution_info)
    logger.info(f"Screen(s) resolutions found: {displays_info}")
    return displays_info

def load_playfield_resolution(resolution_widget: QComboBox, available_resolutions: dict):
    try:
        display_id = int(ini.get_section_value("Player", "PlayfieldDisplay"))
        display_name = f"Display {display_id}"
        width = int(ini.get_section_value("Player", "PlayfieldWidth"))
        height = int(ini.get_section_value("Player", "PlayfieldHeight"))
        depth = int(ini.get_section_value("Player", "PlayfieldColorDepth"))
        hz = int(ini.get_section_value("Player", "PlayfieldRefreshRate"))

        screens = QGuiApplication.screens()
        dpi_scale = screens[display_id].devicePixelRatio()

        logger.info(f"Original width: {width}, height: {height}, dpi_scale: {dpi_scale}")

        if dpi_scale >= 2.0:
            width *= 2
            height *= 2
            logger.info(f"Scaled for high DPI: width={width}, height={height}")

        if display_name not in available_resolutions:
            logger.info(f"Display '{display_name}' not found in available resolutions. Falling back to Display 0.")
            display_name = "Display 0"

        resolutions = available_resolutions.get(display_name, [])
        resolution_widget.clear()
        resolution_widget.addItems(resolutions)

        resolution_pattern = re.compile(r"(\d+)\s*x\s*(\d+)\s*\((\d+)Hz\s+[^,]*,\s*depth=(\d+)\)")
        logger.info(f"Looking for resolution: {width}x{height} @ {hz}Hz depth={depth} in {display_name}")

        for i in range(resolution_widget.count()):
            item_text = resolution_widget.item(i).text()
            logger.info(f"[{i}] Checking item: '{item_text}'")

            match = resolution_pattern.search(item_text)
            if match:
                w, h, item_hz, d = map(int, match.groups())
                logger.info(f"Parsed: {w}x{h} {item_hz}Hz {d}-bit")

                if w == width and h == height and d == depth and item_hz == hz:
                    resolution_widget.setCurrentRow(i)
                    logger.info(f" Resolution matched at index {i}: '{item_text}'")
                    return

        logger.info(f"No matching resolution found for {width}x{height} @ {hz}Hz depth={depth} in {display_name}.")

    except Exception as e:
        logger.error(f"Error while processing INI file: {e}")
