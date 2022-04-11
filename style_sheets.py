# stylesheets.py
# - this file contains stylesheet strings for use by this app
import sys



class AppStyleSheets():
        def __init__(self):    # Standard Python Function, called at the instantiation of a class
            # operating system specific
            if 'darwin' in sys.platform.lower(): # apple/ mac
                self.font = """font: 14pt \"helvetica\"; """
                self.combo_box_item_list_color = """color: #000000; """
            elif 'linux' in sys.platform.lower(): # linux
                self.font = """font: 9pt \"helvetica\"; """
                self.combo_box_item_list_color = """color: #FFFFFF; """
            else: # windows
                self.font = """font: 11pt \"helvetica\"; """
                self.font_italic = """font: 10pt italic \"helvetica\"; """
                self.combo_box_item_list_color = """color: #FFFFFF; """
            
            
# ======== Push Buttons ==========================================
# TODO: Revert to 35px big button height once remove 1.5mm buttons
            self.big_buttons = """ 
QPushButton {
    background: solid #4c326f;
    color: #FFFFFF;
    font-weight: bold;
    border-width: 2px;
    border-color: #000000; 
    border-radius: 5px;
    min-width: 75px;
    min-height: 30px;
    /* max-width: 150px; */
    max-height: 30px; """
            self.big_buttons += self.font
            self.big_buttons += """
}
QPushButton:pressed {
    border-style: solid;
    background: solid #68478c;
}
QPushButton:!pressed {
    border-style: none;
    background: solid #4c326f;
}
QPushButton:disabled {
    color: gray;
} """

            self.big_buttons_checkable = """
QPushButton {
    background: solid #4c326f;
    color: #FFFFFF;
    font-weight: bold;
    border-width: 2px;
    border-color: #000000; 
    border-radius: 5px;
    min-width: 75px;
    min-height: 35px;
    /* max-width: 150px; */
    max-height: 35px; """
            self.big_buttons_checkable += self.font
            self.big_buttons_checkable += """
}
QPushButton:checked {
    border-style: solid;
    background: solid #68478c;
}
QPushButton:!checked {
    border-style: none;
    background: solid #4c326f;
}
QPushButton:disabled {
    color: gray;
} """

            self.icon_buttons = """
QPushButton {
    background: solid #4c326f;
    color: #FFFFFF;
    font-weight: bold;
    border-width: 2px;
    border-color: #000000; 
    border-radius: 5px;
    min-height: 25px;
} 
QPushButton:checked {
    border-style: solid;
    background: solid #68478c;
}
QPushButton:!checked {
    border-style: none;
    background: solid #4c326f;
}
QPushButton:disabled {
    color: gray;
} """

            # Tool Button/ Menu Button
            self.tool_button = ""
            # Create Large Custom Button Stylesheet ======(MAC)=
            if 'darwin' in sys.platform.lower():
                self.tool_button += """ 
QToolButton {
    background: solid #919191; 
    color: #FFFFFF; 
    font-weight: bold;    
    border-width: 2px;
    border-color: #000000; 
    border-radius: 5px;
    min-height: 30px;
    max-height: 30px;
    outline: none; """
                self.tool_button += self.font
                self.tool_button += """
}
"""
        # Create Large Custom Button Stylesheet ======(UNKNOWN)=
            else:
                self.tool_button += """ 
QToolButton {
    background: solid #4c326f; 
    color: #FFFFFF; 
    border-width: 2px;
    border-color: #000000; 
    border-radius: 5px;
    min-height: 30px;
    max-height: 30px;
    outline: none; """
                self.tool_button += self.font
                self.tool_button += """
}
"""
            # Tool button: Common to all platforms
            self.tool_button += """ 
QToolButton:pressed {
    background: solid #68478c; 
}
QToolButton:!pressed {
    background: solid #4c326f; 
}
"""



# ======== Combo Boxes ==========================================
            self.combo_boxes = """
QComboBox { """
            self.combo_boxes += self.font
            self.combo_boxes += """
    border: 1px solid gray;
    border-radius: 5px;
} 
"""
            self.combo_boxes += """
QAbstractItemView { """
            self.combo_boxes += self.combo_box_item_list_color
            self.combo_boxes += self.font
            self.combo_boxes += """
}
"""

# ======== Spin Boxes ======================================
            self.spin_boxes = """ 
QDoubleSpinBox {
            """
            self.spin_boxes += self.font
            self.spin_boxes += """
}
"""

# ======== Labels ==========================================
            self.labels = """
QLabel {
    color: #FFFFFF;
    font-weight: bold; """
            self.labels += self.font
            self.labels += """ 
} """


            self.background_frames = """
QFrame {
    background: solid #221734;
    font-weight: bold;
} """

            self.text_boxes = """
QTextEdit {
    background: solid #FFFFFF; 
    border-radius: 5px; """
            self.text_boxes += self.font
            self.text_boxes += """
} 
"""

            self.text_boxes += """
QLineEdit {
    background: solid #FFFFFF; 
    border-radius: 5px; """
            self.text_boxes += self.font
            self.text_boxes += """
} 
"""

# ======= Checkboxes =======
            self.check_boxes = """
QCheckBox {
    color: #FFFFFF;
    font-weight: bold; 
    """
            self.check_boxes += self.font
            self.check_boxes += """
} 
QCheckBox:disabled {
    color: gray;
}
"""
# ======= GroupBoxes =======
            self.groupboxes = """
QGroupBox { 
     border: 2.5px solid white; 
     border-radius: 5px; 
 } 
 """

#             self.monitor_frame = """
# QFrame {

# }
# """

app_style = AppStyleSheets()

PURPLE_LIGHT = '#68478c' # Button Off (was Background)
PURPLE_MID = '#4c326f' # Button on (was Button OnPressed Button
PURPLE_DARK = '#221734' # Background (was Button Off)
