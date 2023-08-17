# memory_map_stm32_64kb.py
from type_conversions import type_converter

# MemoryMap_STM32_64kB Class:  Simulates a Processor
# - holds a memory storage location for each rom byte
# - allows data to be placed at those storage locations
# - keeps track of which pages have not had data added to them since last init
# - can calculate whether or not a page is empty.
class MemoryMap_STM32_64kB():
    def __init__(self, use_8bit_chunks_on_settings=False, parent=None):
        # Processor Quantities
        self.use_8bit_chunks_on_settings = use_8bit_chunks_on_settings
        self.PROCESSOR_ROM_SIZE = 0x10000
        self.ROM_PAGE_SIZE = 0x800
        self.ROM_PAGES = int(self.PROCESSOR_ROM_SIZE/self.ROM_PAGE_SIZE) # python3 compat: Cast to int because defaults to float
        # Processor Properties
        self.BASE_ROM_START_ADDRESS_DATASHEET = 0x08000000 # hex files start at address 0, but ST documentation records this address as 0x08000000
        self.BASE_ROM_END_ADDRESS_DATASHEET = self.BASE_ROM_START_ADDRESS_DATASHEET + self.PROCESSOR_ROM_SIZE  # hex files start at address 0, but ST documentation records this address as 0x08000000
        self.BASE_ROM_ADDRESS = 0x00000000
        self.ROM_END_ADDRESS = self.BASE_ROM_ADDRESS + self.PROCESSOR_ROM_SIZE
        self.BASE_RAM_ADDRESS = 0x20000000
        # ROM Checksum Parameters
        self.ROM_CRC32_INIT_VALUE = 0xFFFFFFFF
        self.ROM_CRC32_NIBBLE_TABLE = [
            # - This is from https://www.iar.com/support/tech-notes/general/checksum-generation/
            0x00000000, 0x04C11DB7, 0x09823B6E, 0x0D4326D9, 0x130476DC, 0x17C56B6B, 0x1A864DB2, 0x1E475005,
            0x2608EDB8, 0x22C9F00F, 0x2F8AD6D6, 0x2B4BCB61, 0x350C9B64, 0x31CD86D3, 0x3C8EA00A, 0x384FBDBD,
        ]
        # self.SIZE_U8_IN_BYTES = 1
        # self.SIZE_U16_IN_BYTES = 2
        # self.SIZE_U32_IN_BYTES = 4
        # Error Codes
        self.SUCCESS_CODE = 0
        self.ERROR_CODE_WRITE_OUT_OF_RANGE = 1
        self.ERROR_CODE_WRITE_VALUE = 2

        self.ROM_PAGE_ID_USER_SETTINGS = 27
        self.ROM_PAGE_ID_DEFAULT_SETTINGS = 26 

        self.init_memory_map()

        self.drive_app_edit_select = 1 # ENABLE_APP_CONFIG_CRC_PATCH -> TODO: Magic Number drive is 1, app is 0, variable name is unclear to function though.

    def init_memory_map(self):
        self.modified_pages = [False]*self.ROM_PAGES
        self.empty_page = [0xFF]*self.ROM_PAGE_SIZE
        self.memory_map = [0xFF]*self.PROCESSOR_ROM_SIZE

    def init_crc32_calculation_parameters(self):
        self.rom_crc32_value = self.ROM_CRC32_INIT_VALUE
        pass


    # write_to_rom: updates memory contents
    # receives: rom_address_offset (this routine wants the offset address like 0x0000)
    # - Writes one byte to one virtual memory address
    # -- Returns 0, if write was successful
    # -- Returns 1, if write failed (out of range)
    # -- Returns 2, if write failed (invalid value)
    def write_to_rom(self, rom_address_offset, value_u8):
        # if rom_address not in range(self.BASE_ROM_ADDRESS, self.ROM_END_ADDRESS): # This takes to 1-2ms to generate the large range
        if rom_address_offset < self.BASE_ROM_ADDRESS or rom_address_offset >= self.ROM_END_ADDRESS:
            # Handle bad addresses
            # print("address out of range, skipping! " + hex(rom_address))
            return self.ERROR_CODE_WRITE_OUT_OF_RANGE
        elif value_u8 > 0xFF or value_u8 < 0:
            # Handle data overflow
            # print("invalid value, skipping! " + str(value_u8))
            return self.ERROR_CODE_WRITE_VALUE
        else:
            # Write to Memory Contents
            adjusted_address = rom_address_offset - self.BASE_ROM_ADDRESS
            self.memory_map[adjusted_address] = value_u8
            # - update flags
            self.update_modified_pages_for_address(rom_address_offset)
            return self.SUCCESS_CODE # Return empty list to indicate no failures

    # # write_to_rom: updates memory contents
    # # receives: rom_address_offset (this routine wants the offset address like 0x0000)
    # # - Writes one byte to one virtual memory address
    # # -- Returns 0, if write was successful
    # # -- Returns 1, if write failed (out of range)
    # # -- Returns 2, if write failed (invalid value)
    # def write_to_rom_st_addressing(self, rom_address, value_u8):
    #     rom_address_offset = rom_address - self.BASE_ROM_ADDRESS


    # bulk_write_to_rom_st_addressing: updates memory contents using a start address and a list of data bytes
    # - receives: rom_start_address (this routine wants the processor address like 0x08000000)
    # - returns: status of write
    # -- Returns 0, if write was successful
    # -- Returns 1, if write failed (out of range)
    # -- Returns 2, if write failed (invalid value)
    def bulk_write_to_rom_st_addressing(self, rom_start_address, data_list):
        status_code = self.SUCCESS_CODE # set default value for code that will be returned
        rom_end_address = rom_start_address + len(data_list)
        if rom_start_address < self.BASE_ROM_START_ADDRESS_DATASHEET:
            return self.ERROR_CODE_WRITE_OUT_OF_RANGE
            # print("warning: attempted memory map write out of bounds (low), write cancelled.")
            # return
        elif rom_start_address >= self.BASE_ROM_END_ADDRESS_DATASHEET:
            return self.ERROR_CODE_WRITE_OUT_OF_RANGE
            # print("warning: attempted memory map write out of bounds (high), write cancelled.")
            # return

        if rom_end_address > self.BASE_ROM_END_ADDRESS_DATASHEET:
            write_length = self.BASE_ROM_END_ADDRESS_DATASHEET - rom_start_address
            # flag as an error, but do not return yet to allow writing of data to the end of ROM
            status_code = self.ERROR_CODE_WRITE_OUT_OF_RANGE
            # return self.ERROR_CODE_WRITE_OUT_OF_RANGE
            # print("warning: attempted to write out of bounds, input data truncated.")
        else:
            write_length = len(data_list)

        # if app_config.ENABLE_APP_CONFIG_CRC_PATCH: # This seems to NOT apply to this software, all configs work properly without it.
        #     if self.drive_app_edit_select: # Drive edit option selected
        #         adjusted_start_address = rom_start_address - self.BASE_ROM_START_ADDRESS_DATASHEET
        #     else: # App edit option selected
        #         adjusted_start_address = rom_start_address #- self.BASE_ROM_START_ADDRESS_DATASHEET
        # else:
        adjusted_start_address = rom_start_address - self.BASE_ROM_START_ADDRESS_DATASHEET


        # adjusted_start_address = rom_start_address - self.BASE_ROM_START_ADDRESS_DATASHEET
        self.memory_map[adjusted_start_address:adjusted_start_address+write_length] = data_list # REVIEW: Need to cast?
        for this_address_offset in range(adjusted_start_address, adjusted_start_address+write_length):
            self.update_modified_pages_for_address(this_address_offset)
        return status_code

    # bulk_read_from_rom_st_addressing: updates memory contents using a start address and a list of data bytes
    # - receives: rom_start_address (this routine wants the processor address like 0x08000000)
    # - receives: rom_end_address (this routine wants the processor address like 0x08000000) (exclusive, this address' contents are not returned)
    # - returns: list of memory contents
    # -- Returns empty list, if rom_start_address or rom_end_address is invalid
    def bulk_read_from_rom_st_addressing(self, rom_start_address, rom_end_address):
        if rom_start_address < self.BASE_ROM_START_ADDRESS_DATASHEET or rom_start_address >= self.BASE_ROM_END_ADDRESS_DATASHEET:
            return []
        elif rom_end_address < self.BASE_ROM_START_ADDRESS_DATASHEET or rom_start_address >= self.BASE_ROM_END_ADDRESS_DATASHEET: 
            return []
        adjusted_start_address = rom_start_address - self.BASE_ROM_START_ADDRESS_DATASHEET
        adjusted_end_address = rom_end_address - self.BASE_ROM_START_ADDRESS_DATASHEET
        memory_contents = self.memory_map[adjusted_start_address:adjusted_end_address]
        return memory_contents


    def copy_from_page_to_page(self, from_page_id, to_page_id):
        print("copy! TODO: Making overwriting default settings page an option!")
        from_page_start_address = from_page_id*self.ROM_PAGE_SIZE
        from_page_end_address = from_page_start_address + self.ROM_PAGE_SIZE # Exclusive, this address is not included in calculation
        to_page_start_address = to_page_id*self.ROM_PAGE_SIZE
        to_page_end_address = to_page_start_address + self.ROM_PAGE_SIZE # Exclusive, this address is not included in calculation

        from_address = int(from_page_start_address)
        to_address = int(to_page_start_address)
        while(from_address < from_page_end_address):
            value_u8 = int(self.memory_map[from_address])
            self.write_to_rom(to_address, value_u8)
            from_address += 1
            to_address += 1

    # Page Status
    # - page_is_empty: returns true if all bits in page are of 'erased' value
    def page_is_empty(self, page_id):
        page_start_address = page_id*self.ROM_PAGE_SIZE
        page_end_address = page_start_address + self.ROM_PAGE_SIZE # Exclusive, this address is not included in calculation
        if self.memory_map[page_start_address:page_end_address] == self.empty_page:
            # print("page is empty: " + str(page_id))
            return True
        else:
            # print(len(self.memory_map[page_start_address:page_end_address]))
            # print(len(self.empty_page))
            return False

    # - get_empty_pages: scans all flash pages and returns a list of integer ids of the flash pages that are 'empty'
    def get_empty_pages(self):
        empty_pages = []
        for this_page_id in range(self.ROM_PAGES):
            if self.page_is_empty(this_page_id):
                #empty_pages[this_page_id] = True
                empty_pages.append(this_page_id)
        # print("empty: " + str(empty_pages))
        return empty_pages

    # - page_is_modified: returns true if any incoming data has been written to this area (ie. write_to_rom, bulk_write_to_rom_st_addressing)
    def page_is_modified(self, page_id):
        if self.modified_pages[page_id]:
            return True
        else:
            return False

    # - get_modified_pages: scans all flash pages and returns a list of integer ids of the flash pages that have been 'modified'
    def get_modified_pages(self):
        # print("modified: " + str(self.modified_pages))
        return self.modified_pages

    # - update_modified_pages_for_address: updates the 'modified' flag for a given address. 
    # -- This should be called when virtual rom is written to (like write_to_rom and bulk_write_to_rom_st_addressing do)
    def update_modified_pages_for_address(self, address):
        adjusted_address = address - self.BASE_ROM_ADDRESS
        page_id = int(adjusted_address/self.ROM_PAGE_SIZE) # python3 compatibility: cast to int (defaults to float) 
        if page_id >= len(self.modified_pages):
            # print("page id out of range!")
            return
        else:
            self.modified_pages[page_id] = True

    # - get_u32_value_at_address: read a whole "word" from memory, compose it in the proper manner for crc calculation
    def get_u8_value_at_address(self, current_address):
        # Get Data Bytes and Place in a List
        # - Example:
        # -- __root const uint32_t MeerkatConfig_ClockCheck_IdealLsiCounts_u32 @ (THIS_BLOCK_ADDR) = 3788;
        # --- hex_value of 3788 = 0x00000ecc
        # -- hex file value: CC0E0000
        # -- list value: [0xcc, 0x0e, 0x00, 0x00]
        data_bytes = list(self.memory_map[current_address:current_address+type_converter.SIZE_U8_IN_BYTES])
        # for this_byte_index in range(type_converter.SIZE_U32_IN_BYTES):
        #     data_bytes.append(self.memory_map[current_address + this_byte_index])
        # Convert Data Bytes to a single u32 integer
        data_value_u32 = 0
        for this_byte_index in range(type_converter.SIZE_U8_IN_BYTES):
            data_value_u32 = data_value_u32 + (data_bytes[this_byte_index] << 8*this_byte_index)
        # if data_bytes == [0xcc,0x0e,0x00,0x00]:
        # print(hex(current_address) + ": " + str(data_bytes) + " -> " + hex(data_value_u32))
        # print(hex(current_address)+": " + hex(data_value_u32))
        return data_value_u32

    # - get_u16_value_at_address: read a half "word" from memory, compose it in the proper manner for crc calculation
    def get_u16_value_at_address(self, current_address):
        # Get Data Bytes and Place in a List
        # - Example:
        # -- __root const uint32_t MeerkatConfig_ClockCheck_IdealLsiCounts_u32 @ (THIS_BLOCK_ADDR) = 3788;
        # --- hex_value of 3788 = 0x00000ecc
        # -- hex file value: CC0E0000
        # -- list value: [0xcc, 0x0e, 0x00, 0x00]
        data_bytes = list(self.memory_map[current_address:current_address+type_converter.SIZE_U16_IN_BYTES])
        # for this_byte_index in range(self.SIZE_U32_IN_BYTES):
        #     data_bytes.append(self.memory_map[current_address + this_byte_index])
        # Convert Data Bytes to a single u32 integer
        data_value_u32 = 0
        for this_byte_index in range(type_converter.SIZE_U16_IN_BYTES):
            data_value_u32 = data_value_u32 + (data_bytes[this_byte_index] << 8*this_byte_index)
        # if data_bytes == [0xcc,0x0e,0x00,0x00]:
        # print(hex(current_address) + ": " + str(data_bytes) + " -> " + hex(data_value_u32))
        return data_value_u32

    # - get_u16_value_at_address: read a half "word" from memory, compose it in the proper manner for crc calculation
    def get_i16_value_at_address(self, current_address):
        # Get Data Bytes and Place in a List
        # - Example:
        # -- __root const uint32_t MeerkatConfig_ClockCheck_IdealLsiCounts_u32 @ (THIS_BLOCK_ADDR) = 3788;
        # --- hex_value of 3788 = 0x00000ecc
        # -- hex file value: CC0E0000
        # -- list value: [0xcc, 0x0e, 0x00, 0x00]
        data_bytes = list(self.memory_map[current_address:current_address+type_converter.SIZE_U16_IN_BYTES])
        # for this_byte_index in range(type_converter.SIZE_U32_IN_BYTES):
        #     data_bytes.append(self.memory_map[current_address + this_byte_index])
        # Convert Data Bytes to a single u32 integer
        data_value_u32 = 0
        for this_byte_index in range(type_converter.SIZE_U16_IN_BYTES):
            data_value_u32 = data_value_u32 + (data_bytes[this_byte_index] << 8*this_byte_index)
        # if data_bytes == [0xcc,0x0e,0x00,0x00]:
        # print(hex(current_address) + ": " + str(data_bytes) + " -> " + hex(data_value_u32))
        # Now convert into a signed value

        type_converter.get_i16_value_from_u16_value(data_value_u32)

        return data_value_u32

    # - get_u32_value_at_address: read a whole "word" from memory, compose it in the proper manner for crc calculation
    def get_u32_value_at_address(self, current_address):
        # Get Data Bytes and Place in a List
        # - Example:
        # -- __root const uint32_t MeerkatConfig_ClockCheck_IdealLsiCounts_u32 @ (THIS_BLOCK_ADDR) = 3788;
        # --- hex_value of 3788 = 0x00000ecc
        # -- hex file value: CC0E0000
        # -- list value: [0xcc, 0x0e, 0x00, 0x00]
        data_bytes = list(self.memory_map[current_address:current_address+type_converter.SIZE_U32_IN_BYTES])
        # for this_byte_index in range(type_converter.SIZE_U32_IN_BYTES):
        #     data_bytes.append(self.memory_map[current_address + this_byte_index])
        # Convert Data Bytes to a single u32 integer
        data_value_u32 = 0
        for this_byte_index in range(type_converter.SIZE_U32_IN_BYTES):
            data_value_u32 = data_value_u32 + (data_bytes[this_byte_index] << 8*this_byte_index)
        # if data_bytes == [0xcc,0x0e,0x00,0x00]:
        # print(hex(current_address) + ": " + str(data_bytes) + " -> " + hex(data_value_u32))
        return data_value_u32

    # - get_u32_value_at_address: read a whole "word" from memory, compose it in the proper manner for crc calculation
    def get_u32_value_at_address_inverted(self, current_address):
        # Get Data Bytes and Place in a List
        # - Example:
        # -- __root const uint32_t MeerkatConfig_ClockCheck_IdealLsiCounts_u32 @ (THIS_BLOCK_ADDR) = 3788;
        # --- hex_value of 3788 = 0x00000ecc
        # -- hex file value: CC0E0000
        # -- list value: [0xcc, 0x0e, 0x00, 0x00]
        data_bytes = list(self.memory_map[current_address:current_address+type_converter.SIZE_U32_IN_BYTES])
        data_bytes.reverse()
        # for this_byte_index in range(type_converter.SIZE_U32_IN_BYTES):
        #     data_bytes.append(self.memory_map[current_address + this_byte_index])
        # Convert Data Bytes to a single u32 integer
        data_value_u32 = 0
        for this_byte_index in range(type_converter.SIZE_U32_IN_BYTES):
            data_value_u32 = data_value_u32 + (data_bytes[this_byte_index] << 8*this_byte_index)
        # if data_bytes == [0xcc,0x0e,0x00,0x00]:
        # print(hex(current_address) + ": " + str(data_bytes) + " -> " + hex(data_value_u32))
        return data_value_u32

    # - get_u32_value_at_address: read a whole "word" from memory, compose it in the proper manner for crc calculation
    def get_i32_value_at_address(self, current_address):
        # Get Data Bytes and Place in a List
        # - Example:
        # -- __root const uint32_t MeerkatConfig_ClockCheck_IdealLsiCounts_u32 @ (THIS_BLOCK_ADDR) = 3788;
        # --- hex_value of 3788 = 0x00000ecc
        # -- hex file value: CC0E0000
        # -- list value: [0xcc, 0x0e, 0x00, 0x00]
        data_bytes = list(self.memory_map[current_address:current_address+type_converter.SIZE_U32_IN_BYTES])
        # for this_byte_index in range(type_converter.SIZE_U32_IN_BYTES):
        #     data_bytes.append(self.memory_map[current_address + this_byte_index])
        # Convert Data Bytes to a single u32 integer
        data_value_u32 = 0
        for this_byte_index in range(type_converter.SIZE_U32_IN_BYTES):
            data_value_u32 = data_value_u32 + (data_bytes[this_byte_index] << 8*this_byte_index)
        # if data_bytes == [0xcc,0x0e,0x00,0x00]:
        # print(hex(current_address) + ": " + str(data_bytes) + " -> " + hex(data_value_u32))
        type_converter.get_i32_value_from_u32_value(data_value_u32)
        return data_value_u32

    # update_crc32_from_data_at_address: update firmware crc calculation using a single "word" of ROM
    def update_crc32_from_data_at_address(self, current_address):
        # Get all data for the current u32
        data_value_u32 = self.get_u32_value_at_address(current_address)
        # XOR the current u32 to the existing checksum
        self.rom_crc32_value = (self.rom_crc32_value ^ data_value_u32) & 0xFFFFFFFF
        # Perform the required bitflip operation on each four bits for the u32 based on the polynomial
        for this_byte_index in range(type_converter.SIZE_U32_IN_BYTES * 2): # *2 because nibble table only handles Half bytes
            self.rom_crc32_value = ((self.rom_crc32_value << 4) ^ self.ROM_CRC32_NIBBLE_TABLE[self.rom_crc32_value >> 28 & 0x0F]) & 0xFFFFFFFF
        # print("post update: " + hex(current_address) + ": " + hex(data_value_u32) + " -> " + hex(self.rom_crc32_value) )
        
    # update_crc32_from_data_at_address: update firmware crc calculation using a single "word" of ROM
    def update_crc32_from_data_at_address_8bit_chunks(self, current_address):
        data_value_u8 = self.get_u8_value_at_address(current_address)
        # high nibble
        high_index = ((self.rom_crc32_value >> 28) ^ (data_value_u8 >> 4)) & 0x0F
        sum_high_nibble = self.rom_crc32_value << 4
        self.rom_crc32_value = self.ROM_CRC32_NIBBLE_TABLE[high_index] ^ sum_high_nibble
        # low nibble
        low_index = ((self.rom_crc32_value >> 28) ^ (data_value_u8 & 0x0F)) & 0x0F
        sum_low_nibble = self.rom_crc32_value << 4
        self.rom_crc32_value = self.ROM_CRC32_NIBBLE_TABLE[low_index] ^ sum_low_nibble


        # # Get all data for the current u32
        # data_value_u32 = self.get_u32_value_at_address_inverted(current_address)
        # # XOR the current u32 to the existing checksum
        # self.rom_crc32_value = (self.rom_crc32_value ^ data_value_u32) & 0xFFFFFFFF
        # # Perform the required bitflip operation on each four bits for the u32 based on the polynomial
        # for this_byte_index in range(type_converter.SIZE_U32_IN_BYTES * 2): # *2 because nibble table only handles Half bytes
        #     self.rom_crc32_value = ((self.rom_crc32_value << 4) ^ self.ROM_CRC32_NIBBLE_TABLE[self.rom_crc32_value >> 28 & 0x0F]) & 0xFFFFFFFF


    # get_crc32_for_address_range
    # - Calculate a CRC Value for a specified address range.
    # -- End address is 'exclusive', it will not be included if end_address&0x03=0
    # - This algorithm looks at data in four byte chunks, so end_address-start_address should be a multiple of '4'
    def get_crc32_for_address_range(self, start_address, end_address):
        # print("\naddress range: " + hex(start_address) + "-" + hex(end_address))
        # Detect invalid address ranges to avoid program errors
        if start_address < self.BASE_ROM_ADDRESS:
            # print("rom crc32 calculation: invalid start address")
            return 0xFFFFFFFF # Return default checksum value in error case
        elif end_address > self.ROM_END_ADDRESS: # we allow 'ROM_END_ADDRESS', though it won't be included in calculation
            # print("rom crc32 calculation: invalid end address")
            return 0xFFFFFFFF # Return default checksum value in error case
        # Calculate the Checksum
        current_address = int(start_address) # cast to int to force copy and not pointer
        self.init_crc32_calculation_parameters()
        while current_address < end_address: # We don't allow use of 'ROM_END_ADDRESS' in calculation (not <=, but <)
            if self.use_8bit_chunks_on_settings:
                self.update_crc32_from_data_at_address_8bit_chunks(current_address)
                current_address += 1 # Update the address pointer for the next iteration
            else:
                self.update_crc32_from_data_at_address(current_address)
                current_address += 4 # Update the address pointer for the next iteration
        return int(self.rom_crc32_value & 0xFFFFFFFF) # int casting is done to return to u32 (calculation innately pushes declaration to u64)


    # get_crc_u32_from_page_list
    # - Calculate a CRC Value for a list of pages.
    # -- if 'ignore_last_four_bytes' is enabled, the algorithm will presume the CRC is placed in the last four bytes of the page.
    # --- and the last four bytes will not be included in the calculation.
    def get_crc_u32_from_page_list(self, page_id_list, ignore_last_four_bytes=False):
        start_address = min(page_id_list)*self.ROM_PAGE_SIZE # inclusive
        end_address = (max(page_id_list)+1)*self.ROM_PAGE_SIZE # exclusive (does not include last byte)
        if ignore_last_four_bytes:
            end_address = end_address - 4

        print("start: " + str(hex(start_address)))
        print("end: " + str(hex(end_address)))
        crc32_value = self.get_crc32_for_address_range(start_address, end_address)
        return crc32_value


    def get_data_from_page_range(self, start_page, end_page):
        start_address = start_page*self.ROM_PAGE_SIZE # inclusive
        end_address = (end_page+1)*self.ROM_PAGE_SIZE # exclusive (does not include last byte)

        start_address_st_addressing = start_address + self.BASE_ROM_START_ADDRESS_DATASHEET
        end_address_st_addressing = end_address + self.BASE_ROM_START_ADDRESS_DATASHEET
        memory_contents = self.bulk_read_from_rom_st_addressing(start_address_st_addressing, end_address_st_addressing)
        return memory_contents

    def get_offset_address_from_page_id(self, page_id):
        offset_address = page_id*self.ROM_PAGE_SIZE
        return offset_address

    def get_st_address_from_page_id(self, page_id):
        st_address = start_page*self.ROM_PAGE_SIZE + self.BASE_ROM_START_ADDRESS_DATASHEET
        return st_address
