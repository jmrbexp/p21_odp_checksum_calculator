# debug_file.py: this file contains operations to read/write settings to a file
import time

from numpy import byte
from find_files import get_hex_directory

class IntelHexFileProperties():
    def __init__(self, parent=None):
        self.RECORD_TYPE_DATA = 0x00
        self.RECORD_TYPE_END_OF_FILE = 0x01
        self.RECORD_TYPE_EXTENDED_SEGMENT_ADDRESS = 0x02
        self.RECORD_TYPE_START_SEGMENT_ADDRESS = 0x03
        self.RECORD_TYPE_EXTENDED_LINEAR_ADDRESS = 0x04
        self.RECORD_TYPE_START_LINEAR_ADDRESS = 0x05

    def convert_line_string_to_list_of_integers(self, line_string):
        # Should already be length validated before completing
        line_string = line_string.replace(":", "")
        string_buffer = ""
        return_list = []
        for this_index in range(len(line_string)):
            string_buffer += line_string[this_index]
            if len(string_buffer) == 2:
                return_list.append(int(string_buffer, 16))
                string_buffer = ""
        return return_list

    def convert_u32_to_list_of_u8s(self, value_u32):
        return_list = []
        # Big Endian
        return_list.append(value_u32 >> 24 & 0xFF)
        return_list.append(value_u32 >> 16 & 0xFF)
        return_list.append(value_u32 >> 8 & 0xFF)
        return_list.append(value_u32 & 0xFF)
        return return_list



intel_hex_properties = IntelHexFileProperties()


# class HexFileOutClass():
#     def __init__(self, parent=None):
#         pass
#         self.base_file_name = "hex_file_out"
#         self.file_dir = get_hex_directory()
#         # self.file_name = "DEBUG_output.txt"
#         # self.file_path = self.file_dir + self.file_name

#     def close_file(self, file_target):
#         try:
#             file_target.close()
#         except IOError:
#             pass
#             # print("could not close settings file.")

#     def create_file(self, serial_string, file_string): # Says Create, but actually will append if file already exists
#         time_string = time.strftime("%Y%m%d_%H%M%S")
#         self.file_path = self.file_dir + self.base_file_name + '_' + serial_string + '_' + time_string + '.txt'
#         # print(self.file_path)
#         write_file_target = self.open_file_for_append()
#         if not write_file_target:
#             # print("could not open write file target: " + str(self.file_path))
#             return False

#         try:
#             write_file_target.write(str(file_string))
#             write_file_target.close()
#             return True
#         except IOError:
#             # print("could not write to file target: " + str(self.file_path))
#             return False

#     def open_file_for_write(self):
#         try:
#             target = open(self.file_path, 'w')
#             return target
#         except IOError:
#             # print("could not open to file " + str(self.file_path))
#             return False

#     def open_file_for_append(self):
#         try:
#             target = open(self.file_path, 'a')
#             return target
#         except IOError:
#             # print("could not open to file " + str(self.file_path))
#             return False

#     def open_file_for_read(self):
#         try:
#             target = open(self.file_path, 'r')
#             return target
#         except IOError:
#             # print("could not write to file " + str(self.file_path))
#             return False

#     def remove_comments_from_line(self, line_buffer):
#         if '#' in line_buffer:
#             line_buffer = line_buffer[:line_buffer.index('#')]
#         return line_buffer

#     def replace_common_separators_with_spaces(self, line_buffer):
#         line_buffer = line_buffer.replace(',', ' ')
#         line_buffer = line_buffer.replace('[', ' ')
#         line_buffer = line_buffer.replace(']', ' ')
#         line_buffer = line_buffer.replace('(', ' ')
#         line_buffer = line_buffer.replace(')', ' ')
#         line_buffer = line_buffer.replace('"', ' ')
#         line_buffer = line_buffer.replace('\n', ' ') # new line
#         return line_buffer


class HexFileInClass():
    def __init__(self, parent=None):
        self.CHECKSUM_CALC_START_ADDRESS = 0x2000
        self.CHECKSUM_CALC_END_ADDRESS = 0x17DFC # Exclusive (not included in calc)
        self.PROCESSOR_ROM_SIZE = 0x20000
        self.MIN_LINE_LENGTH = 8
        pass
        self.init_memory_map()

    def init_memory_map(self):
        self.test_counter = 0
        self.base_address = 0x0000
        self.TEST_COUNTER_PRINT_LIMIT = 10
        self.memory_map = [0xFF]*self.PROCESSOR_ROM_SIZE
        pass

    def import_log_file(self, file_path): # parse the file, return the sound data and the constant
        self.calculated_checksum = 0xFFFFFF
        # print("import")
        self.file_path = file_path
        self.target = self.open_file_for_load()
        if not self.target: # if file did not open properly exit the routine
            # print("no target...")
            return
        # parse the file
        # print("parsing")
        self.parse_hex_file()
        # print("done parsing")
        # Return pertinent values to the parent
        return self.calculated_checksum

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

    def parse_hex_file(self):
        # Clear local variables used in calculations
        self.init_memory_map()

        # Read Contents of file in to local variables
        line_buffer = self.read_line()
        while len(line_buffer):
            self.parse_hex_file_line(line_buffer)
            line_buffer = self.read_line()
        # print(str(self.memory_map[self.CHECKSUM_CALC_START_ADDRESS:self.CHECKSUM_CALC_END_ADDRESS+6]))
        self.validate_rom_checksum()

    def validate_rom_checksum(self):
        u32_counter = 0
        u32_accumulator = 0
        calculated_checksum = 0 # start value - definied in bootloader firmware
        # use memory map to read the current checksum stored in rom.
        stored_checksum = self.memory_map[self.CHECKSUM_CALC_END_ADDRESS:self.CHECKSUM_CALC_END_ADDRESS+4]
        # use memory map to calculate the current checksum based on rom contents.
        for this_address in range(self.CHECKSUM_CALC_START_ADDRESS, self.CHECKSUM_CALC_END_ADDRESS):
            u32_accumulator += self.memory_map[this_address]
            u32_counter += 1
            if u32_counter == 4: # checksum is calculated in 32 bit chunks, collect four bytes then add in.
                calculated_checksum += u32_accumulator
                u32_accumulator = 0
                u32_counter = 0
        print(str(stored_checksum))
        print(hex(calculated_checksum))
        # Now convert calculated checksum to a list, for easy printing of the desired firmware line.
        calculated_checksum_list = intel_hex_properties.convert_u32_to_list_of_u8s(calculated_checksum)
        print(calculated_checksum_list)
        if calculated_checksum_list == stored_checksum:
            print("firmware stored checksum matches calculated checksum!")
        else:
            print("firmware checksum does not match calculated checksum. please update firmware source code to the following.")
            output_line = "(ChecksumBytes.c):\nCHECKSUM[6] = {"
            output_line += str(calculated_checksum_list[0]) + ", "
            output_line += str(calculated_checksum_list[1]) + ", "
            output_line += str(calculated_checksum_list[2]) + ", "
            output_line += str(calculated_checksum_list[3]) + "};\n"
            print(output_line)
        # output_line += 


    def parse_hex_file_line(self, unfiltered_line):
        # Validate Line
        if not ":" in unfiltered_line:
            print("invalid line: no colon. line skipped.")
            return
        split_line = unfiltered_line.split(":")
        if len(split_line) < 2:
            print("invalid line: no data after colon. line skipped")
            return
        line_buffer = split_line[1] # Get Data for line buffer
        line_buffer = line_buffer.replace('\n', '') # Remove new line character
        if len( line_buffer ) < self.MIN_LINE_LENGTH: 
            print("line too short. line skipped.")
            return
        # else -> valid line

        # Split the Line up to to Component Parts
        line_buffer_list = intel_hex_properties.convert_line_string_to_list_of_integers(line_buffer)
        byte_count = line_buffer_list[0]
        address_16 = line_buffer_list[1]*256 + line_buffer_list[2]
        record_type = line_buffer_list[3]
        line_data = line_buffer_list[4:-1]
        line_checksum = line_buffer_list[-1]
        expected_checksum = (256 - (sum(line_buffer_list[:-1]) & 0xFF)) & 0xFF
        if line_checksum != expected_checksum:
            print("WARNING: line checksum failure! " + line_buffer + " - expected " + str(expected_checksum))

        if record_type == intel_hex_properties.RECORD_TYPE_END_OF_FILE:
            print("end of file...")
            pass
        elif record_type == intel_hex_properties.RECORD_TYPE_START_SEGMENT_ADDRESS:
            print("program execution start address: " + str(line_data))
        elif record_type == intel_hex_properties.RECORD_TYPE_EXTENDED_SEGMENT_ADDRESS:
            # print("data address (extended): " + str(line_data))
            self.base_address = 16 * (line_data[0]*256 + line_data[1])
                # "This is multiplied by 16 and added to each subsequent data record address to form the starting address for the data."
                # " This allows addressing up to one megabyte of address space."" 
        elif record_type == intel_hex_properties.RECORD_TYPE_START_LINEAR_ADDRESS:
            print("program linear address" + str(line_data))
        elif record_type == intel_hex_properties.RECORD_TYPE_EXTENDED_LINEAR_ADDRESS:
            print("program linear address (extended)" + str(line_data))
        elif record_type == intel_hex_properties.RECORD_TYPE_DATA:
            # print("data address: " + hex(self.base_address + address_16) + " (" + str(address_16) + ")")
            self.put_data_in_memory_map(address_16, line_data)
        # DEBUG PRINTING
        # if self.test_counter in range(215,250):
        #     print(line_buffer)
        #     print(line_buffer_list)
        #     print("- address: " + hex(address_16))
        #     print("- byte count: " + hex(byte_count))
        #     print("- record_type: " + hex(record_type))
        #     print(" - line data: " + str(line_data))
        #     print(" - line checksum: " + hex(line_checksum))
        #     print(" - expected checksum: " + hex(expected_checksum))
        # self.test_counter = self.test_counter + 1


            # record_output = str(hex(address)) + '\t' + str(byte_count) + '\t'
            # if record_type == 0:
            #     record_output += 'data'
            #     record_output += '\t\t' + line_buffer[8:(8+2*(byte_count))]
            # elif record_type == 1:
            #     record_output += 'end of file'
            # elif record_type == 2:
            #     record_output += 'ext segment addr'
            # elif record_type == 3:
            #     record_output += 'start segment address'
            # elif record_type == 4:
            #     record_output += 'ext linear addr'
            # elif record_type == 5:
            #     record_output += 'start linear address'
            # print(record_output)



        # if not self.waiting_for_data():
        #     # Look for a Header
        #     if self.spectrum_data_header in line_buffer:
        #         # print("spectrum data header!")
        #         self.waiting_for_spectrum_data = True
        #     elif self.audio_db_constant_header in line_buffer:
        #         pass
        #         # print("audio db constant header!")
        # elif self.waiting_for_spectrum_data:
        #     self.spectrum_data_string = line_buffer
        #     try:
        #         self.spectrum_data_list = eval(line_buffer)
        #     except:
        #         # print("could not convert spectrum data!")
        #         self.spectrum_data_list = []
            # print("getting spectrum data...")
            # print("- string size: " + str(len(self.spectrum_data_string)))
            # print("- list size: " + str(len(self.spectrum_data_list)))
            # for this_item in self.spectrum_data_list:
            #     print(str(this_item[0]))
            # for this_item in self.spectrum_data_list:
            #     print(str(this_item[1]))
            #     raw_input("press enter to continue>")

    # def waiting_for_data(self):
    #     if self.waiting_for_spectrum_data:
    #         return True
    #     else:
    #         return False

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

    def put_data_in_memory_map(self, start_address_u16, data_list):
        # note: incoming start_address is expected to not be adjusted to RECORD_TYPE_EXTENDED_SEGMENT_ADDRESS yet.
        adjusted_start_address_u16 = start_address_u16 + self.base_address
        for this_data_index in range(len(data_list)):
            write_address = adjusted_start_address_u16 + this_data_index
            if write_address >= self.PROCESSOR_ROM_SIZE:
                print("data out of range. skipping line data")
                break 
            # - Add data point to memory map
            this_data_byte = data_list[this_data_index]
            self.memory_map[write_address] = int(this_data_byte) # Force a copy by casting

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
    file_path = "test_hex.hex"
    hex_file_in.import_log_file(file_path)
