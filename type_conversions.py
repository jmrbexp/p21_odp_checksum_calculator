# type_conversions.py
# - Created by J.Moon 20201013a
# - A class for converting strings into various number types 

# convert_string_to_int
# - supports binary values, hex values, and decimal values

import math
from numpy import number
import struct # For float to memory representation conversions


class TypeConversions():
    def __init__(self):    # Standard Python Function, called at the instantiation of a class
        # Initialize Variables
        self.init_system()
        self.HEXIDECIMAL_BASE_CHARACTERS = 16
        self.DECIMAL_BASE_CHARACTERS = 10
        self.BINARY_BASE_CHARACTERS = 2
        self.FLOAT_BASE_CHARACTERS = 1 # 1 is not valid when using 'int', which is fine, because 'float' can't use 'int.
        # common variable sizes
        self.SIZE_I8_IN_BYTES = 1
        self.SIZE_U8_IN_BYTES = 1
        self.SIZE_I16_IN_BYTES = 2
        self.SIZE_U16_IN_BYTES = 2
        self.SIZE_I32_IN_BYTES = 4
        self.SIZE_U32_IN_BYTES = 4
        self.SIZE_FLOAT_IN_BYTES = 4

        # common variable value limits
        self.U8_MIN = 0 # inclusive, this value IS allowed
        self.U8_MAX = 2**8 # exclusive, this value is NOT allowed
        self.U16_MIN = 0 # inclusive, this value IS allowed
        self.U16_MAX = 2**16 # exclusive, this value is NOT allowed
        self.I16_MIN = -1*2**(16-1) # inclusive, this value IS allowed
        self.I16_MAX = 2**(16-1) # exclusive, this value is NOT allowed
        self.U32_MIN = 0 # inclusive, this value IS allowed
        self.U32_MAX = 2**32 # exclusive, this value is NOT allowed
        self.I32_MIN = -1*2**(32-1) # inclusive, this value IS allowed
        self.I32_MAX = 2**(32-1) # exclusive, this value is NOT allowed


        self.ERROR_CODE_INVALID_STRING = -1
        self.ERROR_CODE_OUT_OF_RANGE = -2

    def init_system(self):
        pass

    # get_u8_as_u8_list_from_string: return an 8-bit unsigned integerr from a string value
    # - string values supported are 'hex', 'binary', and 'decimal'
    # -- hex must have x in the string. binary must have 'b' in the string. decimal is default if x or b is not included in string.
    # - returns: positive value between 0-255 if string is valid
    # -- Negative Value containing Error Code if received string cannot be converted to desired type
    def get_u8_as_u8_list_from_string(self, this_string):
        return_value = -1
        lower_case_string = this_string.lower() # lower case for non-case sensitive checking of character values

        # Determine number base
        if 'x' in lower_case_string:
            number_base = self.HEXIDECIMAL_BASE_CHARACTERS
            # add 0 character at the front if needed for the 'int' conversion
            if '0' !=  lower_case_string[0]:
                lower_case_string = '0' + lower_case_string
        elif 'b' in lower_case_string:
            number_base = self.BINARY_BASE_CHARACTERS
            # add 0 character at the front if needed for the 'int' conversion
            if '0' !=  lower_case_string[0]:
                lower_case_string = '0' + lower_case_string
        elif '.' in lower_case_string:
            number_base = self.FLOAT_BASE_CHARACTERS
            return [] # Invalid Input: Float representation not allowed for integers
        else:
            number_base = self.DECIMAL_BASE_CHARACTERS
            # do not need to add characters for 'int' conversion

        # print("number base: " + str(number_base))

        # Convert String to Integer
        try:
            return_value = int(lower_case_string, number_base)
        except ValueError:  # exit and return error code if cannot convert
            return []
            # return_value = self.ERROR_CODE_INVALID_STRING
            # return return_value

        # Ensure Value is in range of u8
        if return_value < self.U8_MIN or return_value >= self.U8_MAX:
            return []
            # return_value = self.ERROR_CODE_OUT_OF_RANGE # return error code if value is out of range for type

        return_list = [return_value]
        return return_list


    # get_u8_as_u8_list_from_string: return an 8-bit unsigned integerr from a string value
    # - string values supported are 'hex', 'binary', and 'decimal'
    # -- hex must have x in the string. binary must have 'b' in the string. decimal is default if x or b is not included in string.
    # - returns: positive value between 0-255 if string is valid
    # -- Negative Value containing Error Code if received string cannot be converted to desired type
    def get_u16_as_u8_list_from_string(self, this_string):
        return_value = -1
        lower_case_string = this_string.lower() # lower case for non-case sensitive checking of character values

        # Determine number base
        if 'x' in lower_case_string:
            number_base = self.HEXIDECIMAL_BASE_CHARACTERS
            # add 0 character at the front if needed for the 'int' conversion
            if '0' !=  lower_case_string[0]:
                lower_case_string = '0' + lower_case_string
        elif 'b' in lower_case_string:
            number_base = self.BINARY_BASE_CHARACTERS
            # add 0 character at the front if needed for the 'int' conversion
            if '0' !=  lower_case_string[0]:
                lower_case_string = '0' + lower_case_string
        elif '.' in lower_case_string:
            number_base = self.FLOAT_BASE_CHARACTERS
            return [] # Invalid Input: Float representation not allowed for integers
        else:
            number_base = self.DECIMAL_BASE_CHARACTERS
            # do not need to add characters for 'int' conversion

        # print("number base: " + str(number_base))

        # Convert String to Integer
        try:
            return_value = int(lower_case_string, number_base)
        except ValueError:  # exit and return error code if cannot convert
            # return_value = self.ERROR_CODE_INVALID_STRING
            # return return_value
            return []

        # Ensure Value is in range of u8
        if return_value < self.U16_MIN or return_value >= self.U16_MAX:
            return []
            # return_value = self.ERROR_CODE_OUT_OF_RANGE # return error code if value is out of range for type

        return_list = [return_value & 0xFF] + [return_value >> 8 & 0xFF]
        # if return value is 0x0201 we want a return of [0x01, 0x02]

        return return_list

    # get_i16_as_u8_list_from_string: return a list of 8-bit unsigned integers from a string value containing a 
    # - string values supported are 'hex', 'binary', and 'decimal'
    # -- hex must have x in the string. binary must have 'b' in the string. decimal is default if x or b is not included in string.
    # - returns: positive value between 0-255 if string is valid
    # -- Negative Value containing Error Code if received string cannot be converted to desired type
    def get_i16_as_u8_list_from_string(self, this_string):
        return_value = -1
        lower_case_string = this_string.lower() # lower case for non-case sensitive checking of character values

        # Determine number base
        if 'x' in lower_case_string:
            number_base = self.HEXIDECIMAL_BASE_CHARACTERS
            # add 0 character at the front if needed for the 'int' conversion
            if '0' !=  lower_case_string[0]:
                lower_case_string = '0' + lower_case_string
        elif 'b' in lower_case_string:
            number_base = self.BINARY_BASE_CHARACTERS
            # add 0 character at the front if needed for the 'int' conversion
            if '0' !=  lower_case_string[0]:
                lower_case_string = '0' + lower_case_string
        elif '.' in lower_case_string:
            number_base = self.FLOAT_BASE_CHARACTERS
            return [] # Invalid Input: Float representation not allowed for integers
        else:
            number_base = self.DECIMAL_BASE_CHARACTERS
            # do not need to add characters for 'int' conversion

        # print("number base: " + str(number_base))

        # Convert String to Integer
        try:
            return_value = int(lower_case_string, number_base)
        except ValueError:  # exit and return error code if cannot convert
            # return_value = self.ERROR_CODE_INVALID_STRING
            # return return_value
            return []

        # Ensure Value is in range an i16
        if return_value < self.I16_MIN or return_value >= self.I16_MAX:
            return []
            # return_value = self.ERROR_CODE_OUT_OF_RANGE # return error code if value is out of range for type

        # Convert to u16 then package as two bytes
        adjusted_value = self.get_u16_value_from_i16_value(return_value)
        return_list = [adjusted_value & 0xFF] + [adjusted_value >> 8 & 0xFF]
        # if return value is 0x0201 we want a return of [0x01, 0x02]

        return return_list


    def get_u32_as_u8_list_from_u32(self, u32_value): # lsB is the first byte
        return_list = []
        for this_byte_index in range(self.SIZE_U32_IN_BYTES):
            return_list.append(u32_value >> 8*this_byte_index & 0xFF)
        return return_list


    # get_u8_as_u8_list_from_string: return an 8-bit unsigned integerr from a string value
    # - string values supported are 'hex', 'binary', and 'decimal'
    # -- hex must have x in the string. binary must have 'b' in the string. decimal is default if x or b is not included in string.
    # - returns: positive value between 0-255 if string is valid
    # -- Negative Value containing Error Code if received string cannot be converted to desired type
    def get_u32_as_u8_list_from_string(self, this_string):
        return_value = -1
        lower_case_string = this_string.lower() # lower case for non-case sensitive checking of character values

        # Determine number base
        if 'x' in lower_case_string:
            number_base = self.HEXIDECIMAL_BASE_CHARACTERS
            # add 0 character at the front if needed for the 'int' conversion
            if '0' !=  lower_case_string[0]:
                lower_case_string = '0' + lower_case_string
        elif 'b' in lower_case_string:
            number_base = self.BINARY_BASE_CHARACTERS
            # add 0 character at the front if needed for the 'int' conversion
            if '0' !=  lower_case_string[0]:
                lower_case_string = '0' + lower_case_string
        elif '.' in lower_case_string:
            number_base = self.FLOAT_BASE_CHARACTERS
            return [] # Invalid Input: Float representation not allowed for integers
        else:
            number_base = self.DECIMAL_BASE_CHARACTERS
            # do not need to add characters for 'int' conversion

        # print("number base: " + str(number_base))

        # Convert String to Integer
        try:
            return_value = int(lower_case_string, number_base)
        except ValueError:  # exit and return error code if cannot convert
            # return_value = self.ERROR_CODE_INVALID_STRING
            # return return_value
            return []

        # Ensure Value is in range of u8
        if return_value < self.U32_MIN or return_value >= self.U32_MAX:
            # return_value = self.ERROR_CODE_OUT_OF_RANGE # return error code if value is out of range for type
            return []

        return_list = [return_value & 0xFF] + [return_value >> 8 & 0xFF] + [return_value >> 16 & 0xFF] + [return_value >> 24 & 0xFF]
        return return_list

    def get_i32_value_from_u32_value(self, u32_value):
        # This algorithm will presume we want the lower 16 bits of anything, it does not range check
        u32_value_truncated = u32_value & 0xFFFFFFFF
        # Determine if should be negative or positive
        if u32_value_truncated >= self.I32_MAX: # negative value
            i32_value = u32_value_truncated - self.U32_MAX # 0xFFFF to i32 = 0xFFFF- 0x10000 = -1
        else:
            i32_value = u32_value_truncated
        return i32_value

    # get_i32_as_u8_list_from_string: return a list of 8-bit unsigned integers from a string value containing a 
    # - string values supported are 'hex', 'binary', and 'decimal'
    # -- hex must have x in the string. binary must have 'b' in the string. decimal is default if x or b is not included in string.
    # - returns: positive value between 0-255 if string is valid
    # -- Negative Value containing Error Code if received string cannot be converted to desired type
    def get_i32_as_u8_list_from_string(self, this_string):
        return_value = -1
        lower_case_string = this_string.lower() # lower case for non-case sensitive checking of character values

        # Determine number base
        if 'x' in lower_case_string:
            number_base = self.HEXIDECIMAL_BASE_CHARACTERS
            # add 0 character at the front if needed for the 'int' conversion
            if '0' !=  lower_case_string[0]:
                lower_case_string = '0' + lower_case_string
        elif 'b' in lower_case_string:
            number_base = self.BINARY_BASE_CHARACTERS
            # add 0 character at the front if needed for the 'int' conversion
            if '0' !=  lower_case_string[0]:
                lower_case_string = '0' + lower_case_string
        elif '.' in lower_case_string:
            number_base = self.FLOAT_BASE_CHARACTERS
            return [] # Invalid Input: Float representation not allowed for integers
        else:
            number_base = self.DECIMAL_BASE_CHARACTERS
            # do not need to add characters for 'int' conversion

        # print("number base: " + str(number_base))

        # Convert String to Integer
        try:
            return_value = int(lower_case_string, number_base)
        except ValueError:  # exit and return error code if cannot convert
            # return_value = self.ERROR_CODE_INVALID_STRING
            # return return_value
            return []

        # Ensure Value is in range an i16
        if return_value < self.I32_MIN or return_value >= self.I32_MAX:
            return []
            # return_value = self.ERROR_CODE_OUT_OF_RANGE # return error code if value is out of range for type

        # Convert to u16 then package as two bytes
        adjusted_value = self.get_u32_value_from_i32_value(return_value)
        return_list = [adjusted_value & 0xFF] + [adjusted_value >> 8 & 0xFF] + [adjusted_value >> 16 & 0xFF] + [adjusted_value >> 24 & 0xFF]
        # if return value is 0x0201 we want a return of [0x01, 0x02]

        return return_list


    def get_i8_value_from_u8_value(self, u8_value):
        # This algorithm will presume we want the lower 16 bits of anything, it does not range check
        u8_value_truncated = u8_value & 0xFF
        # Determine if should be negative or positive
        if u8_value_truncated >= self.I8_MAX: # negative value
            i8_value = u8_value_truncated - self.U8_MAX # 0xFFFF to i16 = 0xFFFF- 0x10000 = -1
        else:
            i8_value = u8_value_truncated
        return i8_value

    def get_i16_value_from_u16_value(self, u16_value):
        # This algorithm will presume we want the lower 16 bits of anything, it does not range check
        u16_value_truncated = u16_value & 0xFFFF
        # Determine if should be negative or positive
        if u16_value_truncated >= self.I16_MAX: # negative value
            i16_value = u16_value_truncated - self.U16_MAX # 0xFFFF to i16 = 0xFFFF- 0x10000 = -1
        else:
            i16_value = u16_value_truncated
        return i16_value

    def get_u16_value_from_i16_value(self, i16_value):
        # This algorithm presumes that i16_value is in range
        if i16_value >= 0:
            return i16_value
        else:
            return self.U16_MAX + i16_value # if i16_value = -1, then return should be 0xFFFF, -2 then 0xFFFE

    def get_u32_value_from_i32_value(self, i32_value):
        # This algorithm presumes that i16_value is in range
        if i32_value >= 0:
            return i32_value
        else:
            return self.U32_MAX + i32_value # if i16_value = -1, then return should be 0xFFFFFFFF, -2 then 0xFFFFFFFE

    # get_float_as_u8_list_from_string: return a list of 8-bit unsigned integers from a string value containing a 
    # - string values supported are 'hex', 'binary', and 'decimal'
    # -- hex must have x in the string. binary must have 'b' in the string. decimal is default if x or b is not included in string.
    # - returns: positive value between 0-255 if string is valid
    # -- Negative Value containing Error Code if received string cannot be converted to desired type
    def get_float_as_u8_list_from_string(self, this_string):
        return_value = -1
        lower_case_string = this_string.lower() # lower case for non-case sensitive checking of character values

        # Determine number base
        if 'x' in lower_case_string:
            number_base = self.HEXIDECIMAL_BASE_CHARACTERS
            # add 0 character at the front if needed for the 'int' conversion
            if '0' !=  lower_case_string[0]:
                lower_case_string = '0' + lower_case_string
        elif 'b' in lower_case_string:
            number_base = self.BINARY_BASE_CHARACTERS
            # add 0 character at the front if needed for the 'int' conversion
            if '0' !=  lower_case_string[0]:
                lower_case_string = '0' + lower_case_string
        elif '.' in lower_case_string:
            number_base = self.FLOAT_BASE_CHARACTERS
        else:
            number_base = self.DECIMAL_BASE_CHARACTERS
            # do not need to add characters for 'int' conversion

        # print("number base: " + str(number_base))

        # Convert String to Integer
        if number_base in [self.FLOAT_BASE_CHARACTERS, self.DECIMAL_BASE_CHARACTERS]: # Decimal/ Float -> Convert 'float' to memory units
            try:
                # Convert string to a float
                float_value = float(lower_case_string)
                # Now convert the float into it's internal memory representation (four bytes)
            except ValueError:  # exit and return error code if cannot convert
                # return_value = self.ERROR_CODE_INVALID_STRING
                # return return_value
                return []      
            # Now convert the float into it's internal memory representation (four bytes)
            # - REVIEW: move to function convert_float_value_to_float_memory_representation_u32?
            # -- I see each of these 'unpack' commands are used at least twice each...
            return_value = (struct.unpack('<I', struct.pack('<f', float_value)))[0]
            # REVIEW: should be able to simplify
            # - list(struct.pack("!f", 5.1))
            # -- [64, 163, 51, 51]

        else: # Hex/ Binary Representation -> What is actually written in memory, just split, do not modify
            try:
                return_value = int(lower_case_string, number_base)
            except ValueError:  # exit and return error code if cannot convert
                # return_value = self.ERROR_CODE_INVALID_STRING
                # return return_value
                return []

        # Ensure Value is in range for a four byte value
        if return_value < self.U32_MIN or return_value >= self.U32_MAX:
            return []
        # Convert to u16 then package as two bytes
        return_list = [return_value & 0xFF] + [return_value >> 8 & 0xFF] + [return_value >> 16 & 0xFF] + [return_value >> 24 & 0xFF]
            # if return value is 0x0201 we want a return of [0x01, 0x02]

        return return_list

    def convert_float_value_to_float_memory_representation_u32(self, float_value):
        # Now convert the float into it's internal memory representation (four bytes)
        return_value = (struct.unpack('<I', struct.pack('<f', float_value)))[0]
        return return_value

    # receives: u32 of the memory representation of a float value
    # returns: displayable floating point value 
    def float_memory_representation_to_float_value(self, float_memory_representation_u32):
        byte_string_representation = struct.pack('<I', float_memory_representation_u32)
        float_value = struct.unpack('<f', byte_string_representation)[0]
        # if math.isnan(float_value):
        #     print("not a valid float!")
        return float_value

    # receives: u32 of the memory representation of a float value
    # returns: displayable floating point value (with minimum number of characters to represent the value)
    def float_memory_representation_to_displayable_float_value(self, float_memory_representation_u32):
        MIN_ROUNDING_AMOUNT = 0 # a float can only round to six or 7 chars, so if we get to six, we just abandon rouding
        MAX_ROUNDING_AMOUNT = 6 # a float can only round to six or 7 chars, so if we get to six, we just abandon rouding
        rounding_successful = False
        # Determine calculated float value
        float_value = self.float_memory_representation_to_float_value(float_memory_representation_u32)
        # Now try to round it and convert it back to float_memory_representation_u32
        # - if value has not changed, accept the rounded value as the display value, since it is proven accurate
        for this_round_amount in range(MIN_ROUNDING_AMOUNT, MAX_ROUNDING_AMOUNT):
            rounded_float_value = round(float_value, this_round_amount)
            rounded_value_memory_representation = self.convert_float_value_to_float_memory_representation_u32(rounded_float_value)
            if rounded_value_memory_representation == float_memory_representation_u32:
                # print("rounding match!")
                rounding_successful = True
                break

        if not rounding_successful:
            return float_value
        else:
            return rounded_float_value
        # float_value_ceil = struct.unpack('<f', struct.pack('<I', float_memory_representation_u32+1))[0]
        # float_value = struct.unpack('<f', struct.pack('<I', float_memory_representation_u32))[0]
        # float_value_floor = struct.unpack('<f', struct.pack('<I', float_memory_representation_u32-1))[0]

        # >>> struct.unpack('<f', struct.pack('<I', 1051931442))[0]
        # 0.34999996423721313
        # >>> struct.unpack('<f', struct.pack('<I', 1051931443))[0]
        # 0.3499999940395355
        # >>> struct.unpack('<f', struct.pack('<I', 1051931444))[0]
        # 0.3500000238418579

    def get_variable_length_in_bytes_from_variable_type_string(self, this_type):
        if this_type == "u8" or this_type == "h8":
            this_length = self.SIZE_U8_IN_BYTES
        elif this_type == "u16" or this_type == "h16":
            this_length = self.SIZE_U16_IN_BYTES
        elif this_type == "i16":
            this_length = self.SIZE_I16_IN_BYTES
        elif this_type == "u32"  or this_type == "h32":
            this_length = self.SIZE_U32_IN_BYTES
        elif this_type == "i32":
            this_length = self.SIZE_I32_IN_BYTES
        elif this_type == "float":
            this_length = self.SIZE_FLOAT_IN_BYTES
        else: 
            print("unrecognized type (%s), defaulting to u8" % str(this_type))
            # self.display_message("unrecognized type (%s), defaulting to u8" % str(this_type))
            this_length = type_converter.SIZE_U8_IN_BYTES
        return this_length

    # convert_modbus_list_of_u8s_to_memory_representation: 
    # - modbus sends a bunch of u16 words, but they should go to memory in reverse order (per u16)
    # -- this function expects modbus_list to be a size that is a multiple of 2 bytes, odd bytes at the end are ignored
    def convert_modbus_list_of_u8s_to_memory_representation(self, modbus_list):
        memory_list = []
        this_index = 0
        while this_index < len(modbus_list)-1: #-1 because we do this in pairs of bytes, so we ignore odd bytes at the end
            memory_list.append(modbus_list[this_index+1])
            memory_list.append(modbus_list[this_index])
            this_index += 2
        return memory_list

    def convert_list_of_ints_to_list_of_hex(self, list_of_u8s):
        return_list = []
        this_index = 0
        while this_index < len(list_of_u8s):
            return_list.append(hex(list_of_u8s[this_index]))
        return return_list

type_converter = TypeConversions()


