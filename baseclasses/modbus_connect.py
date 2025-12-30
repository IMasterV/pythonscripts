import csv
import struct
import time

from pymodbus.client import (ModbusSerialClient, ModbusTcpClient)
from pymodbus import (
    framer,
    ModbusException)
from pymodbus.framer import ModbusSocketFramer


def _validate_com_settings(settings):
    """Проверка корректности настроек COM порта"""
    if len(settings) != 5:
        raise ValueError("com_settings должен содержать 5 элементов: (port, baudrate, bytesize, parity, stopbits)")

    port, baudrate, bytesize, parity, stopbits = settings

    # Проверка параметров
    if not isinstance(port, str):
        raise TypeError(f"Порт должен быть строкой, получен {type(port)}")

    if baudrate not in [300, 600, 1200, 2400, 4800, 9600, 19200, 38400, 57600, 115200]:
        print(f"Предупреждение: нестандартная скорость {baudrate}")

    if bytesize not in [5, 6, 7, 8]:
        raise ValueError(f"Некорректный bytesize: {bytesize}")

    if parity.upper() not in ['N', 'E', 'O', 'M', 'S']:
        raise ValueError(f"Некорректная parity: {parity}")

    if stopbits not in [1, 1.5, 2]:
        raise ValueError(f"Некорректные stopbits: {stopbits}")


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

        # Проверяем настройки для COM порта
        if self._comm == 'com' and com_settings:
            _validate_com_settings(com_settings)

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
                timeout=1,
                retries=0,
                # retry_on_empty=False,y
                # source_address=("localhost", 0),
            )
            print(f'connect to {self.host}')
            client.connect()
            return ModbusFunction(client, comm=self._comm)

        if self._comm == 'com':
            client = ModbusSerialClient(
                port=self.com_settings[0],
                # framer=framer,
                timeout=1,
                retries=1,
                retry_on_empty=False,
                close_comm_on_error=False,
                strict=True,
                baudrate=self.com_settings[1],
                bytesize=self.com_settings[2],
                parity=self.com_settings[3],
                stopbits=self.com_settings[4],
                # handle_local_echo=False,
            )
            print(f"connect to {self.com_settings[0]}")
            if client.connect():
                return ModbusFunction(client, comm=self._comm)
            else:
                raise ConnectionError("Connection failed")


class ModbusFunction:
    """Functions Modbus"""

    def __init__(self, client, comm):
        self.client = client
        self.comm = comm

        # счётчики
        self.requests_count = 0
        self.errors_count = 0
        self.reconnects = 0


    def _reconnect(self):
        if self.comm == 'tcp':
            return self._reconnect_tcp()
        # elif self.comm == 'com':
        #     return self._reconnect_serial()
        return False

    def _reconnect_tcp(self):
        try:
            self.client.close()
            if self.client.connect():
                self.reconnects += 1
                print("Modbus reconnected")
                return True
        except Exception:
            pass
        return False

    # def _reconnect_serial(self):
    #     try:
    #         if self.client.socket:
    #             self.client.socket.close()
    #         #time.sleep(0.2)
    #         if self.client.connect():
    #             self.reconnects += 1
    #             print("RTU port reopened")
    #             return True
    #     except Exception as e:
    #         print("Reconnect error:", e)
    #     return False


    def rd_holding_registers(self, address, count, id=1):
        self.requests_count += 1

        # if not self.client.connected:
        #     if not self._reconnect_tcp():
        #         self.errors_count += 1
        #         return None

        # ТОЛЬКО TCP проверяет connected
        if self.comm == 'tcp' and not self.client.connected:
            if not self._reconnect():
                self.errors_count += 1
                return None

        #print("get and verify data")
        try:
            value = self.client.read_holding_registers(address=address, count=count, slave=id)
        except ModbusException as exc:
            print(f"ModbusException: {exc}")
            self.errors_count += 1
            if self.comm == 'tcp':
                self._reconnect()
            #self.client.close()
            return None

        if value.isError():  # pragma no cover
            print(f"Received Modbus library error({value})")
            self.errors_count += 1
            # TCP можно переподключать
            if self.comm == 'tcp':
                self._reconnect()
            #self.client.close()
            return None

        return value.registers

    def wr_holding_registers(self, address, values, id=1):
        #print("set and verify data")
        try:
            value = self.client.write_registers(address=address, values=values, slave=id)

        except ModbusException as exc:
            print(f"ModbusException: {exc}")
            self.errors_count += 1
            self.client.close()
            return None


        if value.isError():  # pragma no cover
            print(f"Received Modbus library error({value})")
            self.errors_count += 1
            self.client.close()
            return None

        return True