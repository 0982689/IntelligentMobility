from actuators import PWMMotors, PWMServo


class RLClient:
    def __init__(self) -> None:
        self.motors = PWMMotors()
        self.servo = PWMServo()
