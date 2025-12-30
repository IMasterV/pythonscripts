from dataclasses import dataclass, asdict, field
from typing import Any, Optional

@dataclass
class ModbusField:
    addr: int
    count: int
    value: Optional[Any] = None

# field позволяет создавать объект с отдельными экземплярами
@dataclass
class Parameters:
    do1: ModbusField = field(default_factory=lambda: ModbusField(addr=0x0000, count=1))
    do2: ModbusField = field(default_factory=lambda: ModbusField(addr=0x0001, count=1))
    in1: ModbusField = field(default_factory=lambda: ModbusField(addr=0x0002, count=1))
    in2: ModbusField = field(default_factory=lambda: ModbusField(addr=0x0003, count=1))

    time: ModbusField = field(default_factory=lambda: ModbusField(addr=0x0004, count=2))
    m210_errors: ModbusField = field(default_factory=lambda: ModbusField(addr=0x0006, count=1))
    m210_requests: ModbusField = field(default_factory=lambda: ModbusField(addr=0x0007, count=1))
    m210_reconnects: ModbusField = field(default_factory=lambda: ModbusField(addr=0x0008, count=1))

    m510_time: ModbusField = field(default_factory=lambda: ModbusField(addr=0x0009, count=2))
    m510_errors: ModbusField = field(default_factory=lambda: ModbusField(addr=0x000B, count=1))
    m510_requests: ModbusField = field(default_factory=lambda: ModbusField(addr=0x000C, count=1))
    m510_reconnect: ModbusField = field(default_factory=lambda: ModbusField(addr=0x000D, count=1)) # отсутствует

    m110_1_value: ModbusField = field(default_factory=lambda: ModbusField(addr=0x000E, count=4))
    m110_1_errors: ModbusField = field(default_factory=lambda: ModbusField(addr=0x0012, count=1))
    m110_1_requests: ModbusField = field(default_factory=lambda: ModbusField(addr=0x0013, count=1))
    m110_1_reconnects: ModbusField = field(default_factory=lambda: ModbusField(addr=0x0014, count=1))


    #hardware_ver = ModbusField(addr=0x0018, count=8)

