import time
import Adafruit_PCA9685
from Adafruit_GPIO import I2C
from typing import Literal


class _PCA9685:
    def __init__(self, channel, address=0x40, frequency=60, busnum=None, init_delay=0.1) -> None:
        self.default_freq = 60
        self.pwm_scale = frequency / self.default_freq
        if busnum is not None:
            def get_bus() -> Literal[0, 1]:
                return busnum

            I2C.get_default_bus = get_bus
        self.pwm = Adafruit_PCA9685.PCA9685(address=address)
        self.pwm.set_pwm_freq(frequency)
        self.channel = channel
        time.sleep(init_delay)

    def set_pulse(self, pulse: int) -> None:
        """
        Set the pulse of the servo or motors.

        :param pulse: Pulse which gets used by the servo or motor
        :return: None
        """
        self.pwm.set_pwm(self.channel, 0, int(self._map_servo_pulse(pulse) * self.pwm_scale))

    @staticmethod
    def _map_servo_pulse(pulse: int, min_input=-35, min_output=40, max_input=35, max_output=360) -> int:
        """
        Map steering pulse from output of the neural network,
        to a pulse which has the same steering angle on the vehicle.

        :param pulse: pulse generated from the neural network
        :param min_input: minimal input pulse from the neural network
        :param min_output: minimal output pulse for the vehicle
        :param max_input: maximum input pulse from the neural network
        :param max_output: maximum output pulse for the vehicle
        :return:  Return the mapped pulse as int
        """
        return int((pulse - min_input) * (max_output - min_output) / (max_input - min_input) + min_output)


# Steering channel = 0, Throttle channel = 1
class PWMServo(_PCA9685):
    def __init__(self, channel: int = 0) -> None:
        super().__init__(channel=channel, busnum=1)


class PWMMotors(_PCA9685):
    def __init__(self, channel: int = 1) -> None:
        super().__init__(channel=channel, busnum=1)
