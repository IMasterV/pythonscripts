import asyncio

# асинхронный Modbus TCP сервер
from pymodbus.server.async_io import StartAsyncTcpServer

# хранилище данных Modbus
from pymodbus.datastore import (
    ModbusSlaveContext, # контекст одного Slave
    ModbusServerContext, # контекст сервера
    ModbusSequentialDataBlock, # последовательный блок регистров
)
from plc_dataclasses.data_plc import Parameters
from dataclasses import fields
from baseclasses.gpio import GPIO

# eth2
from baseclasses.modbus_connect import ConnectModule
#from baseclasses.value_convert import ConvertValue
from pymodbus import Framer

from baseclasses.response import SpeWriteRead
from plc_dataclasses.module510 import System


module210 = ConnectModule(comm='tcp', host='192.168.0.11', port=502,
                          framer=Framer.SOCKET).request_module()

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


system_param_module = System
module510 = SpeWriteRead(device_address=1)

params = Parameters()
plc_gpio = GPIO()



# создание 101 holding-регистр (0...100)
hr_block = ModbusSequentialDataBlock(
    address=0, # начальный адрес
    values=[0] * 101 # начальные значения
)

# контекст одного Modbus slave
store = ModbusSlaveContext(
    hr=hr_block, # holding registers
    zero_mode=True # адресация начинается с 0
)

# контейнер всех slave-устройств сервера
context = ModbusServerContext(
    slaves=store,
    single=True # только один slave (ID = 0) не учитывается
)

async def update_registers():
    """
    Задача, которая обновляет и читает значения регистров
    """

    m210_errors = 0
    m210_requests = 0


    counter = 0
    print('listening')

    while True:
        counter += 1

        for f in fields(params):
            modbus_field = getattr(params, f.name)

            #пишем в Modbus
            if f.name == "in1":
                modbus_field.value = await plc_gpio.rd_in1()

                context[0].setValues(
                    3,  # Holding Register
                    modbus_field.addr,
                    [int(modbus_field.value)] * modbus_field.count
                )

            if f.name == "in2":
                modbus_field.value = await plc_gpio.rd_in2()

                context[0].setValues(
                    3,  # Holding Register
                    modbus_field.addr,
                    [int(modbus_field.value)] * modbus_field.count
                )

            if f.name == "time":

                response = module210.rd_holding_registers(address=0xF080, count=2)
                modbus_field.value = response
                if response is not None:
                    context[0].setValues(
                        3,  # Holding Register
                        modbus_field.addr,
                        [*modbus_field.value] * modbus_field.count
                    )

            if f.name == "m210_errors":
                context[0].setValues(
                    3,  # Holding Register
                    modbus_field.addr,
                    [module210.errors_count] * modbus_field.count
                )

            if f.name == "m210_requests":
                context[0].setValues(
                    3,  # Holding Register
                    modbus_field.addr,
                    [module210.requests_count] * modbus_field.count
                )

            if f.name == "m210_reconnects":
                context[0].setValues(
                    3,  # Holding Register
                    modbus_field.addr,
                    [module210.reconnects] * modbus_field.count
                )


            if f.name == "m510_time":

                system_param_module.system_time.value = module510.read_data(
                    rd_registers=system_param_module.system_time.addr,
                    count=system_param_module.system_time.count)

                modbus_field.value = system_param_module.system_time.value
                if system_param_module.system_time.value is not None:
                    context[0].setValues(
                        3,  # Holding Register
                        modbus_field.addr,
                        [*modbus_field.value] * modbus_field.count
                    )


            if f.name == "m510_errors":
                context[0].setValues(
                    3,  # Holding Register
                    modbus_field.addr,
                    [module510.errors_count] * modbus_field.count
                )

            if f.name == "m510_requests":
                context[0].setValues(
                    3,  # Holding Register
                    modbus_field.addr,
                    [module510.requests_count] * modbus_field.count
                )

            if f.name == "m110_1_value":
                response = module110_1.rd_holding_registers(address=0xF000, count=4, id=16)
                if response is not None:
                    context[0].setValues(
                        3,  # Holding Register
                        modbus_field.addr,
                        [*response] * modbus_field.count
                    )
                else:
                    context[0].setValues(
                        3,  # Holding Register
                        modbus_field.addr,
                        [*[0, 0, 0, 0]] * modbus_field.count
                    )


            if f.name == "m110_1_errors":
                context[0].setValues(
                    3,  # Holding Register
                    modbus_field.addr,
                    [module110_1.errors_count] * modbus_field.count
                )

            if f.name == "m110_1_requests":
                context[0].setValues(
                    3,  # Holding Register
                    modbus_field.addr,
                    [module110_1.requests_count] * modbus_field.count
                )

            if f.name == "m110_1_reconnects":
                context[0].setValues(
                    3,  # Holding Register
                    modbus_field.addr,
                    [module110_1.reconnects] * modbus_field.count
                )



            read_val = context[0].getValues(3, modbus_field.addr, modbus_field.count)

            if f.name == "do1":
                await plc_gpio.wr_out1(value=str(read_val[0]))

            if f.name == "do2":
                await plc_gpio.wr_out2(value=str(read_val[0]))


        await asyncio.sleep(1)


async def main():
    # запускаем фоновую задачу обновления регистров
    asyncio.create_task(update_registers())

    # Запускаем Modbus TCP сервер
    await StartAsyncTcpServer(
        context=context,
        address=("0.0.0.0", 5020)
    )

if __name__ == "__main__":
    # запуск asyncio в event loop
    asyncio.run(main())

