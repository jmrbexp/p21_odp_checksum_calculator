#!/usr/bin/env python
# universal_control.py
# - Created by J.Moon 20200304
# - This file is designed to be a main application that provides basic connection to serially
# - connected devices. The app then sends messages to and receives messages from that device.
# - The app then displays those items in a GUI.
# - This is designed to be a simple template that can be easily converted for other applications.

# Module Imports
import sys # for getting operating system related information
# import PySide2
# from pyqtgraph.Qt import QtGui, QtCore
# QtWidgets = QtGui # PyQt5/ Pyside2
# print("PySide2 Import Successful")
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

# Local Imports
from find_files import get_splash_image_path

# Main Function
def main():
    app = QtWidgets.QApplication([]) # Mandatory component of any Qt Application, must be declared before any widgets
    pixmap = QtWidgets.QPixmap(get_splash_image_path())
    # screen = QtGui.QApplication.desktop().screenNumber(QtGui.QApplication.desktop().cursor().pos())
    # splash_screen = QtWidgets.QSplashScreen(QtWidgets.QApplication.screenAt(QtWidgets.QCursor.pos()), pixmap)
    # splash_screen = QtWidgets.QSplashScreen(QtWidgets.QScreen(screen), pixmap)
    splash_screen = QtWidgets.QSplashScreen(pixmap)
    splash_screen.show()
    app.processEvents()

    from pump_p21_checksum import MainAppWidget # Only import things after splash screen is displayed so splash screen shows up immediately
    app_windows = MainAppWidget() # instantiates our application's QMainWindow
    app_windows.resize(1160, 250)
    app_windows.center_on_active_screen()
    # app_windows.move(500,500) # have the app start at a specific position
    app.aboutToQuit.connect(app_windows.about_to_quit_cb) # assign callback function for when app is shutting down
    app_windows.show() # displays the QMainWindow to screen
    splash_screen.finish(app_windows)
    sys.exit(app.exec_()) # start the Qt Application's main_loop


# Code to Run if this File is run as the main application
if __name__ == '__main__':
    main()