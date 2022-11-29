from .serial_port import SerialPort
from threading import Thread
from clients import AIClient, RLClient


# Make threaded class for reading the arduino via serial
class ReadAndProcess(Thread):
    def __init__(self, serial_class):
        Thread.__init__(self)
        self.serial_class = serial_class

    # Standard run class from package thread which prints the data from the aruino
    def run(self):
        while True:
            self.serial_class.read_data()
            print(self.serial_class.return_processed_array())


# Main starts program to read serial
if __name__ == "__main__":
    # serial_arduino = SerialPort(9600)
    # read_and_process_thread = ReadAndProcess(serial_class=serial_arduino)
    # read_and_process_thread.start()
    # read_and_process_thread.join()
    # controller = PCA9685(channel=1)
    # controller.run(1)
    client = AIClient()
    client.use_sim()
