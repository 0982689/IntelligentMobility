from threading import Thread
from serial_port import SerialPort
from clients import RLClient, AIClient


# Make threaded class for reading the arduino via serial
class ReadAndProcess(Thread):
    def __init__(self, serial_class: SerialPort = ...) -> None:
        Thread.__init__(self)
        self.serial_class = serial_class

    # Standard run class from package thread which prints the data from the arduino
    def run(self) -> None:
        while True:
            self.serial_class.read_data()


class DriveClient(Thread):
    def __init__(self, rl_client: RLClient = ...) -> None:
        Thread.__init__(self)
        self.rl_client = rl_client

    def run(self) -> None:
        self.rl_client.start_client()
        while True:
            self.rl_client.run_with_lidar()


# 40, 200, 360
# Main starts program to read serial
if __name__ == "__main__":
    serial_arduino = SerialPort(9600)
    client = RLClient(serial_class=serial_arduino)
    drive_client = DriveClient(rl_client=client)
    read_and_process_thread = ReadAndProcess(serial_class=serial_arduino)
    drive_client.start()
    read_and_process_thread.start()
    drive_client.join()
    read_and_process_thread.join()
