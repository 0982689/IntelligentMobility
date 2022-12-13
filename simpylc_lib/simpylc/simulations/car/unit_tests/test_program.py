from unittest import TestCase, main
from simpylc_lib.simpylc.simulations.car.program import ReadAndProcess
from simpylc_lib.simpylc.simulations.car.serial_port import SerialPort

serial_port = SerialPort(9600)
connected = serial_port.open_port.is_open


class TestProgram(TestCase):

    def setUp(self) -> None:
        """
        Instantiating the SerialPort class and 
        starting the read and process thread for tests.
        """
        if not connected:
            # Skips all the tests inside this class
            self.skipTest("Could not connect to comport.")
        read_and_process_thread = ReadAndProcess(serial_class=serial_port)
        read_and_process_thread.start()
        read_and_process_thread.join()

    def test_processed_array_not_none(self) -> None:
        """
        Test will fail if None is in processed array, which means
        that we do not get Lidar info
        """
        self.assertNotIn(None, serial_port.processed_array)

    def test_processed_array_none(self) -> None:
        """
        Test will succeed if None is in processed array, which means
        that we do not get Lidar info
        """
        self.assertIn(None, serial_port.processed_array)


if __name__ == "__main__":
    main()
