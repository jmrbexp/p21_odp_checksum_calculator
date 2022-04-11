# debug_file.py: this file contains operations to read/write settings to a file
import time
from find_files import get_hex_directory

class HexFileOutClass():
    def __init__(self, parent=None):
        pass
        self.base_file_name = "hex_file_out"
        self.file_dir = get_hex_directory()
        # self.file_name = "DEBUG_output.txt"
        # self.file_path = self.file_dir + self.file_name

    def close_file(self, file_target):
        try:
            file_target.close()
        except IOError:
            pass
            # print("could not close settings file.")

    def create_file(self, serial_string, file_string): # Says Create, but actually will append if file already exists
        time_string = time.strftime("%Y%m%d_%H%M%S")
        self.file_path = self.file_dir + self.base_file_name + '_' + serial_string + '_' + time_string + '.txt'
        # print(self.file_path)
        write_file_target = self.open_file_for_append()
        if not write_file_target:
            # print("could not open write file target: " + str(self.file_path))
            return False

        try:
            write_file_target.write(str(file_string))
            write_file_target.close()
            return True
        except IOError:
            # print("could not write to file target: " + str(self.file_path))
            return False

    def open_file_for_write(self):
        try:
            target = open(self.file_path, 'w')
            return target
        except IOError:
            # print("could not open to file " + str(self.file_path))
            return False

    def open_file_for_append(self):
        try:
            target = open(self.file_path, 'a')
            return target
        except IOError:
            # print("could not open to file " + str(self.file_path))
            return False

    def open_file_for_read(self):
        try:
            target = open(self.file_path, 'r')
            return target
        except IOError:
            # print("could not write to file " + str(self.file_path))
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


class HexFileInClass():
    def __init__(self, parent=None):
        pass

    def import_log_file(self, file_path): # parse the file, return the sound data and the constant
        # print("import")
        self.file_path = file_path
        self.target = self.open_file_for_load()
        if not self.target: # if file did not open properly exit the routine
            # print("no target...")
            return
        # parse the file
        # print("parsing")
        self.parse_log_file()
        # print("done parsing")
        # Return pertinent values to the parent
        return self.spectrum_data_list

    def close_file(self, file_target):
        try:
            file_target.close()
        except IOError:
            pass
            # print("could not close settings file.")

    def open_file_for_load(self):
        try:
            target = open(self.file_path, 'r')
            return target
        except IOError:
            # print("could not read from file " + str(self.file_path))
            return False

    def parse_log_file(self):
        # Clear local variables used in calculations

        # Read Contents of file in to local variables
        line_buffer = self.read_line()
        while len(line_buffer):
            self.parse_log_file_line(line_buffer)
            line_buffer = self.read_line()


    def parse_log_file_line(self, line_buffer):
        if not self.waiting_for_data():
            # Look for a Header
            if self.spectrum_data_header in line_buffer:
                # print("spectrum data header!")
                self.waiting_for_spectrum_data = True
            elif self.audio_db_constant_header in line_buffer:
                pass
                # print("audio db constant header!")
        elif self.waiting_for_spectrum_data:
            self.spectrum_data_string = line_buffer
            try:
                self.spectrum_data_list = eval(line_buffer)
            except:
                # print("could not convert spectrum data!")
                self.spectrum_data_list = []
            # print("getting spectrum data...")
            # print("- string size: " + str(len(self.spectrum_data_string)))
            # print("- list size: " + str(len(self.spectrum_data_list)))
            # for this_item in self.spectrum_data_list:
            #     print(str(this_item[0]))
            # for this_item in self.spectrum_data_list:
            #     print(str(this_item[1]))
            #     raw_input("press enter to continue>")

    def waiting_for_data(self):
        if self.waiting_for_spectrum_data:
            return True
        else:
            return False

    def read_line(self):
        if not self.target:
            # print("no target")
            return ""
        try:
            line_buffer = self.target.readline()
            # print("got line")
        except IOError:
            # print("io error")
            return ""
        return line_buffer

    # def remove_comments_from_line(self, line_buffer):
    #     if '#' in line_buffer:
    #         line_buffer = line_buffer[:line_buffer.index('#')]
    #     return line_buffer

    # def replace_common_separators_with_spaces(self, line_buffer):
    #     line_buffer = line_buffer.replace(',', ' ')
    #     line_buffer = line_buffer.replace('[', ' ')
    #     line_buffer = line_buffer.replace(']', ' ')
    #     line_buffer = line_buffer.replace('(', ' ')
    #     line_buffer = line_buffer.replace(')', ' ')
    #     line_buffer = line_buffer.replace('"', ' ')
    #     line_buffer = line_buffer.replace('\n', ' ') # new line
    #     return line_buffer

# sound_test_log_out = HexFileOutClass()
hex_file_in = HexFileInClass()

# Application Execution Start (if this is the main file, typically it will not be)                                                                                                                                                                                                                                                                                                                                                           
if __name__ == '__main__':
    print("hex_files.py is main application. For Testing Purposes Only!")


