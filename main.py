import time

from baseclasses.modbus_connect import ConnectModule
from baseclasses.value_convert import ConvertValue
from pymodbus import Framer

from baseclasses.response import SpeWriteRead
from plc_dataclasses.module510 import System
from baseclasses.modbus_operations import ModbusFeatures


######################## RS-485-3 CONNECT MODULE
from pymodbus.client import ModbusSerialClient
import serial

# Простое подключение без класса
# def connect_to_serial():
#     client = ModbusSerialClient(
#         port="/dev/ttyS3",
#         baudrate=115200,
#         bytesize=8,
#         parity='N',
#         stopbits=1,
#         timeout=2.0
#     )
#
#     if client.connect():
#         print("Подключено успешно!")
#         return client
#     else:
#         print("Ошибка подключения")
#         return None
#
#
# # Использование
# client = connect_to_serial()
# if client:
#     # Читаем 10 регистров с адреса 0
#     response = client.read_holding_registers(0, 1, slave=1)
#     print(response)
#     if response.isError():
#         print("Ошибка:", response)
#     else:
#         print("Регистры:", response.registers)
#     client.close()



com_settings_115200_8N1 = (
    "/dev/ttyS3",
    9600,
    8,
    'N',
    1
)
conn = ConnectModule(
    comm='com',           # Указываем тип соединения 'com'
    com_settings=com_settings_115200_8N1  # Передаем настройки COM порта
)

module110_1 = conn.request_module()
response = module110_1.rd_holding_registers(address=0xF000, count=2, id=16)
print(response)





######################### TCP CONNECT MODULE
# module210 = ConnectModule(comm='tcp', host='192.168.0.11', port=502,
#                           framer=Framer.SOCKET).request_module()
#
# while True:
#     response = module210.rd_holding_registers(address=0xF080, count=2)
#     print("Response:", response)
#     print(
#         f"Requests: {module210.requests_count}, "
#         f"Errors: {module210.errors_count}",
#         f"Reconnections: {module210.reconnects}"
#     )
#
#     time.sleep(1)





######################### SPE CONNECT MODULE
# request = 0
# reconnect = 0
# error = 0
#
# system_param_module = System
#
# device = SpeWriteRead(device_address=1)
#
# while True:
#
#     system_param_module.system_time.value = device.read_data(rd_registers=system_param_module.system_time.addr,
#                                                             count=system_param_module.system_time.count)
#
#     print(system_param_module.system_time.value)
#     print(f'request {device.request}')
#     print(f'error {device.error}')
#     time.sleep(1)


