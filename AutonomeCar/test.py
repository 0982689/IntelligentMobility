import serialPort
import threading
import time
import serial.tools.list_ports

ports = list(serial.tools.list_ports.comports())
for p in ports:
    print(p)

arduino = serialPort.serialPort(p[0], 9600)
t1 = threading.Thread(target=arduino.read_data)
t1.start()
while True:
    time.sleep(1)
    print(arduino.message)
