# init_file.py: this file contains operations to read/write settings to a file

import time


# InitFileClass: provides functions to allow an app to save some settings at app closing and restore them at startup
# - ie. Currently connected serial port, currently connected audio port
class InitFileClass():
    def __init__(self, parent=None):
        self.LOAD_INIT_NO_ERROR = 0
        self.LOAD_INIT_OPEN_ERROR = 1
        self.LOAD_INIT_IO_ERROR = 2
        self.SAVE_INIT_NO_ERROR = 0
        self.SAVE_INIT_OPEN_ERROR = 1
        self.SAVE_INIT_IO_ERROR = 2
        self.CATEGORY_STRING_PORT = "port"
        self.CATEGORY_STRING_LAST_DIR = "last_dir"
        self.CATEGORY_STRINGS = [self.CATEGORY_STRING_PORT, self.CATEGORY_STRING_LAST_DIR] # For writing at app shut down REVIEW: NOT USED
        self.CATEGORY_ID_PORT = 0
        self.separator = " "
        self.init_file_read_tables()
        self.init_file_write_tables()

    # Call this after reading the file,  and restore the value where applicable
    def get_last_selected_directory_from_read_table(self):
        if not self.CATEGORY_STRING_LAST_DIR in self.init_file_read_categories:
            value = "" # Return empty string to signify setting does not exist
        else:
            index = self.init_file_read_categories.index(self.CATEGORY_STRING_LAST_DIR)
            value = self.init_file_read_values[index]
        return value
    # Call this anytime before shutdown, to ensure this value is written to file at shutdown
    def update_last_selected_directory(self, last_selected_directory_path):
        # if exists in write table already
        if self.CATEGORY_STRING_LAST_DIR in self.init_file_write_categories:
            index = self.init_file_write_categories.index(self.CATEGORY_STRING_LAST_DIR)
            self.init_file_write_values[index] = last_selected_directory_path
        # if not, add entry
        else:
            self.init_file_write_categories.append(self.CATEGORY_STRING_LAST_DIR)   
            self.init_file_write_values.append(last_selected_directory_path)

    # These tables are for storing data before writing them to file
    def init_file_write_tables(self):
        self.init_file_write_categories = [] # Read from Column 1 of each line
        self.init_file_write_values = [] # Read from Column 2 of each line

    # These tables are for storing data after reading them from file
    def init_file_read_tables(self):
        self.init_file_read_categories = [] # Read from Column 1 of each line
        self.init_file_read_values = [] # Read from Column 2 of each line

    # load_init_file: main function (startup) -> reads in 'init_file' and interprets contents. 
    # - returns NO ERROR if read properly, returns error code if file was not read or file was corrupt
    def load_init_file(self, file_path):
        read_file_target = self.open_init_file_for_load(file_path)
        self.init_file_read_tables() # clear existing data if exists
        self.init_file_write_tables() # clear existing data if exists
        # make sure file opened properly
        if not read_file_target:
            return self.LOAD_INIT_OPEN_ERROR
        # read the first line
        try:
            line_buffer = read_file_target.readline()
        except IOError:
            return self.LOAD_INIT_OPEN_ERROR
        # while the line buffer contains data add items to the imported settings lists
        while len(line_buffer):
            # clean line of common separators, so that ini files can be readable if desired
            line_buffer = self.remove_comments_from_line(line_buffer)
            line_buffer = self.replace_common_separators_with_spaces(line_buffer)
            # split the line so we can separate categories from their values
            split_line = line_buffer.split(maxsplit=1) # only split one time, so strings can have spaces in them
            # parse line: Store Category and Value if both exists
            if len(split_line) > 1:
                category_str = split_line[0].lower()
                value_str = split_line[1]
                self.init_file_read_categories.append(category_str)
                self.init_file_write_categories.append(category_str)
                # Auto copy to write tables for writing to settings file at app shut down
                self.init_file_read_values.append(value_str)
                self.init_file_write_values.append(value_str)
            # Read next line
            try:
                line_buffer = read_file_target.readline()
            except IOError:
                return self.LOAD_INIT_OPEN_ERROR

        self.close_init_file(read_file_target)
        return self.LOAD_INIT_NO_ERROR

    # close_init_file: closes file target objects for use by other applications
    def close_init_file(self, file_target):
        try:
            file_target.close()
        except IOError:
            pass
            # print("could not close settings file.")

    # save_init_file: main function (shutdown) -> saves in 'init_file' writing settings to be restored at next app startup.
    def save_init_file(self, file_path):
        file_buffer = ""
        line_buffer = ""
        write_file_target = self.open_init_file_for_save(file_path)
        # Make sure file opened properly
        if not write_file_target:
            # print("could not open write file target: " + str(file_path))
            return self.SAVE_INIT_OPEN_ERROR
        # Write all settings to file buffer
        # line_buffer = self.CATEGORY_STRINGS[0] + self.separator + str(this_value)
        for this_index in range(len(self.init_file_write_categories)):
            line_buffer = self.init_file_write_categories[this_index] + self.separator + str(self.init_file_write_values[this_index]) + '\n'
            file_buffer += line_buffer
        # Write file buffer to the target file
        try:
            write_file_target.write(file_buffer)
            write_file_target.close()
            return self.SAVE_INIT_NO_ERROR
        except IOError:
            # print("could not write to file target: " + str(file_path))
            return self.SAVE_INIT_IO_ERROR

    # open_init_file_for_save: basic routine to 'safely' open a file for writing 
    def open_init_file_for_save(self, file_path):
        try:
            target = open(file_path, 'w')
            return target
        except IOError:
            # print("could not open to file " + str(file_path))
            return False

    # open_init_file_for_load: basic routine to 'safely' open a file for reading 
    def open_init_file_for_load(self, file_path):
        try:
            target = open(file_path, 'r')
            return target
        except IOError:
            # print("could not write to file " + str(file_path))
            return False

    def remove_comments_from_line(self, line_buffer):
        if '#' in line_buffer:
            line_buffer = line_buffer[:line_buffer.index('#')]
        return line_buffer

    def replace_common_separators_with_spaces(self, line_buffer):
        line_buffer = line_buffer.replace(',', ' ')
        line_buffer = line_buffer.replace('[', ' ')
        line_buffer = line_buffer.replace(']', ' ')
        line_buffer = line_buffer.replace('(', ' ')
        line_buffer = line_buffer.replace(')', ' ')
        line_buffer = line_buffer.replace('"', ' ')
        line_buffer = line_buffer.replace('\n', ' ') # new line
        return line_buffer

init_settings = InitFileClass()
