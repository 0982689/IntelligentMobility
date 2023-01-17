import time
import Adafruit_PCA9685
from Adafruit_GPIO import I2C
from typing import Literal


class _PCA9685:
    def __init__(self, channel, address=0x40, frequency=60, busnum=None, init_delay=0.1) -> None:
        self.default_freq = 45
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
        self.pwm.set_pwm(self.channel, 0, int(self._map_servo_pulse(pulse) * self.pwm_scale))

    # -35, 35 || 40, 360
    @staticmethod
    def _map_servo_pulse(pulse: int) -> int:
        return int((pulse - (-35)) * (360 - 40) / (35 - (-35)) + 40)


# Steering channel = 12, Throttle channel = 13
class PWMServo(_PCA9685):
    def __init__(self, channel: int = 0) -> None:
        super().__init__(channel=channel, busnum=1)


class PWMMotors(_PCA9685):
    def __init__(self, channel: int = 1) -> None:
        super().__init__(channel=channel, busnum=1)
