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
    def init_system(self):
        pass

    def init_widgets(self):
        self.open_button = QtWidgets.QPushButton("open binary file (hex/hxf/bin)")
        self.fix_button = QtWidgets.QPushButton("fix checksum")

    def arrange_widgets(self):
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.open_button)
        self.layout.addWidget(self.fix_button)
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

