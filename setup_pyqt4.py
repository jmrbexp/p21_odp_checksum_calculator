# Packaging Script for Program
# - Created by J.Moon 20191227

# Special Libraries: PyQtGraph/ Readline

# Compiling The Program
# OS X: python setup_*.py bdist_mac
# Windows/Linux: python setup_*.py build
# Output Directory: build/

application_title = "Pump Gen3 - Application Hex File - Checksum Calculator" #what you want to application to be called
main_python_file = "pump_gen3_checksum.py" #the name of the python file you use to run the program

import sys
import distutils
import os
from cx_Freeze import setup, Executable

includes = ["atexit","re","sip","readline"]#,"scipy"]

target_name = "pump_gen3_app_checksum"
if sys.platform == "win32":  # Windows
    packages = ['numpy', 'pyqtgraph']#['scipy.sparse.linalg', 'scipy.integrate']
    #base = "Console"      
    base = "Win32GUI"  # This option forces console window NOT to open
    includefiles = [('images/r_icon.png', 'images/r_icon.png')]
    # includefiles += [('images/blue_circle_96.png', 'images/blue_circle_96.png')]
    # includefiles += [('images/green_circle_96.png', 'images/green_circle_96.png')]
    # includefiles += [('images/red_circle_96.png', 'images/red_circle_96.png')]
    # includefiles += [('images/white_circle_96.png', 'images/white_circle_96.png')]
    # includefiles += [('images/yellow_circle_96.png', 'images/yellow_circle_96.png')]
    includefiles += [('logs/empty_log.txt', 'logs/empty_log.txt')]
    includefiles += [('settings.ini', 'settings.ini')]
    target_name += ".exe"
    build_base_dir = "build/pump_gen3_app_checksum"
    build_dir_extension = "exe.%s-%s" % (distutils.util.get_platform(), sys.version[0:3])
    build_final_dir = os.path.join(build_base_dir, build_dir_extension)                                    
elif sys.platform == "darwin": # Mac
    packages = [] # ['scipy.sparse.linalg', 'scipy.integrate']
    includes += ["PyQt4.QtGui", "PyQt4.QtCore", "PyQt4.QtSvg"] #this inclusion of libraries...
    # - keeps the app from getting confused with which version of Qt to use, when one exists 
    # -- on the end user's computer (it uses the local copy packaged with the app)
    # Note: couldn't use , "PyQt4.QtXml" for some reason (not found), but didn't need for this app (20190618)
    base = None
    includefiles = []
else: # Linux
    base = "Console"
    includefiles = []
    build_base_dir = "build/modbus_control"
    build_dir_extension = "exe.%s-%s" % (distutils.util.get_platform(), sys.version[0:3])
    build_final_dir = os.path.join(build_base_dir, build_dir_extension)                                    

Exe_Target = Executable(
    # what to build
    script = "pump_gen3_checksum.py",
    initScript = None,
    base = base,
    targetName = target_name,
    #compress = True,
    #copyDependentFiles = True,
    #appendScriptToExe = False,
    #appendScriptToLibrary = False,
    icon = None
)


# TODO: Get extensions directory to copy automatically
# def copy_dir(dir_path):
#     #dir_path = 'extensions'
#     # base_dir = os.path.join(module_dir, dir_path)
#     base_dir = dir_path
#     for (dirpath, dirnames, files) in os.walk(base_dir):
#         for this_file in files:
#             yield os.path.join(dirpath.split('/', 1)[1], this_file)

# TODO: get rid of unneeded modules like tkinter by creating the variable
# excludes = ["tkinter"] 
# - then add , 
# --- "excludes": excludes
# -----  to the 'options' line
if sys.platform != "darwin": # Windows:
    setup(
        name = application_title,
        version = 1,
        description = "Testing Application",
        options = {"build_exe" : {"build_exe" : build_final_dir,"includes" : includes,'include_files':includefiles,'packages': packages, 
        #'zip_include_packages':['PyQt4', 'pyqtgraph'], 
        'excludes': ['PySide', 'Tkinter', 'collections.sys', 'collections._weakref']}}, # , 'collections.abc' # collections for later versions of cx_freeze
        executables = [Exe_Target],
        # package_data = {'' : [file for file in copy_dir("extensions/")]},
        )
else: #if sys.platform == "darwin": # Mac
    setup(
        name = application_title,
        version = 1,
        description = "Testing Application",
        options = {"build_exe" : {"includes" : includes, 'include_files':includefiles }},
        executables = [Exe_Target],
        package_data = {'' : [file for file in copy_dir("extensions/", "extensions/")]},
        )
