from turtle import distance
from serialPort import serialPort
from serial.tools.list_ports import comports
from threading import Thread
from queue import Queue

for port in comports():
    print(port)

ser = serialPort(port[0], 9600, timeout=1)
arduino_list = []
queue = Queue()

class SerialReaderThread(Thread):
    def run(self):
        while True:
            line = (ser.readline().decode())
            queue.put(line)

class LineWriterThread(Thread):
    def run(self):
        while True:
            line = queue.get()
            dist, angle = line.split(',')
            arduino_dict = {"angle": angle, "distance": dist}
            arduino_list.append(arduino_dict)
 
serial_reader_thread = SerialReaderThread()
line_writer_thread = LineWriterThread()

serial_reader_thread.start()
line_writer_thread.start()

serial_reader_thread.join()
line_writer_thread.join()

test = arduino_list

