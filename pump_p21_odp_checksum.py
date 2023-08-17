#!/usr/bin/env python
# universal_control.py
# - Created by J.Moon 20220411
# - This file is designed to be a main application that provides a means of opening hex files
# - It will be able to calculate their checksum and verify it according to those stored in ROM


# Module Imports
import sys # for getting operating system related information
try:
    import PySide2
    from pyqtgraph.Qt import QtGui, QtCore
    QtWidgets = QtGui # PyQt5/ Pyside2
    # print("PySide2 Import Successful")
    grouped_dragging_flag = 0x20 # !error: Temporary patch
except ImportError as error_data:
    # print("Pyside2 Import Error: {0}".format(error_data))
    try:
        # print("Reverting to PyQt5")
        import PyQt5
        from pyqtgraph.Qt import QtWidgets, QtGui, QtCore
        grouped_dragging_flag = 0x20
    except ImportError:
        # print("Reverting to PyQt4")
        import PyQt4 # Force pyqtgraph to use PyQt4 (and not PySide)
        from pyqtgraph.Qt import QtGui, QtCore
        QtWidgets = QtGui # PyQt5 to PyQt4 patch
        grouped_dragging_flag = 0x00 # Does not exist in qt4
import time # for getting current time

# Local GUI Widget Imports
from app_configuration import app_config
from central_widget import CentralWidget
from init_file import init_settings
from serial_monitor_gui import SerialMonitorWindow

# Local Backend Imports
from find_files import get_init_file_directory, get_icon_path, get_splash_image_path
# from hex_files import hex_file_in 
from product_properties_p21odp import product_p21odp
# from style_sheets import app_config.app_style



# Version Display
GUI_MOTOR_CONTROL_VERSION = "1.0.2"

# Python2 Patch for raw_input
# - python3 renamed "raw_input" to "input"
# -- we are natively supporting python3, but this patch allows python2 to work with this code.
try:
    if raw_input: # if raw_input exists, user is using python2
        input = raw_input
except NameError:  # if raw_input does not exist, user is using python3
    pass
app_start_time = time.time()

class DockTitleBarWidget(QtWidgets.QLabel):
    def __init__(self):    # Standard Python Function, called at the instantiation of a class
        super(DockTitleBarWidget, self).__init__()      # Calls the basic Widget Init Sequence for QMainWindow
        self.setText("---")
        self.setFixedHeight(3)
        self.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignTop)


class MainAppMenu(QtWidgets.QMenuBar):
    def __init__(self):    # Standard Python Function, called at the instantiation of a class
        super(MainAppMenu, self).__init__()      # Calls the basic Widget Init Sequence for QMainWindow
        pass
        # self.file_menu = BootloaderMenu_App("&File", self)
        # self.addMenu(self.file_menu)


# Main App: This is the master class, which will manage the whole app
# - this class is a subclass of QMainWindow
class MainAppWidget(QtWidgets.QMainWindow): # Declare a class that we've named 'MainAppWidget', it is an extension of the QtWidgets.QMainWindow Widget
    def __init__(self):    # Standard Python Function, called at the instantiation of a class
        super(MainAppWidget, self).__init__()      # Calls the basic Widget Init Sequence for QMainWindow
        # print("QMainWindow init start: " + str(time.time()))

        # Setup App Title, Icon, and Start Time
        self.setWindowTitle("P21 ODP - Drive Hex File - Checksum Calculator - " + GUI_MOTOR_CONTROL_VERSION)
        icon_path = get_icon_path()
        self.setWindowIcon(QtGui.QIcon(icon_path))
        self.set_app_start_time() # marked so time outputs are not huge numbers

        # Declare Class Constants
        # - Timer Timeouts
        self.SINGLE_TIMEOUT_MS = 25
        self.SINGLE_TIMEOUT_COUNTER_MAX = 100/self.SINGLE_TIMEOUT_MS # Graph update time is 100ms, so we are counting cycles to get this value
        # self.SINGLE_TIMEOUT_MODBUS_POLL = 250/self.SINGLE_TIMEOUT_MS # Graph update time is 100ms, so we are counting cycles to get this value

        # - Window Sizing
        self.CENTRAL_WIDGET_START_WIDTH = 400
        self.GRAPH_FRAME_START_WIDTH = 350
        self.SERIAL_MONITOR_START_WIDTH = 350
        self.WIDTH_BUFFER = 0 # how much space to allot for the horizontal 'dividers' between docks when resizing

        # Create GUI Elements
        self.init_all_windows()

        # Size/ Arrange/ Display Windows
        self.size_all_windows()
        self.arrange_all_windows()
        self.apply_style_sheets()
        self.show_all_windows()

        # Init Timer Instances
        self.init_timers()

        # Assign Callbacks - Port Selection/ Communications
        self.assign_timer_callbacks()
        self.assign_config_callbacks()

        # Start Subsystems (this makes the systems 'run')
        # - communications ports
        # self.serial_port_closed_warning_printed = False # Feedback flag to only show 'port closed' warning once.
        # comm_sched.start_system() # Serial Port Thread
        # - port select
        # self.win_port_select.start_system() # Port Selection Display
        # - local timer instances
        self.start_timers()

        # Restore Settings from file
        self.init_dir = get_init_file_directory()
        self.init_file_path = self.init_dir + "settings.ini"
        self.load_init_file()
        # print("QMainWindow init complete: " + str(time.time()))

        # Debug Operations
        self.display_gui_platform()

    # ======= Restore Settings From File =START=
    # load_init_file: load saved settings from an init file.
    def load_init_file(self):
        # Get Stored Settings in Init File
        status = init_settings.load_init_file(self.init_file_path)
        if status == init_settings.LOAD_INIT_NO_ERROR:
            # Import Loaded Settings
            text = "init file loaded.\n"
            for this_setting in range(len(init_settings.init_file_read_categories)):
                text += '- ' + init_settings.init_file_read_categories[this_setting] + ': ' + init_settings.init_file_read_values[this_setting] + '\n'
        else:
            text = "init file ignored. " + str(status)
        self.win_serial_monitor.add_message_to_buffer(text, add_timestamp=False)

        # Grab individual settings and restore where appropriate
        last_dir = init_settings.get_last_selected_directory_from_read_table()
        if last_dir: # if setting had a value, restore it
            self.central_widget.set_last_selected_directory(last_dir)
        else:
            print('no last dir...')

        
        # if com_port_value:
        #     # print("com port value received by init file: " + str(com_port_value))
        #     self.win_port_select.port_select_init_cb(str(com_port_value))
        # else:
        #     pass
        #     # print("no com port value found in init file")
    # ======= Restore Settings From File ==END==

    # ======= Window Positioning and Sizing =START=
    # init_all_windows: creates all app widget instances and assigns them to containing objects
    # - within the confines of this class (QMainWindow)
    def init_all_windows(self):
        # create app widget instances
        self.central_widget = CentralWidget() # Main Window

        self.win_serial_monitor = SerialMonitorWindow(start_time = self.app_start_time) # Monitor/ Log Window
        # self.win_port_select = PortSelectWindow() # Port Selection Window
        # self.win_custom_send = CustomSendWidget() # Custom Message Sending Widget

        self.setTabPosition( QtCore.Qt.AllDockWidgetAreas, QtGui.QTabWidget.North )
        self.setCentralWidget(self.central_widget)


        # Graphing Widget - placed in a frame, so that it lines up with other framed widgets
        self.setDockOptions(grouped_dragging_flag | self.AllowTabbedDocks | self.AllowNestedDocks) # !error: grouped_dragging_flag is a temporary patch

        # # Menu Bar
        # self.menu_bar = MainAppMenu()
        # self.setMenuBar(self.menu_bar) 

        # - right dock: SerialMonitorWindow (should be about the same in every app)
        self.dock_right = QtWidgets.QDockWidget("Monitor", self)
        self.dock_right.setWidget(self.win_serial_monitor)
        self.dock_right.setMinimumWidth(self.SERIAL_MONITOR_START_WIDTH)
        self.dock_right.setFeatures(QtWidgets.QDockWidget.DockWidgetFloatable | QtWidgets.QDockWidget.DockWidgetMovable)
        self.dock_right_title = DockTitleBarWidget()
        self.dock_right.setTitleBarWidget(self.dock_right_title)
        self.setCorner(QtCore.Qt.TopRightCorner, QtCore.Qt.RightDockWidgetArea)
        # self.setCorner(QtCore.Qt.BottomRightCorner, QtCore.Qt.RightDockWidgetArea)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.dock_right, QtCore.Qt.Horizontal)


    # size_all_windows: resize any widgets that need a specific size constraints
    def size_all_windows(self):
        # self.graph_frame.setMinimumWidth(self.GRAPH_FRAME_START_WIDTH)
        self.central_widget.setMinimumWidth(self.CENTRAL_WIDGET_START_WIDTH) # Ensure Connection widget doesn't get trimmed by forcing main widget a certain width
        # self.graph_frame.setMinimumWidth(self.GRAPH_FRAME_START_WIDTH)

    # arrange_all_windows: move any widgets that are not contained within the QMainWindow
    def arrange_all_windows(self):
        pass # we only have one window here, so it is arranged down below in def main()

    def apply_style_sheets(self):
        # Make each widget group colorful and contents easily visible using css stylesheets
        self.central_widget.setStyleSheet(app_config.app_style.groupboxes + app_config.app_style.background_frames + app_config.app_style.big_buttons + app_config.app_style.combo_boxes + app_config.app_style.labels + app_config.app_style.check_boxes + app_config.app_style.spin_boxes)
        self.win_serial_monitor.setStyleSheet(app_config.app_style.background_frames + app_config.app_style.text_boxes)

    # show_all_windows: enable the display of any widgets that are not contained within the QMainWindow
    def show_all_windows(self):
        pass # we only have one window here, so it is 'show'n down below in def main()
    # ======= Window Positioning and Sizing ==END==

    # ======= Local Widget Callbacks =START=
    def assign_config_callbacks(self):
        self.central_widget.set_serial_monitor_callback(self.win_serial_monitor.add_message_to_buffer)
        product_p21odp.hex_file_in.set_serial_monitor_callback(self.win_serial_monitor.add_message_to_buffer)
    # ======= Local Widget Callbacks ==END==

    # ======= Time Records =======
    # Time Reporting: app reports time relative to app start time.
    # set_app_start_time: set relative time base
    def set_app_start_time(self):
        self.app_start_time = time.time()
    # get_relative_time: get current time relative to when app started
    def get_relative_time(self):
        return time.time() - self.app_start_time
    # ======= Time Records ==END==

    # ======= Timers and Timeout callbacks =START=
    # init_timers: create all timer objects, do not start them yet, as the program is still initializing at this point
    def init_timers(self):
        # serial_monitor: how often to update message and status displays in the GUI
        self.serial_monitor_update_timer = QtCore.QTimer()
        self.serial_monitor_update_timer.setSingleShot(False)
        self.serial_piggyback_counter = 0
        self.modbus_poll_counter = 0

    # assign_timer_callbacks: assign functions to call for each timer, when it times out
    def assign_timer_callbacks(self):
        self.serial_monitor_update_timer.timeout.connect(self.single_timer_cb)

    # start_timers: start all continually running timers.
    def start_timers(self): # SINGLE_TIMEOUT_MS
        self.serial_monitor_update_timer.start(self.SINGLE_TIMEOUT_MS)

    # --  Timer Callback
    def single_timer_cb(self): # called 4 times, 0=all, 1=tx, 2=tx, monitor, 3=tx (REPEAT)
        # Update GUI every 100ms as calculated by SINGLE_TIMEOUT_COUNTER_MAX definition
        self.serial_piggyback_counter += 1
        if self.serial_piggyback_counter > self.SINGLE_TIMEOUT_COUNTER_MAX:
            self.serial_piggyback_counter = 0 # reset counter
            self.win_serial_monitor.display_buffered_messages() # display text to screen
    # ======= Timers and Timeout callbacks ==END==

    # ======= Message Parsing Routines =START=
    # ======= Message Parsing Routines ==END==

    # ======= Debugging Routines =======
    def display_gui_platform(self):
        text = ""
        try:
            PySide2
            text += "PySide2 Platform Active"
        except NameError:
            try:
                PyQt5
                text += "PyQt5 Platform Active"
            except NameError:
                try:
                    PyQt4
                    text += "PyQt4 Platform Active"
                except NameError:
                    text += "No GUI Platform Found!"
        self.win_serial_monitor.add_message_to_buffer(text, add_timestamp=False)


    # ======= Debugging Routines ==END==

    # ======= Exit Routine Callbacks =START=
    # def closeEvent(self, event):
    #     # print('close event... closing other windows')
    #     for this_graph in self.test_graphs:
    #         # print("1")
    #         this_graph.close()
    #         # print("2")
    #     # print("3")
    #     event.accept()
    #     # print("4")

    # about_to_quit: called by Qt QApplication just before it shuts down
    # - typically used to save settings to a file or end non-gui threads
    def about_to_quit_cb(self):
        # comm_sched.ack_received_cb = None # Don't allow this function to be called when app is closing down. (Patches segfaults on old 2.7 python versions)
        # com_port.end_read_thread() # shut down the serial port read thread.
        # com_port_value = com_port.connected_device_text
        # if com_port_value:
        #     # print("saving connected com port to file: " + str(com_port_value))
        #     init_settings.save_init_file(self.init_file_path, com_port_value)
        # else:
        #     pass
        #     # print("no connected com port, not saving")
        print ("Goodbye!") # print message to terminal
    # ======= Exit Routine Callbacks ==END==

    # ======= Window Positioning =START=
    def center_on_active_screen(self):
        # TODO: This doesn't work very well. does the moveCenter function provide any function?
        # Main Window will go top-center
        # Graph Windows will go bottom-center
        top_buffer = 350 # pixels from top where to start the main window
        graph_width = 800
        graph_height = 600

        frameGm = self.frameGeometry()
        screen = QtWidgets.QApplication.desktop().screenNumber(QtWidgets.QApplication.desktop().cursor().pos())
        centerPoint = QtWidgets.QApplication.desktop().screenGeometry(screen).center()
        centerPoint.setY(centerPoint.y())
        frameGm.moveCenter(centerPoint)

        center_x = frameGm.topLeft().x()
        center_y = frameGm.topLeft().y() 
        self.move(center_x, top_buffer)
        # graph1_x = center_x-graph_width/3
        # graph2_x = graph1_x + graph_width
        # self.test_graphs[0].move(graph1_x, center_y)
        # self.test_graphs[1].move(graph2_x, center_y)
        # self.move(centerPoint)
    # ======= Window Positioning ==END==

# Main Function
def main():
    app = QtWidgets.QApplication([]) # Mandatory component of any Qt Application, must be declared before any widgets
    app_windows = MainAppWidget() # instantiates our application's QMainWindow
    app_windows.resize(1160,250)
    app_windows.center_on_active_screen()
    # app_windows.move(500,500) # have the app start at a specific position
    app.aboutToQuit.connect(app_windows.about_to_quit_cb) # assign callback function for when app is shutting down
    app_windows.show() # displays the QMainWindow to screen
    # app_windows.bootloader_app.show()
    sys.exit(app.exec_()) # start the Qt Application's main_loop


# Code to Run if this File is run as the main application
if __name__ == '__main__':
    main()
