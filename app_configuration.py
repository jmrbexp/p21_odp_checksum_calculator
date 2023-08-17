# app_configuration
# - Created by J.Moon 20200413
# -- designed to enable setsting of macros 

# AppConfigurationOptions: This class contains all configuration options for the app
# - It's primarily used for enabling debugging routines, and for variants of the product based on the end-user
import sys # for python2 vs python3 detection

# - import stylesheets
from style_sheets_regal_green import app_style_regal_green
from style_sheets_regal_purple import app_style_regal_purple

class AppConfigurationOptions():
    def __init__(self):    # Standard Python Function, called at the instantiation of a class
        # Initialize Variables
        self.init_system()
        # Version Display
        self.GUI_MOTOR_CONTROL_VERSION = "1.1.1"
    # ======= Widget Creation/ Arrangement =START=
    def init_system(self):
        # - Widget Enables
        self.ENABLE_GRAPH_LEGEND = True # DEFAULT: False -> in Python2 build environment, legend causes segmentation faults at app close
        self.DISPLAY_READ_BUTTONS = True # DEFAULT: False -> Factory doesn't need these.
        # - Communication Settings
        self.DISABLE_CONNECTION_MESSAGES = False # DEFAULT: False -> disable messages sent at com port connection (for bootloader debugging)
        # - App Variants
        self.PUMP_GEN3 = 0
        self.PUMP_P21_TEFC = 1
        # Record python version in use
        if sys.version_info[0] >= 3:
            self.is_python3 = True
            self.app_style = app_style_regal_green # Green theme signifies Python3 platform
        else:
            self.is_python3 = False
            self.app_style = app_style_regal_purple # Purple theme signifies Python2 platform



app_config = AppConfigurationOptions()
