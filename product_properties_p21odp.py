# product_properties_p21odp.py
from memory_map_stm32_64kb import MemoryMap_STM32_64kB
from hex_files import HexFileInClass, intel_hex_properties

# Product_P21Odp_MemoryMap Class: Stores Linker file properties of the P21Odp product
class Product_P21Odp_MemoryMap():
    def __init__(self, hex_file_in = None, parent=None):
        self.assign_hex_file_in(hex_file_in)

        # Processor Quantities
        self.PROCESSOR_ROM_SIZE = 0x10000  

        # - Binary File
        # -- ROM always starts at address 0x0000'0000
        # -- RAM always starts at address 0x0000'0000    
        self.BOOTLOADER_START_ADDRESS_BINFILE = 0x0000
        self.BOOTLOADER_END_ADDRESS_BINFILE = 0x1800 # Exclusive (not included in calc)
        # BOOTLOADER CHECKSUM: assummd to be at END_ADDRESS-4 (TODO: REVIEW)
        self.CHECKSUM_CALC_START_ADDRESS_BINFILE = 0x1800
        # self.CHECKSUM_CALC_END_ADDRESS = 0x97FC # Exclusive (not included in calc)
        self.CHECKSUM_CALC_END_ADDRESS_BINFILE = 0x7FFC # Exclusive (not included in calc)

        # - Hexidecimal File
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

    def assign_hex_file_in(self, hex_file_in):
        self.hex_file_in = hex_file_in


# Virtual Memory Instances
drive_fw_memory_map_file = MemoryMap_STM32_64kB() # for holding a firmware file to flash to a device
hex_file_in = HexFileInClass(memory_map_out=drive_fw_memory_map_file)
product_p21odp = Product_P21Odp_MemoryMap(hex_file_in=hex_file_in)
