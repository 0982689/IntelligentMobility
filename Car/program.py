from .serial_port import SerialPort
from threading import Thread


class ReadAndProcess(Thread):
    def __init__(self, serial_class):
        Thread.__init__(self)
        self.serial_class = serial_class

    def run(self):
        while True:
            self.serial_class.read_data()
            print(self.serial_class.return_processed_array())


if __name__ == "__main__":
    serial_arduino = SerialPort(9600)
    read_and_process_thread = ReadAndProcess(serial_class=serial_arduino)
    read_and_process_thread.start()
    read_and_process_thread.join()
