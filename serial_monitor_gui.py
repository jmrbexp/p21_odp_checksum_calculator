# Serial Monitor GUI
# - Created by J.Moon 20191227
# - A simple text box widget to display messages and timestamps upon.
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
import sys
import time

# SerialMonitorWindow is a frame containing a text box for displaying various information
# - displays messages transmitted and received via the serial ports.
# - displays messages from the app regarding app state.
# - this class is a subclass of QFrame
class SerialMonitorWindow(QtWidgets.QFrame):
    def __init__(self, start_time=None, parent=None): # Standard Python Function, called at the instantiation of a class
        super(SerialMonitorWindow, self).__init__(parent)      # Calls the basic Widget Init Sequence for QFrame
        # Initialize Variables
        if start_time:
            self.start_time = start_time
        else:
            self.start_time = 0
        self.init_system()
        # Create Widgets
        self.init_widgets()
        # Assign Widgets to a local layout
        self.arrange_widgets()
        # Assign Local Widget Callbacks (no callbacks)
        # self.init_callbacks()

    # ======= System Init/ Start =START=
    def init_system(self): # initialize all variables
        if not self.start_time:
            self.start_time = time.time() # Note the start time, so that message received times start at '0' when the app boots
        self.message_buffer = []
    # ======= System Init/ Start ==END==

    # ======= Widget Creation/ Arrangement =START=
    def init_widgets(self):
        self.text_box = QtWidgets.QTextEdit() # create the text box for displaying text

    def arrange_widgets(self):
        # Add widgets to a vertical layout
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.text_box)
        self.setLayout(self.layout) # assign layout to this widget (SerialMonitorWindow)
    # ======= Widget Creation/ Arrangement ==END==

    # ======= Widget Display =START=
    # add_message: a function to allow the main application to display text on-screen
    # - receives:
    # -- message - a string to display on screen
    # -- rx - a boolean that changes the color of the displayed text if it is a received message
    # -- add_timestamp - a boolean to add the current time to the end of a displayed message
    def add_message(self, message, rx=False, add_timestamp=True, color_string=""):
        # Add timestamp to message if required
        if add_timestamp:
            time_val = time.time() - self.start_time # calculate time stamp
            time_text =  " %.3f" %time_val # truncate to milliseconds
        else:
            time_text = "" # set to empty string if timestamp is not required
        # Change the color of the displayed message, if required
        if color_string: # Custom Color Specified
            color = QtGui.QColor(color_string)
            bold = True
        elif rx: # received messages are purple text
            color = QtGui.QColor("purple") # QColor belongs to 'QtGui' in both PyQt4 and 5
            bold = False
        else: # all other messages are black text
            color = QtGui.QColor("black")
            bold = False
        
        self.text_box.setTextColor(color)
        if bold:
            self.text_box.setFontWeight(QtWidgets.QFont.Bold)
        self.text_box.append(str(message) + time_text)
        if bold:
            self.text_box.setFontWeight(QtWidgets.QFont.Normal)

    def add_message_to_buffer(self, message, rx=False, add_timestamp=True, color_string=""):
        self.message_buffer.append([message, rx, add_timestamp, color_string])

    def display_buffered_messages(self):
        for message, rx, add_timestamp, color_string in self.message_buffer:
            self.add_message(message, rx = rx, add_timestamp = add_timestamp, color_string=color_string)
        self.message_buffer = []
    # ======= Widget Display ==END==
