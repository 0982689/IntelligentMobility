from serial import Serial
from serial.tools.list_ports import comports
from typing import Union, List


def find_open_port() -> Union[None, str]:
    ports = list(comports())
    for port in ports:
        return port[0]


class SerialPort:
    def __init__(self, baud) -> None:
        port = find_open_port()
        self.processed_array = [None] * 15
        self.open_port = Serial(port, baud, timeout=.1)
        print(f"connected to: {self.open_port.portstr}")

    def send_data(self, data) -> None:
        self.open_port.write(data)

    def read_data(self) -> None:
        """
        Reads unprocessed data and converts it into processed data.
        Processed array gets assigned.
        """
        if self.open_port.port != None and self.open_port.in_waiting > 0:
            unprocessed_data = str(self.open_port.readline()[:-2], 'utf-8')
        else:
            return

        temp_data = unprocessed_data.split(",")
        try:
            temp_data = [int(string_int) for string_int in temp_data]
            self.processed_array = temp_data
        except Exception as e:
            print(e)

    def return_processed_array(self) -> Union[List[None], List[int]]:
        """
        Returns processed array.
        """
        print(self.processed_array)
        return self.processed_array


if __name__ == "__main__":
    serial = SerialPort(9600)
    while True:
        print(serial.read_data())
