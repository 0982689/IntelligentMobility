from serial_port import SerialPort
from threading import Thread
import json


class ReadAndProcess(Thread):
    def __init__(self, serial_class):
        Thread.__init__(self)
        self.serial_class = serial_class

    def run(self):
        while True:
            self.serial_class.read_data()


class WriteJsonToFile(Thread):
    def __init__(self, json_loc, serial_class):
        Thread.__init__(self)
        self.json_location = json_loc
        self.serial_class = serial_class

    def run(self):
        while True:
            serial_array = self.serial_class.return_processed_array()
            json_dict = {}
            for index in range(15):
                json_dict.update({index: serial_array[index]})
            json_string = json.dumps(json_dict)
            json_file = open("data.json", "w")
            json_file.write(json_string)
            json_file.close()

if __name__ == "__main__":
    serial_arduino = SerialPort(9600)
    json_location = "../"
    read_and_process_thread = ReadAndProcess(serial_class=serial_arduino)
    write_json_file = WriteJsonToFile(json_loc=json_location, serial_class=serial_arduino)
    read_and_process_thread.start()
    write_json_file.start()
    read_and_process_thread.join()
    write_json_file.join()
