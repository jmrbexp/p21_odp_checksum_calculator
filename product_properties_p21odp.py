# product_properties_p21odp.py
from memory_map_stm32_64kb import MemoryMap_STM32_64kB
from hex_files import HexFileInClass, intel_hex_properties
from type_conversions import type_converter

# Product_P21Odp_MemoryMap Class: Stores Linker file properties of the P21Odp product
class Product_P21Odp_MemoryMap():
    def __init__(self, hex_file_in = None, parent=None):
        # Store Pointer to Hex File In Object
        self.assign_hex_file_in(hex_file_in)
        # CONSTANTS
        self.PROCESSOR_STRING = "STM32F301"
        # - Processor Quantities
        self.PROCESSOR_ROM_SIZE = 0x10000  
        self.PROCESSOR_FLASH_PAGE_SIZE = 0x800
        # - Processor Pages (Linking)
        self.FLASH_PAGE_BOOTLOADER_START = 0 
        self.FLASH_PAGE_BOOTLOADER_END = 3 # Exclusive 
        self.FLASH_PAGE_FIRMWARE_START = 3 # 
        self.FLASH_PAGE_FIRMWARE_END = 19 # Exclusive 

        # - Binary File (*.bin)
        # -- ROM always starts at address 0x0000'0000
        # -- RAM always starts at address 0x0000'0000    
        self.BOOTLOADER_START_ADDRESS_BINFILE = 0x0000
        self.BOOTLOADER_CRC_ADDRESS_BINFILE = 0x17FC # Exclusive (not included in calc)
        self.BOOTLOADER_END_ADDRESS_BINFILE = 0x1800 # Exclusive (not included in calc)
        # BOOTLOADER CHECKSUM: assummd to be at END_ADDRESS-4 (TODO: REVIEW)
        self.CHECKSUM_CALC_START_ADDRESS_BINFILE = 0x1800
        self.CHECKSUM_CALC_END_ADDRESS_BINFILE = 0x97FC # Exclusive (not included in calc)
        # self.CHECKSUM_CALC_END_ADDRESS_BINFILE = 0x7FFC # Exclusive (not included in calc)
        # - P21 ODP Specific: Default Binary file is expected to be offset by 0x1800 (first byte is to be placed on mcu at address 0x1800)
        self.DEFAULT_MEMORY_OFFSET_FIRMWARE_BINFILE = 0x1800

        # - Hexidecimal File (*.hex/ *.hxf)
        # -- STM32: ROM always starts at address 0x08000000
        self.STM32_ROM_START = 0x08000000
        # -- STM32: RAM always starts at address 0x20000000
        self.STM32_RAM_START = 0x20000000
        #
        self.BOOTLOADER_START_ADDRESS_HEXFILE = self.BOOTLOADER_START_ADDRESS_BINFILE + self.STM32_ROM_START
        self.BOOTLOADER_END_ADDRESS_HEXFILE = self.BOOTLOADER_START_ADDRESS_BINFILE + self.STM32_ROM_START # Exclusive (not included in calc)
        # BOOTLOADER CHECKSUM: assummd to be at END_ADDRESS-4 (TODO: REVIEW)
        self.CHECKSUM_CALC_START_ADDRESS_HEXFILE = self.CHECKSUM_CALC_START_ADDRESS_BINFILE + self.STM32_ROM_START
        self.CHECKSUM_CALC_END_ADDRESS_HEXFILE = self.CHECKSUM_CALC_END_ADDRESS_BINFILE + self.STM32_ROM_START # Exclusive (not included in calc)

        # Checksum Information
        self.CHECKSUM_LENGTH_BYTES = 4
        self.CHECKSUM_CHUNK_SIZE_BYTES = 4
        self.calculated_checksum_list = [0]*self.CHECKSUM_LENGTH_BYTES

        self.init_system()

    # init_system: Initialize all variables and structures used by this class
    def init_system(self):
        # VARIABLES
        # - crc storage
        self.init_crc_storage()
        self.bootloader_crc_stored_list = [0xFF, 0xFF, 0xFF, 0xFF] 
        self.bootloader_crc_calc_list = [0xFF, 0xFF, 0xFF, 0xFF] 
        self.firmware_crc_stored_list = [0xFF, 0xFF, 0xFF, 0xFF] 
        self.firmware_crc_calc_list = [0xFF, 0xFF, 0xFF, 0xFF] 



    def assign_hex_file_in(self, hex_file_in):
        self.hex_file_in = hex_file_in

    # ======= API Functions =START=
    # = API Functions are designed to be called outside of this class (typically by GUI or Serial Port Callbacks)

    # import_firmware_file: open a file from path and load it's contents in to the file_read memory object for this device
    def import_firmware_file(self, firmware_file_path):
        print("import firmware file to p21 odp emulator")
        self.hex_file_in.import_firmware_file(firmware_file_path, binary_start_address=self.DEFAULT_MEMORY_OFFSET_FIRMWARE_BINFILE)
        self.update_all_crc_data()
    # ======= API Functions ==END=


    # ======= CRC Data =START=
    def update_all_crc_data(self):
        print("updating stored bootloader crc")
        stored_bootloader_crc32_list = self.hex_file_in.memory_map_out.memory_map[self.BOOTLOADER_CRC_ADDRESS_BINFILE: self.BOOTLOADER_CRC_ADDRESS_BINFILE + self.CHECKSUM_LENGTH_BYTES]
        self.stored_bootloader_crc32_value = type_converter.get_u32_value_from_u8_list(stored_bootloader_crc32_list)
        self.stored_bootloader_crc32_value_str = type_converter.convert_u32_crc_value_to_hex_string(self.stored_bootloader_crc32_value)
        print("updating calculated bootloader crc")
        self.bootloader_crc32_value = self.hex_file_in.memory_map_out.get_crc_u32_from_page_list(list(range(self.FLASH_PAGE_BOOTLOADER_START,self.FLASH_PAGE_BOOTLOADER_END)), ignore_last_four_bytes=True)
        self.bootloader_crc32_value_str = type_converter.convert_u32_crc_value_to_hex_string(self.bootloader_crc32_value)
        print("updating stored firmware crc")
        stored_firmware_crc32_list = self.hex_file_in.memory_map_out.memory_map[self.CHECKSUM_CALC_END_ADDRESS_BINFILE: self.CHECKSUM_CALC_END_ADDRESS_BINFILE + self.CHECKSUM_LENGTH_BYTES]
        self.stored_firmware_crc32_value = type_converter.get_u32_value_from_u8_list(stored_firmware_crc32_list)
        self.stored_firmware_crc32_value_str = type_converter.convert_u32_crc_value_to_hex_string(self.stored_firmware_crc32_value)
        print("updating calculated firmware crc")
        self.firmware_crc32_value = self.hex_file_in.memory_map_out.get_crc_u32_from_page_list(list(range(self.FLASH_PAGE_FIRMWARE_START,self.FLASH_PAGE_FIRMWARE_END)), ignore_last_four_bytes=True)
        self.firmware_crc32_value_str = type_converter.convert_u32_crc_value_to_hex_string(self.firmware_crc32_value)

    def get_stored_bootloader_crc_u32(self):
        return 0

    def get_stored_bootloader_crc_u32(self):
        return 0

    def get_all_crc_data_lists(self):
        return self.bootloader_crc_stored_list, self.bootloader_crc_calc_list, self.firmware_crc_stored_list, self.firmware_crc_calc_list


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



    # ======= CRC Data ==END==


# Virtual Memory Instances
drive_fw_memory_map_file = MemoryMap_STM32_64kB() # for holding a firmware file to flash to a device
hex_file_in = HexFileInClass(memory_map_out=drive_fw_memory_map_file)
product_p21odp = Product_P21Odp_MemoryMap(hex_file_in=hex_file_in)
