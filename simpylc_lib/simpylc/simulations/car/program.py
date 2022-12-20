from threading import Thread
from clients import RLClient


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


# 40, 200, 360
# Main starts program to read serial
if __name__ == "__main__":
    # serial_arduino = SerialPort(9600)
    # read_and_process_thread = ReadAndProcess(serial_class=serial_arduino)
    # read_and_process_thread.start()
    # read_and_process_thread.join()
    client = RLClient()
    for z in range(0, 11):
        try:
            if z == 1:
                continue
            print(f"Busnum = {z}")
            client.motors.busnum = z
            for y in range (1, 16):
                client.motors.channel = y
                print(f"Busnum {z} with channel: {client.motors.channel}")
                # for x in range(100, 2000, 100):
                #     print(f"pulse: {x}")
                #     client.motors.run(x)
                client.motors.run(200)
        except:
            pass
    client.motors.run(500)
    # client.servo.run(40)
    # client = AIClient()
    # client.use_sim()
