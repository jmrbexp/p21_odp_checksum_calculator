# Central Widget
# - Created by J.Moon 20200413
# - A customizable widget intended to be the main app widget
# -- this only contains GUI functions and elements

# Module Imports
from app_configuration import app_config

try:
    import PySide2
    from pyqtgraph.Qt import QtGui, QtCore
    QtWidgets = QtGui # PyQt5/ Pyside2
except:
    try:
        import PyQt5
        from pyqtgraph.Qt import QtWidgets, QtGui, QtCore
    except:
        # print("Reverting to PyQt4")
        import PyQt4 # Force pyqtgraph to use PyQt4 (and not PySide)
        from pyqtgraph.Qt import QtGui, QtCore
        QtWidgets = QtGui # PyQt5 to PyQt4 patch
import os
# import unicode

if app_config.is_python3:
    print("python3 patch for unicode!")
    unicode = str

from product_properties_p21odp import product_p21odp
# from hex_files import product_p21odp.hex_file_in

# CentralWidget: This is a customizable widget designed as the widget that will change from app to app
# - you may still need to use the MainAppWidget class to acesses some resources.
# - this class is a subclass of QFrame
class CentralWidget(QtWidgets.QFrame):
    def __init__(self):    # Standard Python Function, called at the instantiation of a class
        super(CentralWidget, self).__init__()      # Calls the basic Widget Init Sequence
        # Initialize Variables
        self.init_system()
        # Create Widgets
        self.init_widgets()
        # Assign Widgets to a local layout
        self.arrange_widgets()
        # Assign Local Widget Callbacks
        self.init_callbacks()

    # ======= Widget Creation/ Arrangement =START=
    # init_system: Initialize all variables and structures used by this class
    def init_system(self):
        self.last_selected_directory = "" # for save to file function
        pass

    # init_widgets: Initialize all Graphical Objects used by this class
    def init_widgets(self):
        # Declare Widgets
        self.fix_button = QtWidgets.QPushButton("fix checksum")

        # - groupboxes
        # -- drive firmware
        self.drive_mcu_fw_groupbox = QtWidgets.QGroupBox("motor drive")
        self.drive_mcu_firmware_label = QtWidgets.QLabel("firmware")
        self.drive_mcu_configuration_label = QtWidgets.QLabel("configuration")

        # - firmware update buttons
        # -- drive firmware
        self.open_button = QtWidgets.QPushButton("open binary file (hex/hxf/bin)") # TODO: Replace with select_drive_fw_file_button
        self.select_drive_fw_file_button = QtWidgets.QPushButton("select file")
        self.write_drive_fw_file_button = QtWidgets.QPushButton("write")
        self.verify_drive_fw_file_button = QtWidgets.QPushButton("read")
        self.drive_fw_status_label = QtWidgets.QLabel("-")
        self.drive_fw_status_label.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)

        # -- spacer widgets
        self.spacer = QtWidgets.QLabel() # Used to push all widgets to the top when the window is big
        self.spacer.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)


    # arrange_widgets: Set up on-screen position of all GUI Objects used by this class
    def arrange_widgets(self):
        # Motor Drive Groupbox
        # - drive fw layout
        self.drive_fw_layout = QtWidgets.QGridLayout()
        self.drive_fw_layout.addWidget(self.drive_mcu_firmware_label, 0, 1, 1, 1)
        self.drive_fw_layout.addWidget(self.select_drive_fw_file_button, 1, 1, 1, 3)
        self.drive_fw_layout.addWidget(self.write_drive_fw_file_button, 1, 4, 1, 1)
        self.drive_fw_layout.addWidget(self.drive_fw_status_label, 1, 5, 1, 1)
        if app_config.DISPLAY_READ_BUTTONS:
            self.drive_fw_layout.addWidget(self.verify_drive_fw_file_button, 1, 6, 1, 1)
        self.drive_fw_layout.setContentsMargins(10,20,10,20)
        # - assign layout to groupbox
        self.drive_mcu_fw_groupbox.setLayout(self.drive_fw_layout)

        # - global layout
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.open_button)
        self.layout.addWidget(self.fix_button)
        self.layout.addWidget(self.drive_mcu_fw_groupbox)
        self.setLayout(self.layout)

        pass
    # ======= Widget Creation/ Arrangement ==END==

    # ======= Widget Status =START=

    # ======= Widget Status ==END==

    # ======= Callback Assignments =START=
    def init_callbacks(self):
        self.open_button.clicked.connect(self.open_button_cb)
        self.fix_button.clicked.connect(self.fix_button_cb)
        pass

    def set_serial_monitor_callback(self, callback):
        self.serial_monitor_cb = callback

    def display_message(self, message, rx=False, add_timestamp=True):
        if self.serial_monitor_cb:
            self.serial_monitor_cb(message, rx, add_timestamp)
    # ======= Callback Assignments ==END==

    # ======= Callback Implementations =START=
    def open_button_cb(self):
        # print("open button: select file")
        self.file_select_title_text = "Select Firmware File"
        self.file_select_default_directory = QtCore.QDir().homePath()
        self.file_select_name_filter = "Hex files (*.hex *.hxf *.bin)"
        # self.selected_file = str(QtWidgets.QFileDialog.getOpenFileName(self, self.file_select_title_text, self.file_select_default_directory, self.file_select_name_filter))
        self.selected_file_name = '' # initialize parameter for storing string of file path
        self.selected_file = QtWidgets.QFileDialog.getOpenFileName(self, self.file_select_title_text, self.file_select_default_directory, self.file_select_name_filter)
        # self.selected_file = self.file_select.getOpenFileName(self, 'Select Firmware File', 'c:\\',"Hex files (*.hex)")

        if self.selected_file and self.selected_file != ('', ''): # If a file is chosen, the formatting will be checked
            print('selected_file: ' + str(self.selected_file))
            if not app_config.is_python3: # Python2 Platform
                unencoded_file_name = self.selected_file
                print('encoded2: ' + str(unencoded_file_name))
                # self.selected_file_name = str(self.selected_file)
            else: # Python3 Platform
                unencoded_file_name = self.selected_file[0]
                print('encoded3: ' + str(unencoded_file_name))
                # self.selected_file_name = str(self.selected_file[0])
            self.selected_file_name = unicode(unencoded_file_name) # unencoded_file_name.encode('utf-8')
            base_file_name = os.path.basename(self.selected_file_name) # File name without the directory path

        if self.selected_file_name:
            self.display_message("importing file file: " + str(self.selected_file_name))
            product_p21odp.hex_file_in.import_log_file(self.selected_file_name)
        else:
            self.display_message("could not open file")

    def fix_button_cb(self):
        print("Fixing Checksum!")
        print("- stored: " + str(product_p21odp.hex_file_in.get_stored_rom_checksum()))
        print("- calculated: " + str(product_p21odp.hex_file_in.get_calculated_rom_checksum()))
        print("- fixing...")#  + str(product_p21odp.hex_file_in.get_calculated_rom_checksum()))
        product_p21odp.hex_file_in.fix_rom_checksum()
        print("- stored (fixed): " + str(product_p21odp.hex_file_in.get_stored_rom_checksum()))
        product_p21odp.hex_file_in.write_data_pages_to_file("test01.hex", product_p21odp.hex_file_in.memory_map, 0, 64) 
        # # print("open button: select file")
        # self.file_select_title_text = "Select Firmware File"
        # self.file_select_default_directory = QtCore.QDir().homePath()
        # self.file_select_name_filter = "Hex files (*.hex *.hxf)"
        # self.selected_file = str(QtWidgets.QFileDialog.getOpenFileName(self, self.file_select_title_text, self.file_select_default_directory, self.file_select_name_filter))
        # base_file_name = os.path.basename(self.selected_file) # File name without the directory path
        # # self.selected_file = self.file_select.getOpenFileName(self, 'Select Firmware File', 'c:\\',"Hex files (*.hex)")
        # if self.selected_file:
        #     product_p21odp.hex_file_in.import_log_file(self.selected_file)
        # else:
        #     self.display_message("could not open file")
    # ======= Callback Implementations ==END==

