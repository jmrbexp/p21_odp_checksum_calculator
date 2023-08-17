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

        # - firmware update buttons
        # -- drive firmware
        # self.select_drive_fw_file_button = QtWidgets.QPushButton("open binary file (hex/hxf/bin)") # TODO: Replace with select_drive_fw_file_button
        self.select_drive_fw_file_button = QtWidgets.QPushButton("select file (hex/hxf/bin)")
        self.write_drive_fw_file_button = QtWidgets.QPushButton("write")
        self.verify_drive_fw_file_button = QtWidgets.QPushButton("read")
        self.drive_fw_status_label = QtWidgets.QLabel("-")
        self.drive_fw_status_label.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)

        # - firmware status buttons
        # -- drive firmware (crc info)
        self.drive_mcu_fw_crc_groupbox = DriveFirmwareCrcsWidget()

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
        # self.layout.addWidget(self.select_drive_fw_file_button)
        self.layout.addWidget(self.fix_button)
        self.layout.addWidget(self.drive_mcu_fw_groupbox)
        self.layout.addWidget(self.drive_mcu_fw_crc_groupbox)
        self.setLayout(self.layout)

        pass
    # ======= Widget Creation/ Arrangement ==END==

    # ======= Widget Status =START=

    # ======= Widget Status ==END==

    # ======= Callback Assignments =START=
    def init_callbacks(self):
        self.select_drive_fw_file_button.clicked.connect(self.select_drive_fw_file_button_cb)
        self.fix_button.clicked.connect(self.fix_button_cb)
        pass

    def set_serial_monitor_callback(self, callback):
        self.serial_monitor_cb = callback

    def display_message(self, message, rx=False, add_timestamp=True):
        if self.serial_monitor_cb:
            self.serial_monitor_cb(message, rx, add_timestamp)
    # ======= Callback Assignments ==END==

    # ======= Callback Implementations =START=
    def select_drive_fw_file_button_cb(self):
        # print("open button: select file")
        self.file_select_title_text = "Select Firmware File"
        if not self.last_selected_directory:
            self.file_select_default_directory = QtCore.QDir().homePath()
        else:
            self.file_select_default_directory = self.last_selected_directory

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
            self.display_message("importing firmware file: " + str(self.selected_file_name))
            product_p21odp.hex_file_in.import_log_file(self.selected_file_name)
            self.select_drive_fw_file_button.setText(base_file_name)
            self.update_crc_data_display()
            self.set_last_selected_directory(QtCore.QDir().absoluteFilePath(self.selected_file_name))

            P21_ODP_FLASH_PAGE_FIRMWARE_START = 3 # TODO: Move
            P21_ODP_FLASH_PAGE_FIRMWARE_END = 19 # Exclusive TODO: MOVE
            crc32_value = product_p21odp.hex_file_in.memory_map_out.get_crc_u32_from_page_list(list(range(P21_ODP_FLASH_PAGE_FIRMWARE_START,P21_ODP_FLASH_PAGE_FIRMWARE_END)), ignore_last_four_bytes=True)
            # crc32_value = product_p21odp.hex_file_in.memory_map_out.get_crc_u32_from_page_list(list(range(32)), ignore_last_four_bytes=False)
            # crc32_value = drive_fw_memory_map_file.get_crc_u32_from_page_list(list(range(3,16)), ignore_last_four_bytes=True)
            print("CRC - Safety Area" + ": 0x{:08x}".format(crc32_value))
            print("-- should be: 0x4A7CB2E6")
        else:
            self.display_message("could not open file")

    def update_crc_data_display(self):
        print("update!")
        bootloader_crc_read = str(product_p21odp.hex_file_in.stored_bootloader_checksum)
        bootloader_crc_calc = str(product_p21odp.hex_file_in.calc_bootloader_checksum)
        firmware_crc_read = str(product_p21odp.hex_file_in.stored_firmware_checksum)
        firmware_crc_calc = str(product_p21odp.hex_file_in.calc_firmware_checksum)
        self.drive_mcu_fw_crc_groupbox.drive_bootlader_read_crc_val_label.setText(bootloader_crc_read)
        self.drive_mcu_fw_crc_groupbox.drive_bootlader_calc_crc_val_label.setText(bootloader_crc_calc)
        self.drive_mcu_fw_crc_groupbox.drive_firmware_read_crc_val_label.setText(firmware_crc_read)
        self.drive_mcu_fw_crc_groupbox.drive_firmware_calc_crc_val_label.setText(firmware_crc_calc)

        print("update END!")

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
    def set_last_selected_directory(self, directory):
        if os.path.exists(directory):
            print('set last: good path!')
            self.last_selected_directory = directory
        else:
            print('set last: bad path...')

    def get_last_selected_directory(self):
        if os.path.exists(self.last_selected_directory):
            print('get last: good path!')
            return self.last_selected_directory
        else:
            print('get last: bad path (returning empty string)...')
            return ""

# DriveFirmwareCrcsWidget: Displays all firmware related CRC Information
class DriveFirmwareCrcsWidget(QtWidgets.QFrame):
    def __init__(self):    # Standard Python Function, called at the instantiation of a class
        super(DriveFirmwareCrcsWidget, self).__init__()      # Calls the basic Widget Init Sequence
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
        pass

    # init_widgets: Initialize all Graphical Objects used by this class
    def init_widgets(self):
        # Declare Widgets
        # - groupboxes
        # -- drive firmware
        self.drive_mcu_fw_groupbox = QtWidgets.QGroupBox("motor drive crcs")
        #
        self.drive_bootlader_read_crc_label = QtWidgets.QLabel("bootloader crc (read) - ")
        self.drive_bootlader_read_crc_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.drive_bootlader_read_crc_val_label = QtWidgets.QLabel("0x00000000")
        #
        self.drive_bootlader_calc_crc_label = QtWidgets.QLabel("bootloader crc (calc) - ")
        self.drive_bootlader_calc_crc_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.drive_bootlader_calc_crc_val_label = QtWidgets.QLabel("0x00000000")
        #
        self.drive_firmware_read_crc_label = QtWidgets.QLabel( "firmware crc (read) - ")
        self.drive_firmware_read_crc_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.drive_firmware_read_crc_val_label = QtWidgets.QLabel( "0x00000000")
        #
        self.drive_firmware_calc_crc_label = QtWidgets.QLabel( "firmware crc (calc) - ")
        self.drive_firmware_calc_crc_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.drive_firmware_calc_crc_val_label = QtWidgets.QLabel( "0x00000000")
        # - firmware update buttons
        # -- drive firmware
        # self.select_drive_fw_file_button = QtWidgets.QPushButton("open binary file (hex/hxf/bin)") # TODO: Replace with select_drive_fw_file_button

        # -- spacer widgets
        self.spacer = QtWidgets.QLabel() # Used to push all widgets to the top when the window is big
        self.spacer.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)


    # arrange_widgets: Set up on-screen position of all GUI Objects used by this class
    def arrange_widgets(self):
        # Motor Drive Groupbox
        # - groupbox layout
        self.drive_fw_layout = QtWidgets.QGridLayout() 
        self.drive_fw_layout.addWidget(self.drive_bootlader_read_crc_label,0,0)
        self.drive_fw_layout.addWidget(self.drive_bootlader_calc_crc_label,1,0)
        self.drive_fw_layout.addWidget(self.drive_firmware_read_crc_label,2,0)
        self.drive_fw_layout.addWidget(self.drive_firmware_calc_crc_label,3,0)
        self.drive_fw_layout.addWidget(self.drive_bootlader_read_crc_val_label,0,1)
        self.drive_fw_layout.addWidget(self.drive_bootlader_calc_crc_val_label,1,1)
        self.drive_fw_layout.addWidget(self.drive_firmware_read_crc_val_label,2,1)
        self.drive_fw_layout.addWidget(self.drive_firmware_calc_crc_val_label,3,1)
        self.drive_fw_layout.setContentsMargins(10,20,10,20)
        self.drive_mcu_fw_groupbox.setLayout(self.drive_fw_layout)
        # - global layout
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.drive_mcu_fw_groupbox)
        self.layout.setContentsMargins(0,0,0,0) # This frame is invisible, allow contents to expand all the way out
        self.setLayout(self.layout)
    # ======= Widget Creation/ Arrangement ==END==

    # ======= Widget Status =START=
    # ======= Widget Status ==END==

    # ======= Callback Assignments =START=
    def init_callbacks(self):
        pass

    def set_serial_monitor_callback(self, callback):
        self.serial_monitor_cb = callback

    def display_message(self, message, rx=False, add_timestamp=True):
        if self.serial_monitor_cb:
            self.serial_monitor_cb(message, rx, add_timestamp)
    # ======= Callback Assignments ==END==

    # ======= Callback Implementations =START=
    # ======= Callback Implementations ==END==

