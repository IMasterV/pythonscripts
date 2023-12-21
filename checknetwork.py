import time
from pymodbus import framer, pymodbus_apply_logging_config
from pymodbus.client import (ModbusSerialClient, ModbusTcpClient)
from pymodbus.exceptions import ModbusException
from pymodbus.pdu import ExceptionResponse
from pymodbus.transaction import (ModbusAsciiFramer, ModbusRtuFramer)


def write_mask_client(host, port, mask, frame=framer.ModbusSocketFramer):
    """Run sync client."""
    # activate debugging
    #pymodbus_apply_logging_config("DEBUG")

    print("get client")
    client = ModbusTcpClient(
        host,
        port=port,
        frame=framer,
        # timeout=10,
        # retries=3,
        # retry_on_empty=False,y
        # close_comm_on_error=False,
        # strict=True,
        # source_address=("localhost", 0),
    )

    print("connect to server")
    client.connect()

    print("set output and verify data")
    try:
        maskoutput = client.write_registers(address=470, values=mask, slave=1)
        #logmode = client.write_registers(address=272, values=0, slave=1)
        timeout = client.write_registers(address=700, values=0, slave=1)
    except ModbusException as exc:
        print(f"Received ModbusException({exc}) from library")
        client.close()
        return exc
    if maskoutput.isError():  # pragma no cover
        print(f"Received Modbus library error({maskoutput}) or ({timeout})")
        client.close()
        return maskoutput.isError()
    if isinstance(maskoutput, ExceptionResponse):  # pragma no cover
        print(f"Received Modbus library exception ({maskoutput}) or ({timeout})")
        # THIS IS NOT A PYTHON EXCEPTION, but a valid modbus message
        client.close()

    print("close connection")  # pragma no cover
    client.close()  # pragma no cover


def run_sync_simple_client(port, listSettings, listcountSettings, framer):
    """Run sync client."""

    # activate debugging
    #pymodbus_apply_logging_config()

    client = ModbusSerialClient(
        port,
        framer=framer,
        # timeout=10,
        # retries=3,
        # retry_on_empty=False,
        # close_comm_on_error=False,.
        # strict=True,
        baudrate=listSettings[0],
        bytesize=listSettings[1],
        parity=listSettings[3],
        stopbits=listSettings[2],
        # handle_local_echo=False,
    )

    print("connect to server")
    client.connect()
    rd = []
    print("get and verify data")
    try:
        readSettings = client.read_holding_registers(address=521, count=4, slave=16)
    except ModbusException as exc:
        print(f"Received ModbusException({exc}) from library")
        client.close()
        return
    if readSettings.isError():  # pragma no cover
        print(f"Received Modbus library error({readSettings})")
        client.close()
        return (readSettings.isError(), rd)
    else:
        print(readSettings.registers)
        rd = readSettings.registers
    if isinstance(readSettings, ExceptionResponse):  # pragma no cover
        print(f"Received Modbus library exception ({readSettings})")
        # THIS IS NOT A PYTHON EXCEPTION, but a valid modbus message
        client.close()

    print("set settings and verify data")
    try:
        wrSetting = client.write_registers(address=521, values=listcountSettings, slave=16)
        print(listcountSettings)
    except ModbusException as exc:
        print(f"Received ModbusException({exc}) from library")
        client.close()
        return
    if wrSetting.isError():  # pragma no cover
        print(f"Received Modbus library error({wrSetting})")
        client.close()
        return
    if isinstance(wrSetting, ExceptionResponse):  # pragma no cover
        print(f"Received Modbus library exception ({wrSetting})")
        # THIS IS NOT A PYTHON EXCEPTION, but a valid modbus message
        client.close()

    print("send Aply and verify data")
    try:
        wrAply = client.write_registers(address=65535, values=40961, slave=16)
    except ModbusException as exc:
        print(f"Received ModbusException({exc}) from library")
        client.close()
        return
    if wrSetting.isError():  # pragma no cover
        print(f"Received Modbus library error({wrAply})")
        client.close()
        return
    if isinstance(wrAply, ExceptionResponse):  # pragma no cover
        print(f"Received Modbus library exception ({wrAply})")
        # THIS IS NOT A PYTHON EXCEPTION, but a valid modbus message
        client.close()

    print("close connection")  # pragma no cover
    client.close()  # pragma no cover
    return (readSettings.isError(), rd)


host = input('Введите IP-адрес модуля (например, 10.2.25.84): ')

defaultbaudrate = int(input('2400/4800/9600/14400/19200/28800/38400/57600/115200: '))
while defaultbaudrate != 2400 and defaultbaudrate != 9600 and defaultbaudrate != 14400 and defaultbaudrate != 19200 and defaultbaudrate != 28800 and defaultbaudrate != 38400 and defaultbaudrate != 57600 and defaultbaudrate != 115200:
    defaultbaudrate = int(input('2400/4800/9600/14400/19200/28800/38400/57600/115200: '))

defaultdataword = int(input('7/8: '))
while defaultdataword != 8 and defaultdataword != 7:
    defaultdataword = int(input('7/8: '))

defaultstopbit = int(input('1/2: '))
while defaultstopbit != 1 and defaultstopbit != 2:
    defaultstopbit = int(input('1/2: '))

defaultparity = input('N/E/O: ').upper()
while defaultparity != 'N' and defaultparity != 'E' and defaultparity != 'O':
    defaultparity = input('N/E/O: ')

chekmodbusrtu = input('Проверяем modbus rtu (y/n): ').lower()
while chekmodbusrtu != 'y' and chekmodbusrtu != 'n':
    chekmodbusrtu = input('Проверяем modbus rtu (y/n): ')

if chekmodbusrtu == 'y':
    connectmodbusrtu = True
else:
    connectmodbusrtu = False


chekmodbusascii = input('Проверяем modbus ascii (y/n): ').lower()
while chekmodbusascii != 'y' and chekmodbusascii != 'n':
    chekmodbusascii = input('Проверяем modbus ascii (y/n): ')

if chekmodbusascii == 'y':
    connectmodbusascii = True
else:
    connectmodbusascii = False


baudSettings = [2400, 4800, 9600, 14400, 19200, 28800, 38400, 57600, 115200]
dataword = [7, 8]
stopbitSettings = [1, 2]
paritySettings = ['N', 'E', 'O']

start = True
pastconnect = False
lastconnect = False
resetmodule = False
fullstop = False

counterrorAply = 0

if connectmodbusrtu:
    print('Проверяем обмен на протоколе Modbus RTU')
    for i in range(9): # baudrate
        if fullstop:
            break
        for s in range(2): # stopbits
            if fullstop:
                break
            for k in range(3): # parity
                if fullstop:
                    break

                for j in range(5): # count connections

                    if start:
                        rdSettings = [defaultbaudrate, 8, defaultstopbit, defaultparity]
                        result1 = write_mask_client(host=host, port=502, mask=1)
                        if str(result1)[:12] == 'Modbus Error':
                            print('Ошибка связи с модулей по IP адресу ' + host)
                            fullstop = True
                            break
                        time.sleep(5)

                        start = False
                    elif errorConnections == False:
                        rdSettings = [baudSettings[wrSettings[0]], 8, stopbitSettings[wrSettings[2]], paritySettings[wrSettings[3]]]
                        pastconnect = False
                        resetmodule = False
                    elif errorConnections == True and resetmodule == False:
                        counterrorAply += 1
                        rdSettings = [baudSettings[rd[0]], 8, stopbitSettings[rd[2]], paritySettings[rd[3]]]            # повторить соединение на предыдущих настройках rdSettings и wrSettings
                        pastconnect = True

                    if pastconnect == False:
                        wrSettings = [i, 1, s, k]

                    print('Подключение по настройкам ' + str(rdSettings))
                    errorConnections, read = run_sync_simple_client(port='COM3', listSettings=rdSettings, listcountSettings=wrSettings, framer=ModbusRtuFramer)

                    if errorConnections == False and pastconnect == False:
                        rd = read
                        wr = wrSettings
                        if i == 8 and k == 2 and s == 1 and lastconnect == False:
                            lastconnect = True
                            continue
                        break

                    wrSettings = wr

                    if j > 2:
                        print('Не удалось подключиться на настройках ' + str(rdSettings))
                        fullstop = True
                        break

                    if j > 1:
                        print('Не удалось подключиться на настройках ' + str(rdSettings))
                        print('Выключаем питание модуля (mask = 0)')
                        #выключаем выход и включаем выход
                        result1 = write_mask_client(host='10.2.25.84', port=502, mask=0)
                        time.sleep(1)
                        print('Включаем питание модуля (mask = 1)')
                        result1 = write_mask_client(host='10.2.25.84', port=502, mask=1)

                        rdSettings = [baudSettings[wr[0]], 8, stopbitSettings[wr[2]], paritySettings[wr[3]]]
                        resetmodule = True
                        #пробуем подключение. если с последними сетевыми настройками не работает то останавливаем программу и говорим что на этих настройках нет подключения
print('Результат Modbus RTU')
print('Количество ошибок записи сетевых настроек с помощью APLY: ' + str(counterrorAply))




lastconnect = False
dataword = [7, 8]
counterrorAply = 0
if connectmodbusascii:
    print('Проверяем обмен на протоколе Modbus ASCII')
    for d in range(2): #daraword
        if fullstop:
            break
        for i in range(9): # baudrate
            if fullstop:
                break
            for s in range(2): # stopbits
                if fullstop:
                    break
                for k in range(3): # parity
                    if fullstop:
                        break

                    for j in range(5): # count connections
                        if (d == 0 and k == 0 and s == 0) or (d == 0 and k == 0 and s == 1) or (d == 0 and k == 1 and s == 1):
                            print('7 бит, 1 или 2 стоп-бит и контроль четности отсутствует не поддержаны аппаратно')
                            break

                        if start:
                            rdSettings = [defaultbaudrate, defaultdataword, defaultstopbit, defaultparity]
                            result1 = write_mask_client(host=host, port=502, mask=1)
                            if str(result1)[:12] == 'Modbus Error':
                                print('Ошибка связи с модулей по IP адресу ' + host)
                                fullstop = True
                                break
                            time.sleep(5)

                            start = False
                        elif errorConnections == False:
                            rdSettings = [baudSettings[wrSettings[0]], dataword[wrSettings[1]], stopbitSettings[wrSettings[2]], paritySettings[wrSettings[3]]]
                            pastconnect = False
                            resetmodule = False
                        elif errorConnections == True and resetmodule == False:
                            rdSettings = [baudSettings[rd[0]], dataword[rd[1]], stopbitSettings[rd[2]], paritySettings[rd[3]]]            # повторить соединение на предыдущих настройках rdSettings и wrSettings
                            pastconnect = True

                        if pastconnect == False:
                            wrSettings = [i, d, s, k]

                        print('Подключение по настройкам ' + str(rdSettings))
                        errorConnections, read = run_sync_simple_client(port='COM3', listSettings=rdSettings, listcountSettings=wrSettings, framer=ModbusAsciiFramer)

                        if errorConnections == False and pastconnect == False:
                            rd = read
                            wr = wrSettings
                            if i == 8 and k == 2 and s == 1 and lastconnect == False:
                                lastconnect = True
                                continue
                            break

                        wrSettings = wr

                        if j > 2:
                            print('Не удалось подключиться на настройках ' + str(rdSettings))
                            fullstop = True
                            break

                        if j > 1:
                            print('Не удалось подключиться на настройках ' + str(rdSettings))
                            print('Перезагружаем питание модуля')
                            #выключаем выход и включаем выход
                            result1 = write_mask_client(host='10.2.25.84', port=502, mask=0)
                            time.sleep(2)
                            result1 = write_mask_client(host='10.2.25.84', port=502, mask=1)
                            time.sleep(5)
                            rdSettings = [baudSettings[wr[0]], dataword[wr[1]], stopbitSettings[wr[2]], paritySettings[wr[3]]]
                            resetmodule = True
                            #пробуем подключение. если с последними сетевыми настройками не работает то останавливаем программу и говорим что на этих настройках нет подключения

print('Результат обмена по Modbus ASCII')
print('Количество ошибок записи сетевых настроек с помощью APLY: ' + str(counterrorAply))