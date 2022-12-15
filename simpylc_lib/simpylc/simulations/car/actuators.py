import time
import Adafruit_PCA9685
from Adafruit_GPIO import I2C
from typing import Literal
from utils import map_range


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


class PWMThrottle:
    """
    Wrapper over a PWM motor controller to convert -1 to 1 throttle
    values to PWM pulses.
    """
    MIN_THROTTLE = -1
    MAX_THROTTLE = 1

    def __init__(self,
                 controller=None,
                 max_pulse=300,
                 min_pulse=490,
                 zero_pulse=350):

        self.controller = controller
        self.max_pulse = max_pulse
        self.min_pulse = min_pulse
        self.zero_pulse = zero_pulse
        self.pulse = zero_pulse

        # send zero pulse to calibrate ESC
        print("Init ESC")
        self.controller.set_pulse(self.max_pulse)
        time.sleep(0.01)
        self.controller.set_pulse(self.min_pulse)
        time.sleep(0.01)
        self.controller.set_pulse(self.zero_pulse)
        time.sleep(1)
        self.running = True
        print('PWM Throttle created')

    def update(self):
        while self.running:
            self.controller.set_pulse(self.pulse)

    def run_threaded(self, throttle):
        if throttle > 0:
            self.pulse = map_range(throttle, 0, self.MAX_THROTTLE,
                                   self.zero_pulse, self.max_pulse)
        else:
            self.pulse = map_range(throttle, self.MIN_THROTTLE, 0,
                                   self.min_pulse, self.zero_pulse)

    def run(self, throttle):
        self.run_threaded(throttle)
        self.controller.set_pulse(self.pulse)

    def shutdown(self):
        # stop vehicle
        self.run(0)
        self.running = False


# Steering channel = 12, Throttle channel = 13
class PWMServo(_PCA9685):
    def __init__(self, channel: int = 0) -> None:
        super().__init__(channel=channel)


class PWMMotors(_PCA9685):
    def __init__(self, channel: int = 1) -> None:
        super().__init__(channel=channel)
