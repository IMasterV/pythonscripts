from dataclasses import dataclass, asdict, field
from typing import Any, Optional

@dataclass
class ModbusField:
    addr: int
    count: int
    value: Optional[Any] = None

@dataclass
class System:
    name = ModbusField(addr=0x0000, count=16)
    firmware_ver = ModbusField(addr=0x0010, count=8)
    hardware_ver = ModbusField(addr=0x0018, count=8)
    module_position = ModbusField(addr=0x0020, count=8)
    system_time = ModbusField(addr=0x0030, count=2) #count = 2?
    fsm_current_state = ModbusField(addr=0x0102, count=1)
    fsm_control_state = ModbusField(addr=0x0103, count=1)
    fsm_status = ModbusField(addr=0x0104, count=1)
    so_timeout = ModbusField(addr=0x0110, count=1)
    restart = ModbusField(addr=0x0180, count=1)