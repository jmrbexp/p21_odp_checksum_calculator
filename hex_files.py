# hex_files.py: this file contains operations to read/write/analyze hex files

# Module Imports
from numpy import byte
import time
# - time: python 3.8 clock patch
try:
    time.clock() # python 3.7 and below
except:
    time.clock = time.perf_counter # python 3.8+

# Local Backend Imports
from app_configuration import app_config
# from find_files import get_hex_directory
from memory_map_stm32_64kb import MemoryMap_STM32_64kB
from type_conversions import type_converter

# IntelHexFileProperties: Class containing basic functions and properties for interpreting Intel Hex Files.
class IntelHexFileProperties():
    def __init__(self, parent=None):
        # Define Record Types (First 2 characters of each hex file line)
        self.RECORD_TYPE_DATA = 0x00
        self.RECORD_TYPE_END_OF_FILE = 0x01
        self.RECORD_TYPE_EXTENDED_SEGMENT_ADDRESS = 0x02
        self.RECORD_TYPE_START_SEGMENT_ADDRESS = 0x03
        self.RECORD_TYPE_EXTENDED_LINEAR_ADDRESS = 0x04
        self.RECORD_TYPE_START_LINEAR_ADDRESS = 0x05


    # convert_line_string_to_list_of_integers: function to convert one hex file line into integers that can be interpreted.
    # - receives: one line of hex file (as string)
    # - returns: list of integers
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


# HexFileInClass: Class containing routines for reading and interpreting a hex file, 
# - and placing memory contents into a virtual memory map
class HexFileInClass():
    def __init__(self, memory_map_out=None, parent=None):
        self.MEMORY_MAP_OUT_MODE_CLEAR_FIRST = 0 # Clear memory when importing new hex file
        self.MEMORY_MAP_OUT_MODE_OVERWRITE = 1 # Don't Clear memory when importing new hex file
        self.MEMORY_MAP_OUT_MODE = self.MEMORY_MAP_OUT_MODE_CLEAR_FIRST
        self.serial_monitor_cb = None
        self.memory_map_out = memory_map_out

        self.START_VALUE_WRITE_FAIL_ADDRESS_MIN = -1
        self.START_VALUE_WRITE_FAIL_ADDRESS_MAX = -1

        self.BOOTLOADER_START_ADDRESS = 0x0000
        self.BOOTLOADER_END_ADDRESS = 0x1800 # Exclusive (not included in calc)
        # BOOTLOADER CHECKSUM: assummd to be at END_ADDRESS-4 (TODO: REVIEW)
        self.CHECKSUM_CALC_START_ADDRESS = 0x1800
        self.CHECKSUM_CALC_END_ADDRESS = 0x97FC # Exclusive (not included in calc)
        # self.CHECKSUM_CALC_END_ADDRESS = 0x7FFC # Exclusive (not included in calc)
        self.PROCESSOR_ROM_SIZE = 0x10000
        
        self.MIN_LINE_LENGTH = 8
        self.CHECKSUM_LENGTH_BYTES = 4
        self.CHECKSUM_CHUNK_SIZE_BYTES = 4
        # self.stored_checksum = [0]*self.CHECKSUM_LENGTH_BYTES
        self.calculated_checksum_list = [0]*self.CHECKSUM_LENGTH_BYTES
        self.init_base_address()

    # init_crc_storage(self): TODO: crc_storage has some redundancy, firmware crcs are stored globally twice
    def init_crc_storage(self):
        self.stored_bootloader_checksum = 0xFFFFFFFF
        self.calc_bootloader_checksum = 0xFFFFFFFF
        self.stored_firmware_checksum = 0xFFFFFFFF
        self.calc_firmware_checksum = 0xFFFFFFFF

    def update_crc_storage(self, stored_bootloader_crc, calc_bootloader_crc, stored_firmware_crc, calc_firmware_crc):
        self.stored_bootloader_checksum = stored_bootloader_crc
        self.calc_bootloader_checksum = calc_bootloader_crc
        self.stored_firmware_checksum = stored_firmware_crc
        self.calc_firmware_checksum = calc_firmware_crc

    def update_crc_storage_bootloader(self, stored_bootloader_crc, calc_bootloader_crc):
        self.stored_bootloader_checksum = stored_bootloader_crc
        self.calc_bootloader_checksum = calc_bootloader_crc

    def update_crc_storage_firmware(self, stored_firmware_crc, calc_firmware_crc):
        self.stored_firmware_checksum = stored_firmware_crc
        self.calc_firmware_checksum = calc_firmware_crc


    # init_base_address: initialize any memory properties specific to the processor being used
    def init_base_address(self): # Base Address is used to allow hex files to address 32-bit address space (while only putting 16-bit address in each file line)
        self.base_address = 0x0000
        self.write_failure_address_min = self.START_VALUE_WRITE_FAIL_ADDRESS_MIN # less than 0
        self.write_failure_address_max = self.START_VALUE_WRITE_FAIL_ADDRESS_MAX # max value that is still an s32 (not 'long')
        if self.MEMORY_MAP_OUT_MODE == self.MEMORY_MAP_OUT_MODE_CLEAR_FIRST:
            if self.memory_map_out:
                # print("re-init memory map")
                self.memory_map_out.init_memory_map()
                # print("re-init memory map (END)")

    # assign_memory_map_out: allows a parent class to assign a virtual memory map to place hex file interpreted data into
    def assign_memory_map_out(self, memory_map_out):
        self.memory_map_out = memory_map_out
    # import_log_file: main routine that opens, and triggers the interpretation of a hex file
    def import_log_file(self, file_path): # parse the file, return the sound data and the constant
        # self.memory_map_out = memory_map_out
        self.calculated_checksum = 0xFFFFFF
        # print("import")
        self.file_path = file_path

        # parse the file
        file_extension = self.file_path[-4:]
        # - binary files
        if file_extension == ".bin":
            self.target = self.open_binary_file_for_load()
            if not self.target: # if file did not open properly exit the routine
                print("no target...")
                return
            print("parsing binary file: " + str(time.clock()))
            self.parse_binary_file()
        # - hex/text based files
        else:
            self.target = self.open_file_for_load()
            if not self.target: # if file did not open properly exit the routine
                # print("no target...")
                return
            print("parsing hex file: " + str(time.clock()))
            self.parse_hex_file()
        print("done parsing: " + str(time.clock()))
        self.close_file(self.target)
        # Return pertinent values to the parent
        return self.calculated_checksum

    # close_file: closes file target objects for use by other applications
    def close_file(self, file_target):
        try:
            file_target.close()
        except IOError:
            pass
            # print("could not close settings file.")

    def open_binary_file_for_load(self):
        try:
            target = open(self.file_path, 'rb')
            return target
        except IOError:
            # print("could not open binary file " + str(self.file_path))
            return False

    # open_file_for_load: basic routine to 'safely' open a file for reading 
    def open_file_for_load(self):
        try:
            target = open(self.file_path, 'r')
            return target
        except IOError:
            # print("could not open standard file " + str(self.file_path))
            return False

    def get_binary_data_from_target(self):
        try: 
            binary_data = self.target.read()
            return binary_data
        except IOError:
            return False

    def parse_binary_file(self):
        # Clear local variables used in calculations
        self.init_base_address() 
        # Read Contents of file in to local variables
        binary_data = self.get_binary_data_from_target()
        if not binary_data:
            print("could not read binary data... cancelling import...")
            return
        # 
        P21_ODP_FIRMWARE_START_ADDRESS = 0x1800
        self.parse_binary_file_data(binary_data, start_address=P21_ODP_FIRMWARE_START_ADDRESS)
        # Validate
        self.calculate_bootloader_checksum()
        self.validate_rom_checksum()


    # parse_hex_file: reads in each line of a hex file and triggers interpretation of the contents.
    def parse_hex_file(self):
        # Clear local variables used in calculations
        self.init_base_address()

        # Read Contents of file in to local variables
        line_buffer = self.read_line()
        while len(line_buffer):
            self.parse_hex_file_line(line_buffer)
            line_buffer = self.read_line()
        # Validate
        self.display_message("hex file import complete.")
        if self.write_errors_detected():
            self.display_message("write failures detected in address range:\n0x{:08x} - 0x{:08x}".format(self.write_failure_address_min, self.write_failure_address_max)) 

        self.calculate_bootloader_checksum() # TODO: Move
        self.validate_rom_checksum() # TODO: Move

    def calculate_bootloader_checksum(self): # TODO: Move
        if not self.memory_map_out:
            self.display_message("bootloader checksum (calc): Fail -> No Assigned Memory Map")
            return
        stored_checksum = self.get_stored_bootloader_checksum_list()
        self.display_message("bootloader checksum (file): " + str(stored_checksum))
        # self.display_message("bootloader checksum (file): " + str(stored_checksum) + " - " + type_converter.convert_list_of_ints_to_list_of_hex(stored_checksum))
        u32_counter = 0
        u32_accumulator = 0
        calculated_checksum = 0 # start value - definied in bootloader firmware
        # use memory map to calculate the current checksum based on rom contents.
        for this_address in range(self.BOOTLOADER_END_ADDRESS-4, self.BOOTLOADER_END_ADDRESS):
            u32_accumulator += self.memory_map_out.memory_map[this_address]
            u32_counter += 1
            if u32_counter == self.CHECKSUM_CHUNK_SIZE_BYTES: # checksum is calculated in 32 bit chunks, collect four bytes then add in.
                calculated_checksum += u32_accumulator
                u32_accumulator = 0
                u32_counter = 0
        calculated_checksum_list = intel_hex_properties.convert_u32_to_list_of_u8s(calculated_checksum)
        self.display_message("bootloader checksum (calc): " + str(calculated_checksum_list))
        self.update_crc_storage_bootloader(stored_checksum, calculated_checksum_list)
        # self.display_message("bootloader checksum (calc): " + str(calculated_checksum_list)+ " - " + type_converter.convert_list_of_ints_to_list_of_hex(calculated_checksum_list))
        # if calculated_checksum_list == stored_checksum:
        #     self.display_message("firmware stored checksum matches calculated checksum!")
        # else:
        #     self.display_message("firmware checksum does not match calculated checksum. please update firmware source code to the following.")
        #     output_line = "(ChecksumBytes.c):\nCHECKSUM[6] = {"
        #     output_line += "0x00, 0x48, " # These values are fixed in the source code and not used in the calculation
        #     output_line += "0x" + "{:02x}".format(calculated_checksum_list[0]).upper() + ", "
        #     output_line += "0x" + "{:02x}".format(calculated_checksum_list[1]).upper() + ", "
        #     output_line += "0x" + "{:02x}".format(calculated_checksum_list[2]).upper() + ", "
        #     output_line += "0x" + "{:02x}".format(calculated_checksum_list[3]).upper() + "};\n"
        #     self.display_message(output_line)
        # # output_line += 

    def get_stored_bootloader_checksum_list(self): # TODO: Move
        if not self.memory_map_out:
            return []
        stored_checksum = self.memory_map_out.memory_map[self.BOOTLOADER_END_ADDRESS-4:self.BOOTLOADER_END_ADDRESS]
        return stored_checksum

    def get_stored_rom_checksum_list(self): # TODO: Move 
        if not self.memory_map_out:
            return []
        stored_checksum = self.memory_map_out.memory_map[self.CHECKSUM_CALC_END_ADDRESS:self.CHECKSUM_CALC_END_ADDRESS+4]
        return stored_checksum

    def get_calculated_rom_checksum(self): # TODO: Move
        return self.calculated_checksum_list

    def fix_rom_checksum(self): # TODO: Move
        for this_byte_index in range(len(self.calculated_checksum_list)):
            self.memory_map_out.memory_map[self.CHECKSUM_CALC_END_ADDRESS+this_byte_index] = self.calculated_checksum_list[this_byte_index] 

    # def calculate_rom_checksum_polynomial_method(self):
    #     pass
    #     for this_address in range(self.CHECKSUM_CALC_START_ADDRESS, self.CHECKSUM_CALC_END_ADDRESS):
    #         u32 = type_converter.get_u32
    #         if u32_counter == self.CHECKSUM_CHUNK_SIZE_BYTES: # checksum is calculated in 32 bit chunks, collect four bytes then add in.


    def validate_rom_checksum(self): # TODO: Move
        u32_counter = 0
        u32_accumulator = 0
        calculated_checksum = 0 # start value - definied in bootloader firmware
        # use memory map to read the current checksum stored in rom.
        # self.stored_checksum = self.memory_map[self.CHECKSUM_CALC_END_ADDRESS:self.CHECKSUM_CALC_END_ADDRESS+4]
        stored_checksum_list = self.get_stored_rom_checksum_list()

        
        # use memory map to calculate the current checksum based on rom contents.
        # self.calculate_rom_checksum_polynomial_method()
        for this_address in range(self.CHECKSUM_CALC_START_ADDRESS, self.CHECKSUM_CALC_END_ADDRESS):
            u32_accumulator += self.memory_map_out.memory_map[this_address]
            u32_counter += 1
            if u32_counter == self.CHECKSUM_CHUNK_SIZE_BYTES: # checksum is calculated in 32 bit chunks, collect four bytes then add in.
                calculated_checksum += u32_accumulator
                u32_accumulator = 0
                u32_counter = 0

        self.display_message("application checksum (file): " + str(stored_checksum_list))
        # self.display_message("application checksum (file): " + str(stored_checksum) + " - " + type_converter.convert_list_of_ints_to_list_of_hex(stored_checksum))
        # print(hex(calculated_checksum))
        # Now convert calculated checksum to a list, for easy printing of the desired firmware line.
        self.calculated_checksum_list = intel_hex_properties.convert_u32_to_list_of_u8s(calculated_checksum)
        self.display_message("application checksum (calc): " + str(self.calculated_checksum_list))
        # self.display_message("application checksum (calc): " + str(self.calculated_checksum_list) + " - " + type_converter.convert_list_of_ints_to_list_of_hex(self.calculated_checksum_list))
        if self.calculated_checksum_list == stored_checksum_list:
            self.display_message("firmware stored checksum matches calculated checksum!")
        else:
            self.display_message("firmware checksum does not match calculated checksum. please update firmware source code to the following.")
            output_line = "(ChecksumBytes.c):\nCHECKSUM[6] = {"
            output_line += "0x00, 0x48, " # These values are fixed in the source code and not used in the calculation
            output_line += "0x" + "{:02x}".format(self.calculated_checksum_list[0]).upper() + ", "
            output_line += "0x" + "{:02x}".format(self.calculated_checksum_list[1]).upper() + ", "
            output_line += "0x" + "{:02x}".format(self.calculated_checksum_list[2]).upper() + ", "
            output_line += "0x" + "{:02x}".format(self.calculated_checksum_list[3]).upper() + "};\n"
            self.display_message(output_line)
        # output_line += 
        self.update_crc_storage_firmware(stored_checksum_list, self.calculated_checksum_list)

    def parse_binary_file_data(self, binary_data, start_address=0):
        # start_address = 0
        print("parse binary file data!")
        print(binary_data)
        print("- list of integer data")
        list_of_ints_data = list(binary_data)
        print(list_of_ints_data)
        self.put_data_in_memory_map(start_address, list_of_ints_data)


    # parse_hex_file_line: interprets a single line of a hex file
    # - triggers conversion of line from string into a list of bytes
    # -- then interprets line and places in virtual memory (if virtual memory map is assigned to this instance)
    def parse_hex_file_line(self, unfiltered_line):
        # Validate Line
        if not ":" in unfiltered_line:
            self.display_message("invalid line: no colon. line skipped.")
            return
        split_line = unfiltered_line.split(":")
        if len(split_line) < 2:
            self.display_message("invalid line: no data after colon. line skipped")
            return
        line_buffer = split_line[1] # Get Data for line buffer
        line_buffer = line_buffer.replace('\n', '') # Remove new line character
        if len( line_buffer ) < self.MIN_LINE_LENGTH: 
            self.display_message("line too short. line skipped.")
            return
        # else -> valid line

        # Split the Line up to to Component Parts
        # -    :0AFDF6005301000A0048014A5EC4F0

        line_buffer_list = intel_hex_properties.convert_line_string_to_list_of_integers(line_buffer)
        byte_count = line_buffer_list[0]
        address_16 = line_buffer_list[1]*256 + line_buffer_list[2]
        record_type = line_buffer_list[3]
        line_data = line_buffer_list[4:-1]
        line_checksum = line_buffer_list[-1]

        # Caclulate the expected line checksum and validate it with the line_checksum
        expected_checksum = (256 - (sum(line_buffer_list[:-1]) & 0xFF)) & 0xFF
        if line_checksum != expected_checksum:
            self.display_message("WARNING: line checksum failure! " + line_buffer + " - expected " + str(expected_checksum))

        # Message is fully validated: Respond to the incoming record based on record_type
        if record_type == intel_hex_properties.RECORD_TYPE_END_OF_FILE:
            self.display_message("end of file...")
            pass
        elif record_type == intel_hex_properties.RECORD_TYPE_START_SEGMENT_ADDRESS:
            self.display_message("program execution start address: " + str(line_data))
        elif record_type == intel_hex_properties.RECORD_TYPE_EXTENDED_SEGMENT_ADDRESS:
            # print("data address (extended): " + str(line_data))
            self.base_address = 16 * (line_data[0]*256 + line_data[1])
                # "This is multiplied by 16 and added to each subsequent data record address to form the starting address for the data."
                # " This allows addressing up to one megabyte of address space."" 
        elif record_type == intel_hex_properties.RECORD_TYPE_START_LINEAR_ADDRESS:
            self.display_message("program linear address" + str(line_data))
        elif record_type == intel_hex_properties.RECORD_TYPE_EXTENDED_LINEAR_ADDRESS:
            self.display_message("program linear address (extended)" + str(line_data))
        elif record_type == intel_hex_properties.RECORD_TYPE_DATA:
            # print("data address: " + hex(self.base_address + address_16) + " (" + str(address_16) + ")")
            failed_write_addresses = self.put_data_in_memory_map(address_16, line_data)
            if failed_write_addresses:
                min_fail_address = min(failed_write_addresses)
                max_fail_address = max(failed_write_addresses)
                if min_fail_address < self.write_failure_address_min or self.write_failure_address_min < 0:
                    self.write_failure_address_min = int(min_fail_address) # cast to int to force copy (not pointer)
                elif max_fail_address > self.write_failure_address_max:
                    self.write_failure_address_max = int(max_fail_address) # cast to int to force copy (not pointer)


    # read_line: basic routine to pull one 'line' out of a file and return it (as a string)
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


    # put_data_in_memory_map
    # - Puts a series of data into the virtual memory space
    # -- returns a list of failed write addresses (empty list if none failed) 
    def put_data_in_memory_map(self, start_address_u16, data_list):
        # print("put " + hex(start_address_u16) + " " + str(data_list))
        # note: incoming start_address is expected to not be adjusted to RECORD_TYPE_EXTENDED_SEGMENT_ADDRESS yet.
        adjusted_start_address_u16 = start_address_u16 + self.base_address
        write_failure_addresses = []
        for this_data_index in range(len(data_list)):
            # - Add data point to memory map
            write_address = adjusted_start_address_u16 + this_data_index
            this_data_byte = data_list[this_data_index]
            if self.memory_map_out:
                error_code = self.memory_map_out.write_to_rom(write_address, int(this_data_byte)) # Force a copy by casting to int
                if error_code:
                    write_failure_addresses.append(write_address)
        return write_failure_addresses

    # write_errors_detected: returns True if any memory contents read from the hex file could not be placed in the virtual memory map
    def write_errors_detected(self):
        if self.write_failure_address_min != self.START_VALUE_WRITE_FAIL_ADDRESS_MIN:
            return True
        elif self.write_failure_address_max != self.START_VALUE_WRITE_FAIL_ADDRESS_MAX:
            return True
        else:
            return False


    # ======= Callback Assignments =START=
    # init_callbacks: setup local functions to allow for response to user interaction with graphical objects
    # def init_callbacks(self):
    #     pass

    # set_serial_monitor_callback: allows another class to assign this class a function where it can display status messages 
    def set_serial_monitor_callback(self, callback):
        self.serial_monitor_cb = callback

    # display_message: displays status messages if a callback is set up.
    def display_message(self, message, rx=False, add_timestamp=False):
        if self.serial_monitor_cb:
            self.serial_monitor_cb(message, rx, add_timestamp)
    # ======= Callback Assignments ==END==

# HexFileOutClass: Class containing routines for writing data to a hex file, 
# - and placing memory contents into a virtual memory map
class HexFileOutClass():
    def __init__(self, parent=None):
        self.MAX_BYTES_PER_LINE = 0x10
        self.LINE_FILE_HEADER = ":0400000300000000F9\n" # TODO: REVIEW
        self.LINE_FILE_TAIL = ":00000001FF\n"
        self.CHARACTER_LINE_START = ":"
        pass

    def write_data_to_file(self, file_path, memory_map, start_address, end_address):
        pass

    def write_data_pages_to_file(self, file_path, memory_map, start_page, end_page):
        all_data = memory_map.get_data_from_page_range(start_page, end_page)
        if not all_data:
            # print("no data")
            return 2 # Memory object didn't return data
        start_offset_address = memory_map.get_offset_address_from_page_id(start_page)
        current_offset_address = int(start_offset_address)
        end_offset_address = memory_map.get_offset_address_from_page_id(end_page+1) # Exclusive, this value is not included

        # - open the file
        self.file_path = file_path
        file_target = self.open_file_for_save()
        if not file_target:
            # print("no file target")
            return 1 # File didn't open return error code

        # - write header line to file
        error_code = self.write_line_to_file(file_target, self.LINE_FILE_HEADER)
        if error_code:
            pass
            # print("couldn't write header")
        # - write data lines to file
        while current_offset_address < end_offset_address:
            this_line_str = ""
            this_line_list = []
            
            # -- add start character
            this_line_str += self.CHARACTER_LINE_START
            # -- add line data length
            bytes_left = end_offset_address - current_offset_address
            if bytes_left >= self.MAX_BYTES_PER_LINE:
                packet_len = self.MAX_BYTES_PER_LINE
            else:
                packet_len = bytes_left
            this_line_str += "{:02X}".format(packet_len)
            this_line_list.append(packet_len)
            # -- add line start address
            this_line_str += "{:04X}".format(current_offset_address)
            this_line_list.append(current_offset_address >> 8 & 0xFF)
            this_line_list.append(current_offset_address & 0xFF)
            # -- add record type
            this_line_str += "{:02X}".format(intel_hex_properties.RECORD_TYPE_DATA)
            this_line_list.append(intel_hex_properties.RECORD_TYPE_DATA)
            # -- add line data
            data_packet = all_data[(current_offset_address-start_offset_address):(current_offset_address-start_offset_address + packet_len)]
            for this_index in range(len(data_packet)):
                this_line_str += "{:02X}".format(data_packet[this_index])
                this_line_list.append(data_packet[this_index])
            # -- add line checksum
            line_checksum = (256 - (sum(this_line_list) & 0xFF)) & 0xFF
            this_line_str += "{:02X}".format(line_checksum)
            this_line_list.append(line_checksum)
            # -- actually write the line to the file
            this_line_str += '\n'
            error_code = self.write_line_to_file(file_target, this_line_str)

            # - increment address in prep for the next line
            current_offset_address += packet_len
        # if current_offset_address != end_offset_address:
        #     print("WARNING: current_offset_address should match end_offset_address after data write")


        # - write tail line to file
        error_code = self.write_line_to_file(file_target, self.LINE_FILE_TAIL)
        if error_code:
            pass
            # print("couldn't write tail")

        self.close_file(file_target)
        return 0 # All things worked properly, return 0, for no-errors

    # ======= File Operations =START=
    # close_file: closes file target objects for use by other applications
    def close_file(self, file_target):
        try:
            file_target.close()
        except IOError:
            pass
            # print("could not close settings file.")

    # open_file_for_save: basic routine to 'safely' open a file for reading 
    def open_file_for_save(self):
        try:
            target = open(self.file_path, 'w')
            return target
        except IOError:
            # print("could not read from file " + str(self.file_path))
            return False

    def write_line_to_file(self, write_file_target, file_data):
        # Exit if there is nothing to write
        if not file_data:
            return 1
        #
        if not write_file_target:
            return 2
        #
        try:
            write_file_target.write(str(file_data))
        except IOError:
            return 3

        return 0 # no errors
    # ======= File Operations ==END==

    # ======= Callback Assignments =START=
    # def init_callbacks(self):
    #     pass

    def set_serial_monitor_callback(self, callback):
        self.serial_monitor_cb = callback

    def display_message(self, message, rx=False, add_timestamp=False):
        if self.serial_monitor_cb:
            self.serial_monitor_cb(message, rx, add_timestamp)
    # ======= Callback Assignments ==END==

# Properties Class Instances
intel_hex_properties = IntelHexFileProperties()



# Application Execution Start (if this is the main file, typically it will not be)                                                                                                                                                                                                                                                                                                                                                           
if __name__ == '__main__':
    print("hex_files.py is main application. For Testing Purposes Only!")
    # file_path = "test_hex.hex"
    # print("start import")
    # print(time.clock())
    # hex_file_in.import_log_file(file_path)
    # print(time.clock())
