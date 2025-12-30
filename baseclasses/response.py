from baseclasses.modbus_operations import ModbusFeatures, ModbusRequest
from baseclasses.spe_operations import SpeOperations


class SpeWriteRead:
    def __init__(self, device_address):
        self.device_address = device_address
        self.rr = SpeOperations()

        self.requests_count = 0
        self.errors_count = 0

    def write_data(self, wr_registers, data):
        self.requests_count += 1

        try:
            my_request = ModbusRequest(self.device_address, wr_registers).generate_modbus_write_request(data)
            response = tuple(self.rr.auto_request_response(requests=[my_request], num=1))[0]

            return response
        except IndexError:
            self.errors_count += 1

        return None
        # myrequest2 = ModbusFeatures.create_modbus_rtu_request(device_address=self.device_address,
        #                                                       function_code=0x10,
        #                                                       register_address=wr_registers,
        #                                                       data_count=data)
        #
        # response = tuple(self.rr.auto_request_response(requests=[bytes(myrequest2)], num=1))
        #print(response)

    def read_data(self, rd_registers, count, num=1):
        self.requests_count += 1

        try:
            my_request = ModbusRequest(self.device_address, rd_registers).generate_modbus_read_request(count)
            response = tuple(self.rr.auto_request_response(requests=[my_request], num=num))[0]

            return response
        except IndexError:
            self.errors_count += 1

        return None
        # myrequest1 = ModbusFeatures.create_modbus_rtu_request(device_address=self.device_address,
        #                                                       function_code=0x03,
        #                                                       register_address=rd_registers,
        #                                                       data_count=count)
        #
        # # num = 1 -> [0]
        # response = tuple(self.rr.auto_request_response(requests=[bytes(myrequest1)], num=1))[0]
