import serial
import serial.tools.list_ports
from typing import Union, List


# 150 degrees : 10 = 15 angles. array 14

def find_open_port():
    ports = list(serial.tools.list_ports.comports())
    for port in ports:
        return port[0]


class SerialPort:
    def __init__(self, baud):
        port = find_open_port()
        self.processed_array = [None] * 15
        self.open_port = serial.Serial(port, baud, timeout=.1)
        print("connected to: " + self.open_port.portstr)

    def send_data(self, data):
        self.open_port.write(data)

    def read_data(self):
        if self.open_port.in_waiting > 0:
            unprocessed_data = str(self.open_port.readline()[:-2], 'utf-8')
        else:
            return

        temp_data = unprocessed_data.split(",")
        for idx, string_int in enumerate(temp_data):
            temp_data[idx] = int(string_int)

        self.processed_array = temp_data

    def return_processed_array(self) -> Union[List[None], List[int]]:
        """
        Returns processed array
        """
        return self.processed_array


if __name__ == "__main__":
    serial = SerialPort(9600)
    while True:
        print(serial.read_data())
