import csv
import struct
import time
# from pymodbus import framer, pymodbus_apply_logging_config
from pymodbus.client import (ModbusSerialClient, ModbusTcpClient)
from pymodbus.pdu import ExceptionResponse
# from pymodbus.transaction import (ModbusAsciiFramer, ModbusRtuFramer)
from pymodbus import (
    framer,
    # Framer,
    ExceptionResponse,
    ModbusException,
    pymodbus_apply_logging_config)
from pymodbus.framer import ModbusSocketFramer
from pymodbus.register_read_message import ReadHoldingRegistersRequest, ReadHoldingRegistersResponse
from pymodbus.register_write_message import WriteMultipleRegistersRequest, WriteMultipleRegistersResponse


class ModbusRequest:
    def __init__(self, device_address, register_address):
        self.device_address = device_address
        self.register_address = register_address

    @classmethod
    def _compute_crc(cls, data):
        """Computes CRC-16 for a Modbus RTU packet"""
        crc = 0xFFFF
        for byte in data:
            crc ^= byte
            for _ in range(8):
                if crc & 0x0001:
                    crc = (crc >> 1) ^ 0xA001
                else:
                    crc >>= 1
        return crc.to_bytes(2, byteorder='little')  # CRC � little-endian

    def generate_modbus_read_request(self, count):
        """function_code (0x03)"""
        function_code = 0x03  # Read Holding Registers
        request = ReadHoldingRegistersRequest(address=self.register_address, count=count)
        pdu = request.encode()
        frame = bytes([self.device_address, function_code]) + pdu
        crc = self._compute_crc(frame)
        return frame + crc

    def generate_modbus_write_request(self, values):
        """function_code (0x10)"""
        function_code = 0x10  # Write Multiple Registers
        request = WriteMultipleRegistersRequest(address=self.register_address, values=values)
        pdu = request.encode()
        frame = bytes([self.device_address, function_code]) + pdu
        crc = self._compute_crc(frame)
        return frame + crc


class ModbusResponseMixin:
    def parse_modbus_response(self, response):
        MODBUS_EXCEPTIONS = {
            0x01: "Неверная функция (Illegal Function)",
            0x02: "Неверный адрес регистра (Illegal Data Address)",
            0x03: "Недопустимое значение данных (Illegal Data Value)",
            0x04: "Ошибка устройства (Slave Device Failure)",
            0x05: "Подтверждено (Acknowledge)",
            0x06: "Устройство занято (Slave Device Busy)",
            0x08: "Ошибка памяти (Memory Parity Error)",
            0x0A: "Путь недоступен (Gateway Path Unavailable)",
            0x0B: "Устройство не отвечает (Gateway Target Device Failed to Respond)"
        }


        """Parses a Modbus RTU response (reading 0x03 or writing 0x10) using pymodbus"""
        if len(response) < 5:  # Minimum valid Modbus response length
            raise ValueError("Invalid response: insufficient length")

        device_address, function_code = struct.unpack(">BB", response[:2])

        if function_code & 0x80:
            exception_code = response[2]
            error_msg = MODBUS_EXCEPTIONS.get(exception_code, f"Неизвестная ошибка (code: {exception_code})")
            raise ValueError(f"Modbus исключение от устройства {device_address}: {error_msg}")

        if function_code == 0x03:  # Response for reading registers
            parsed_response = ReadHoldingRegistersResponse()
            parsed_response.decode(response[2:-2])  # Decode PDU excluding CRC
            return list(parsed_response.registers)
            #     {
            #     "device_address": device_address,
            #     "function_code": function_code,
            #     "register_values": list(parsed_response.registers)
            # }

        elif function_code == 0x10:  # Response for writing registers
            parsed_response = WriteMultipleRegistersResponse()
            parsed_response.decode(response[2:-2])  # Decode PDU excluding CRC
            return {
                "device_address": device_address,
                "function_code": function_code,
                "register_address": parsed_response.address,
                "register_count": parsed_response.count
            }

        else:
            raise ValueError(f"Unsupported function code: {function_code}")


class ModbusFeatures:
    def __init__(self):
        self.some = ''

    @staticmethod
    def create_modbus_rtu_request(device_address, function_code, register_address, data_count):
        def compute_crc(data):
            """
            Computes CRC-16 for a Modbus RTU packet.
            """
            crc = 0xFFFF
            for byte in data:
                crc ^= byte
                for _ in range(8):
                    if crc & 0x0001:
                        crc = (crc >> 1) ^ 0xA001
                    else:
                        crc >>= 1
            return crc.to_bytes(2, byteorder='little')  # CRC (little-endian)

        """
        Creates a Modbus RTU request in byte format.
        :param device_address: Modbus device address
        :param function_code: Modbus function code
        :param register_address: Starting register address
        :param data_count: Number of registers to be transmitted
        :return: Modbus RTU request as a list of bytes (list[int])
        """
        # Validate input ranges
        if not (1 <= device_address <= 32):
            raise ValueError("Device address must be between 1 and 32")
        if not (1 <= function_code <= 21):
            raise ValueError("Function code must be between 1 and 21")
        if not (0 <= register_address <= 65535):
            raise ValueError("Register address must be between 0 and 65535")

        # Create packet without CRC
        if function_code == 0x03:
            if not (1 <= data_count <= 125):
                raise ValueError("Data count for reading must be between 1 and 125")
            frame = struct.pack('>B B H H', device_address, function_code, register_address, data_count)

        elif function_code == 0x10:
            if not (1 <= len(data_count) <= 123):
                raise ValueError("Data count for writing must be between 1 and 123")
            register_count = len(data_count)
            byte_count = register_count * 2  # quantity byte
            frame = struct.pack('>B B H H B', device_address, function_code, register_address, register_count,
                                byte_count)
            for value in data_count:
                frame += struct.pack('>H', value)  # write 16-bit values

        # Compute CRC-16 and append it to the packet
        frame += compute_crc(frame)

        # Return byte list
        print(f"Request: {list(frame)}")
        return list(frame)

    @staticmethod
    def parse_modbus_rtu_response(response):
        print(response)
        """
        Parses a Modbus RTU response and returns parsed data.

        Supports:
        - Function 3 (0x03): Read Holding Registers > Returns a list of register values
        - Function 16 (0x10): Write Multiple Registers > Returns confirmation of written registers

        :param response: Byte array of the Modbus RTU response (list[int] or bytes)
        :return: List of register values (for function 3) or confirmation (for function 16)
        """
        if len(response) < 5:
            raise ValueError("Invalid response: packet too short")

        device_address = response[0]
        function_code = response[1]
        payload, crc_received = response[2:-2], response[-2:]

        if function_code == 0x03:  # Read Holding Registers
            byte_count = payload[0]  # quantity bytes
            data = payload[1:]  # Skip byte count
            if len(data) != byte_count:
                raise ValueError("Error: Data byte count does not match header")
            registers = (struct.unpack(">H", bytes(data[i:i + 2]))[0] for i in range(0, len(data), 2))
            return registers

        elif function_code == 0x10:  # Write Multiple Registers
            if len(payload) != 4:
                raise ValueError("Error: Invalid response length for function 16")

            address, register_count = struct.unpack(">HH", bytes(payload))
            return (hex(address), register_count)

        else:
            raise ValueError(f"Unsupported function code: {function_code}")

    @staticmethod
    def read_file_requests():
        bytes_requests = []
        with open('requests.csv', encoding='utf-8') as file:
            rows = csv.reader(file)  # Create reader object
            for row in rows:
                bytes_requests.append(bytes([int(byte, 16) for byte in row]))

        return bytes_requests

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


class ConnectModule:
    def __init__(self, comm, host='', port=502, com_settings=None, framer=ModbusSocketFramer):
        if isinstance(comm, str):
            if comm == 'tcp' or comm == 'com':
                self._comm = comm
            else:
                raise AttributeError('com or tcp')
        else:
            raise AttributeError('comm type must be str')
        self.host = host
        self.port = port
        self.com_settings = com_settings
        self.framer = framer

    @property
    def comm(self):
        return self._comm

    @comm.setter
    def comm(self, comm):
        if isinstance(comm, str):
            if comm == 'tcp' or comm == 'com':
                self._comm = comm
            else:
                raise AttributeError('com or tcp')
        else:
            raise AttributeError('comm type must be str')

    def request_module(self):

        """Run sync client."""
        # activate debugging
        # pymodbus_apply_logging_config("DEBUG")
        if self._comm == 'tcp':
            client = ModbusTcpClient(
                self.host,
                port=self.port,
                framer=self.framer,
                timeout=10,
                retries=4,
                # retry_on_empty=False,y
                # source_address=("localhost", 0),
            )
            print(f'connect to {self.host}')
            client.connect()
            return ModbusFunction(client)

        if self._comm == 'com':
            client = ModbusSerialClient(
                self.com_settings[0],
                # framer=framer,
                # timeout=10,
                # retries=3,
                # retry_on_empty=False,
                # close_comm_on_error=False,.
                # strict=True,
                baudrate=self.com_settings[1],
                bytesize=self.com_settings[2],
                parity=self.com_settings[3],
                stopbits=self.com_settings[4],
                # handle_local_echo=False,
            )
            print(f"connect to {self.com_settings[0]}")
            client.connect()
            return ModbusFunction(client)


class ModbusFunction:
    """Functions Modbus"""

    def __init__(self, client):
        self.client = client

    def rd_holding_registers(self, address, count, id=1):
        #print("get and verify data")
        try:
            value = self.client.read_holding_registers(address=address, count=count, slave=id)
        except ModbusException as exc:
            print(f"Received ModbusException({exc}) from library")
            self.client.close()
            return
        if value.isError():  # pragma no cover
            print(f"Received Modbus library error({value})")
            self.client.close()
            return (value.isError())
        else:
            #print(value.registers)
            return value.registers

    def wr_holding_registers(self, address, values, id=1):
        #print("set and verify data")
        try:
            value = self.client.write_registers(address=address, values=values, slave=id)

        except ModbusException as exc:
            print(f"Received ModbusException({exc}) from library")
            self.client.close()
            return
        if value.isError():  # pragma no cover
            print(f"Received Modbus library error({value})")
            self.client.close()
            return (value.isError())
        else:
            return value.registers