import time as tm
import traceback as tb
import math as mt
import sys as ss
import os
import socket as sc
import numpy as np
import time
import Adafruit_PCA9685
from Adafruit_GPIO import I2C
import simpylc_lib.simpylc.simulations.car.socket_wrapper as sw
from simpylc_lib.simpylc.simulations.car.control_client import parameters as pm
import pickle
from sklearn.neural_network import MLPRegressor

ss.path += [os.path.abspath(relPath) for relPath in ('..',)]

finity = 20.0  # Needs to be float to obtain ditto numpy array

lidar_input_dim = 15

sampleFileName = 'default.samples'

X = np.loadtxt("default.samples", delimiter=' ')

modelSaveFile = 'model.sav'


def getTargetVelocity(steeringAngle):
    return (90 - abs(steeringAngle)) / 60


class AIClient:
    def __init__(self):
        self.steeringAngle = 0

    def train_network(self):
        print("Training...")
        self.neuralNet = MLPRegressor(learning_rate_init=0.010,
                                      n_iter_no_change=2000,
                                      verbose=True,
                                      random_state=1,
                                      hidden_layer_sizes=15,
                                      max_iter=100000)
        self.neuralNet.fit(X[:, :-1], X[:, -1])
        print(self.neuralNet.best_loss_)
        pickle.dump(self.neuralNet, open(modelSaveFile, 'wb'))
        print(f"Training finished in {self.neuralNet.n_iter_} cycles.")

    def use_sim(self):
        try:
            self.neuralNet = pickle.load(open(modelSaveFile, 'rb'))
        except Exception:
            raise FileNotFoundError
        print("Loaded model.")
        with sc.socket(*sw.socketType) as self.clientSocket:
            self.clientSocket.connect(sw.address)
            self.socketWrapper = sw.SocketWrapper(self.clientSocket)
            self.halfApertureAngle = False

            while True:
                self.input()
                self.lidarSweep()
                self.output()
                tm.sleep(0.02)

    def input(self):
        sensors = self.socketWrapper.recv()

        if not self.halfApertureAngle:
            self.halfApertureAngle = sensors['halfApertureAngle']
            self.sectorAngle = 2 * self.halfApertureAngle / lidar_input_dim
            self.halfMiddleApertureAngle = sensors['halfMiddleApertureAngle']

        self.lidarDistances = sensors['lidarDistances']

    def lidarSweep(self):
        sample = [finity for eI in range(lidar_input_dim)]
        for lidarAngle in range(-self.halfApertureAngle, self.halfApertureAngle):
            sectorIndex = round(lidarAngle / self.sectorAngle)
            sample[sectorIndex] = min(sample[sectorIndex], self.lidarDistances[lidarAngle])

        lowest = sample[:]
        lowest.sort()
        lowest = lowest[:2]

        for i in range(len(sample)):
            if sample[i] not in lowest:
                sample[i] = finity

        numpySample = np.array(sample).reshape(1, -1)

        self.steeringAngle = self.neuralNet.predict(numpySample)[0]

        self.targetVelocity = getTargetVelocity(self.steeringAngle)

    def output(self):
        actuators = {
            'steeringAngle': self.steeringAngle,
            'targetVelocity': self.targetVelocity
        }

        self.socketWrapper.send(actuators)


class RLClient:
    '''
    PWM motor controler using PCA9685 boards.
    This is used for most RC Cars
    '''

    def __init__(self, channel, address=0x40, frequency=60, busnum=None, init_delay=0.1):

        self.default_freq = 60
        self.pwm_scale = frequency / self.default_freq
        # Initialise the PCA9685 using the default address (0x40).
        if busnum is not None:
            # replace the get_bus function with our own
            def get_bus():
                return busnum

            I2C.get_default_bus = get_bus
        self.pwm = Adafruit_PCA9685.PCA9685(address=address)
        self.pwm.set_pwm_freq(frequency)
        self.channel = channel
        time.sleep(init_delay)  # "Tamiya TBLE-02" makes a little leap otherwise

    def set_pulse(self, pulse):
        try:
            self.pwm.set_pwm(self.channel, 0, int(pulse * self.pwm_scale))
        except:
            self.pwm.set_pwm(self.channel, 0, int(pulse * self.pwm_scale))

    def run(self, pulse):
        self.set_pulse(pulse)