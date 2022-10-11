import serial


class SerialPort:
    message = ''

    def __init__(self, baud):
        ports = list(serial.tools.list_ports.comports())
        for p in ports:
            print(p)
        self.port = serial.Serial(port, baud, timeout=.1)
        print("connected to: " + self.port.portstr)
        if not self.port.isOpen():
            self.port.open()
            print("connected to: " + self.port.portstr)

    def port_open(self):
        if not self.port.isOpen():
            self.port.open()
            print("connected to: " + self.port.portstr)

    def port_close(self):
        self.port.close()

    def send_data(self, data):
        number = self.port.write(data)
        return number

    def read_data(self):
        if self.port.in_waiting > 0:
            data = self.port.readline()[:-2]
            decoded_data = str(data, 'utf-8')
            # print(decodedData)
            self.message = decodedData
