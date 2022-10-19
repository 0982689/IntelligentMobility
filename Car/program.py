from serial_port import SerialPort
from threading import Thread
import json
from proto_dict import Dictionary



class ReadAndProcess(Thread):
    def __init__(self, serial_class):
        Thread.__init__(self)
        self.serial_class = serial_class

    def run(self):
        while True:
            self.serial_class.read_data()


class WriteJsonToFile(Thread):
    def __init__(self, serial_class):
        Thread.__init__(self)
        self.serial_class = serial_class

    def run(self):
        while True:
            serial_array = self.serial_class.return_processed_array()
            json_dict = {index: value for index, value in enumerate(serial_array)}
            json_string = json.dumps(json_dict)
            json_file = open("data.json", "w")
            json_file.write(json_string)
            json_file.close()
            print(json_dict)
         
            
class WriteProtobufToBinFile(Thread):
    def __init__(self, serial_class):
        Thread.__init__(self)
        self.serial_class = serial_class
        
    def run(self):
        while True:
            serial_array = self.serial_class.return_processed_array()
            proto_dict = {index: value for index, value in enumerate(serial_array)}
            message = Dictionary(pairs=proto_dict)
            serialized_msg = Dictionary.serialize(message)
            with open("Car/proto.bin", "wb") as output:
                output.write(serialized_msg)
            
            #with open("Car/proto.bin", "rb") as output: Example of reading a binary protobuf
            #    serialized_msg = output.read()
            #    message = Dictionary.deserialize(serialized_msg)
            #    print(message.pairs[0]) Outputs distance at index 0. dict(message.pairs)[0] to make it a dict
            

if __name__ == "__main__":
    serial_arduino = SerialPort(9600)
    read_and_process_thread = ReadAndProcess(serial_class=serial_arduino)
    write_json_file = WriteJsonToFile(serial_class=serial_arduino)
    read_and_process_thread.start()
    write_json_file.start()
    read_and_process_thread.join()
    write_json_file.join()
