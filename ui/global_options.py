from ui_helpers.widget_option_manager import WidgetOptionManager
from utils import show_save_message, logger
from ui_helpers.widget_diffs import show_diff_table
from config.vpinball_ini import VPinballINI

ini = VPinballINI()

GLOBAL_OPTIONS = [
    "FlipperPhysicsMass0",
    "FlipperPhysicsStrength0",
    "FlipperPhysicsElasticity0",
    "FlipperPhysicsScatter0",
    "FlipperPhysicsEOSTorque0",
    "FlipperPhysicsEOSTorqueAngle0",
    "FlipperPhysicsReturnStrength0",
    "FlipperPhysicsElasticityFalloff0",
    "FlipperPhysicsFriction0",
    "FlipperPhysicsCoilRampUp0",
    "TablePhysicsGravityConstant0",
    "TablePhysicsContactFriction0",
    "TablePhysicsElasticity0",
    "TablePhysicsElasticityFalloff0",
    "TablePhysicsScatterAngle0",
    "TablePhysicsContactScatterAngle0",
    "TablePhysicsMinSlope0",
    "TablePhysicsMaxSlope0",
    "PhysicsSetName0"
]

def load_global_options(main_window):
    manager = WidgetOptionManager(main_window)
    return manager.load_options("Player", GLOBAL_OPTIONS)

def prepare_global_updates(main_window):
    manager = WidgetOptionManager(main_window)
    return manager.prepare_updates("Player", GLOBAL_OPTIONS)

def on_save_global_clicked(main_window):
    updates = prepare_global_updates(main_window)
    if show_diff_table(ini, updates, parent=main_window):
        for section, values in updates.items():
            ini.update_section_subset(section, values)
        try:
            ini.save()
            logger.info("=== Global Options saved ===")
            show_save_message("Global Options saved")
        except Exception as e:
            logger.error(f"Error saving Global Options: {e}")
            show_save_message("Error saving Global Options")


#from utils import show_save_message, logger
#from config.vpinball_ini import VPinballINI
#
#ini = VPinballINI()
#
## Class for handling this in another way?
#GLOBAL_OPTIONS = [
#    "FlipperPhysicsMass0",
#    "FlipperPhysicsStrength0",
#    "FlipperPhysicsElasticity0",
#    "FlipperPhysicsScatter0",
#    "FlipperPhysicsEOSTorque0",
#    "FlipperPhysicsEOSTorqueAngle0",
#    "FlipperPhysicsReturnStrength0",
#    "FlipperPhysicsElasticityFalloff0",
#    "FlipperPhysicsFriction0",
#    "FlipperPhysicsCoilRampUp0",
#    "TablePhysicsGravityConstant0",
#    "TablePhysicsContactFriction0",
#    "TablePhysicsElasticity0",
#    "TablePhysicsElasticityFalloff0",
#    "TablePhysicsScatterAngle0",
#    "TablePhysicsContactScatterAngle0",
#    "TablePhysicsMinSlope0",
#    "TablePhysicsMaxSlope0",
#    "PhysicsSetName0"
#]
#
#def load_global_options(main_window):
#    """Load Global configuration from VPinballX.ini"""
#    logger.info("=== Loading Global Options ===")
#    
#    for option in GLOBAL_OPTIONS:
#        widget = getattr(main_window.ui, option)
#        if not widget:
#            logger.warning(f"Widget {option} not found in UI")
#            continue
#        
#        widget.setText(ini.get_section_value("Player", option,""))
#        logger.info(f"Loading {option}: {widget.text()}")
#    
#    logger.info("=== Global Options loaded ===")
#
#def save_global_options(main_window):
#    """Save Global options on VPinballX.ini"""
#    logger.info("=== Saving Global Options ===")
#    updates = {}    
#    for option in GLOBAL_OPTIONS:
#        widget = getattr(main_window.ui, option)
#
#        updates[option] = widget.text()
#        logger.info(f"Saving {option}: {updates[option]}")
#   
#    ini.update_section_subset("Player", updates)
#
#    try:
#        ini.save()
#        logger.info("=== Global Options saved ===")
#        show_save_message("Global Options saved")
#    except Exception as e:
#        logger.error(f"Error saving Global Options: \n {e}")
#        show_save_message("Error saving Global Options")
#
#