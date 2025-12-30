import time
import select
from baseclasses.modbus_operations import ModbusFeatures, ModbusResponseMixin

class SpeOperations(ModbusResponseMixin):
    def __init__(self):
        self.modbus_features = ModbusFeatures

    # Main function that performs data writing and reading.
    def auto_request_response(self, requests, num):
        try:
            # Open the file in read/write mode without buffering.
            with open("/dev/spe", "r+b", buffering=0) as f:
                for i in range(num + 1):  # Loop with NUM + 1 iterations.
                    # Wait for the file to be ready for writing.
                    select.select([], [f.fileno()], [])

                    # If not the last iteration, write requests.
                    if i != num:
                        start_time = time.time()
                        for request in requests:
                            f.write(request)  # Write the request to the file.
                        # print(f"Added {len(requests)} new requests")  # Log the write operation.

                    # If not the first iteration, read response data.
                    if i != 0:
                        for j in range(len(requests)):
                            response_bytes = f.read(256)  # Read data from the file.
                            # Print data in hexadecimal format or a message if no data is available.
                            if not response_bytes:
                                print('no data')
                            else:
                                end_time = time.time()
                                elapsed_time = end_time - start_time
                                #print('Elapsed time: ', elapsed_time)

                                #print(self.modbus_features.parse_modbus_rtu_response([byte for byte in response_bytes]))
                                yield self.parse_modbus_response(response_bytes)

                                #yield tuple(self.modbus_features.parse_modbus_rtu_response([byte for byte in response_bytes]))				

        except OSError as e:  # Handle file operation errors.
            print(f"Error: {e.strerror} ({e.errno})")