import imp
import os
import sys


def main_is_frozen():
   return (hasattr(sys, "frozen") or # new py2exe
           hasattr(sys, "importers") # old py2exe
           or imp.is_frozen("__main__")) # tools/freeze

def get_main_dir():
   if main_is_frozen():
       # print 'Running from path', os.path.dirname(sys.executable)
       return os.path.dirname(sys.executable)
   return os.path.dirname(sys.argv[0])


# ========== GetImagesDirectories ============
def get_mac_working_directory(): # TODO: should be able to replace this with the 'get_main_dir' method
    CURRENT_DIR_PATH = os.path.dirname(sys.executable)
 
    MAC_APP_STRING = '.app/Contents/MacOS'
    PYTHON_LIBRARY_STRING = '/library'
    index  = CURRENT_DIR_PATH.rfind(MAC_APP_STRING)
 
    if index > 0:   # If Project Has been built into an app (If Not: index is -1)
        MPHIDFLASH_DIR_STRING_LENGTH = CURRENT_DIR_PATH.rfind(MAC_APP_STRING) + len(MAC_APP_STRING)
        MPHIDFLASH_DIR_PATH = CURRENT_DIR_PATH[:MPHIDFLASH_DIR_STRING_LENGTH]
        #print 'Built App: Calculated MPHIDFlash Dir Path -> ' + MPHIDFLASH_DIR_PATH
        return MPHIDFLASH_DIR_PATH + '/'
    else:           # If Project has Not been built into an app (run via installed$
        return ''
# ========== GetImagesDirectories ========end=

def get_mac_application_directory():
    CURRENT_DIR_PATH = os.path.dirname(os.path.abspath(__file__))
    MAC_APP_STRING = '.app/Contents/MacOS'
    PYTHON_LIBRARY_STRING = '/library'
    index  = CURRENT_DIR_PATH.rfind(MAC_APP_STRING)

    if index > 0:   # If Project Has been built into an app (If Not: index is -1)
        APPLICATION_DIR_STRING_LENGTH = CURRENT_DIR_PATH.rfind(MAC_APP_STRING) + len(MAC_APP_STRING)
        APPLICATION_DIR_PATH = CURRENT_DIR_PATH[:APPLICATION_DIR_STRING_LENGTH]
        #print 'Built App: Calculated Application Dir Path -> ' + APPLICATION_DIR_PATH
        return APPLICATION_DIR_PATH
    else:           # If Project has Not been built into an app (run via installed Python)
        return ''

def get_images_directory():
    # Note: files embedded in an executable (pyinstaller --one-file) can be found using the MEIPASS variable
    # - We decided to externally copy image files and configuration files, so that they can be edited and replaced
    # -- so we are not looking at MEIPASS in those builds yet.
    # try:
    #     this_dir = sys._MEIPASS
    #     print("MEIPASS existed using: " + this_dir)
    # except:
    #     print("MEIPASS did not exist")

    # ========== Project Configuration Constants =================
    if 'darwin' in sys.platform.lower():
        PIXMAP_DIR_BASE = get_mac_working_directory()
        PIXMAP_DIR = PIXMAP_DIR_BASE + "images/"
    else:
        DIR = get_main_dir()
        if DIR:
            DIR += '/'
        PIXMAP_DIR = DIR + "images/"
        # PIXMAP_DIR_BASE = os.path.dirname(os.path.realpath(__file__)) + "/"
    return PIXMAP_DIR

def get_logs_directory():
    # ========== Project Configuration Constants =================
    if 'darwin' in sys.platform.lower():
        LOGS_DIR_BASE = get_mac_working_directory()
        LOGS_DIR = LOGS_DIR_BASE + "logs/"
    else:
        DIR = get_main_dir()
        if DIR:
            DIR += '/'
        LOGS_DIR = DIR + "logs/"
    return LOGS_DIR

def get_icon_path():
    icon_name = "r_icon.png"
    dir_path = get_images_directory()
    return dir_path + icon_name

def get_splash_image_path():
    icon_name = "regal_icon.png"
    dir_path = get_images_directory()
    return dir_path + icon_name

def get_colored_circle_icon_path(color_string):
    icon_name = color_string + "_circle_96.png"
    dir_path = get_images_directory()
    return dir_path + icon_name

def get_init_file_directory(): # note this file must be in the location of the init file
    if 'darwin' in sys.platform.lower():
        DIR_BASE = get_mac_working_directory()
        DIR = DIR_BASE + ""
    else:
        # DIR = os.path.dirname(os.path.realpath(__file__)) + "/"
        DIR = get_main_dir()
        if DIR:
            DIR += '/'
        # DIR = os.path.dirname(os.path.(sys.argv[0])) + "/"
    return DIR