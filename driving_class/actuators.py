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

    def set_pulse(self, pulse) -> None:
        # try:
        #     self.pwm.set_pwm(self.channel, 0, int(pulse * self.pwm_scale))
        # except:
        #     self.pwm.set_pwm(self.channel, 0, int(pulse * self.pwm_scale))
        self.pwm.set_pwm(self.channel, 0, int(pulse * self.pwm_scale))
        
    def run(self, pulse) -> None:
        self.set_pulse(pulse)


class PWMServo(_PCA9685):
    def __init__(self, channel: int = 0) -> None:
        super().__init__(channel=channel)


class _PWMMotorLeft(_PCA9685):
    def __init__(self, channel: int = 1) -> None:
        super().__init__(channel=channel)


class _PWMMotorRight(_PCA9685):
    def __init__(self, channel: int = 2) -> None:
        super().__init__(channel=channel)


class PWMMotors:
    def __init__(self) -> None:
        self.motor_right = _PWMMotorRight()
        self.motor_left = _PWMMotorLeft()

    def set_pulse(self, pulse) -> None:
        self.motor_left.set_pulse(pulse=pulse)
        self.motor_right.set_pulse(pulse=pulse)