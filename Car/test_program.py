from unittest import TestCase, main
from program import ReadAndProcess
from serial_port import SerialPort

serialPort = SerialPort(9600)
read_and_process_thread = ReadAndProcess(serial_class=serialPort)

class TestProgram(TestCase):
    
    def setUp(self) -> None:
        read_and_process_thread.start()
        read_and_process_thread.join()
    
    def test_processed_array(self):
        self.assertNotIn(None, serialPort.processed_array)
          
if __name__ == "__main__":
    main()
        