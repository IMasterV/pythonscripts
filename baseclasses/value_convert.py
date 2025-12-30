import struct

from datetime import datetime, timedelta, timezone

class ConvertValue:
    def __init__(self):
        self.some = ''

    @staticmethod
    def int16_list_to_float(int_list):
        if len(int_list) != 2:
            raise ValueError("Ожидалось два значения int16")

        low, high = int_list
        byte_data = struct.pack('<HH', low, high)  # два uint16 в little-endian
        return struct.unpack('<f', byte_data)[0]

    @staticmethod
    def float_to_int16_list(value):
        # Упаковываем float в 4 байта little-endian
        byte_data = struct.pack('<f', value)
        # Распаковываем как два uint16 (low, high)
        low, high = struct.unpack('<HH', byte_data)
        return [low, high]

    @staticmethod
    def registers_to_ascii(registers):
        # [30797, 12597, 11568, 12851, 20292]
        """
        Converts an array of 16-bit registers to an ASCII string.

        :param registers: List of 16-bit numbers (Modbus registers).
        :return: ASCII string.
        """
        byte_array = bytearray()

        for reg in registers:
            byte_array.extend(reg.to_bytes(2, byteorder='little'))  # Convert register to 2 bytes

        return byte_array.decode("ascii", errors="ignore")  # Decode to string

    @staticmethod
    def modbus_time_to_datetime(registers):
        """
        registers: list[int] -> [high_word, low_word]
        Возвращает datetime (UTC)
        """
        if len(registers) != 2:
            raise ValueError("Нужно ровно 2 регистра")

        low, high = registers
        seconds = (high << 16) | low

        epoch_2000 = datetime(2000, 1, 1, tzinfo=timezone.utc)
        return epoch_2000 + timedelta(seconds=seconds)