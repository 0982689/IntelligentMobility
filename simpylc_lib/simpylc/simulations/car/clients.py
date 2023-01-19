import time
import time as tm
from actuators import PWMMotors, PWMServo
import sys as ss
import os
import socket as sc
import numpy as np
import pickle
import socket_wrapper as sw
import matplotlib.pyplot as plt
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.model_selection import train_test_split
from serial_port import SerialPort

ss.path += [os.path.abspath(relPath) for relPath in ('..',)]

finity = 20.0  # Needs to be float to obtain ditto numpy array

lidar_input_dim = 15

sampleFileName = 'default.samples'

samples = np.loadtxt("default.samples", delimiter=' ')
X = samples[:, :-1]
y = samples[:, -1]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=.2, random_state=1)

scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

modelSaveFile = 'model.sav'

def getTargetVelocity(steeringAngle) -> float:
    return (90 - abs(steeringAngle)) / 60

class AIClient:
    def __init__(self) -> None:
        self.steeringAngle = 0

    def train_network(self) -> None:
        print("Training...")
        self.neuralNet = MLPRegressor(learning_rate_init=.01,
                                      solver='sgd',
                                      activation='tanh',
                                      learning_rate='adaptive',
                                      early_stopping=True,
                                      n_iter_no_change=200,
                                      verbose=True,
                                      random_state=1,
                                      hidden_layer_sizes=(136),
                                      max_iter=25000)
        self.neuralNet.fit(X_train, y_train)
        print(f"Training finished in {self.neuralNet.n_iter_} cycles.")
        y_pred = self.neuralNet.predict(X_test)
        plt.plot(y_test, 'ro', label = 'Real data')
        plt.plot(y_pred, 'bo', label = 'Predicted data')
        plt.title('Prediction')
        plt.xlabel('Items')
        plt.ylabel('Values')
        plt.legend()
        plt.show()
        with open(modelSaveFile, 'wb') as file:
            pickle.dump(self.neuralNet, file)

    def use_sim(self) -> None:
        try:
            with open(modelSaveFile, 'rb') as file:
                self.neuralNet = pickle.load(file)
        except Exception:
            raise FileNotFoundError
        print("Loaded self.neuralNet.")
        with sc.socket(*sw.socketType) as self.clientSocket:
            self.clientSocket.connect(sw.address)
            self.socketWrapper = sw.SocketWrapper(self.clientSocket)
            self.halfApertureAngle = False

            while True:
                self.input()
                self.lidarSweep()
                self.output()
                tm.sleep(0.02)

    def input(self) -> None:
        sensors = self.socketWrapper.recv()

        if not self.halfApertureAngle:
            self.halfApertureAngle = sensors['halfApertureAngle']
            self.sectorAngle = 2 * self.halfApertureAngle / lidar_input_dim
            self.halfMiddleApertureAngle = sensors['halfMiddleApertureAngle']

        self.lidarDistances = sensors['lidarDistances']

    def lidarSweep(self) -> None:
        sample = [finity for _ in range(lidar_input_dim)]
        for lidarAngle in range(-self.halfApertureAngle, self.halfApertureAngle):
            sectorIndex = round(lidarAngle / self.sectorAngle)
            sample[sectorIndex] = min(
                sample[sectorIndex], self.lidarDistances[lidarAngle])

        lowest = sample[:]
        lowest.sort()
        lowest = lowest[:2]

        for i in range(len(sample)):
            if sample[i] not in lowest:
                sample[i] = finity

        numpySample = np.array(sample).reshape(1, -1)

        self.steeringAngle = self.neuralNet.predict(numpySample)[0]

        self.targetVelocity = getTargetVelocity(self.steeringAngle)

    def output(self) -> None:
        actuators = {
            'steeringAngle': self.steeringAngle,
            'targetVelocity': self.targetVelocity
        }

        self.socketWrapper.send(actuators)

class RLClient:
    def __init__(self, serial_class: SerialPort) -> None:
        self.motors = PWMMotors()
        self.servo = PWMServo()
        self.serial_class = serial_class

    def start_client(self) -> None:
        try:
            with open(modelSaveFile, 'rb') as file:
                self.neuralNet = pickle.load(file)
        except Exception:
            raise FileNotFoundError
        print("Loaded model.")

    def run_with_lidar(self) -> None:
        array = self.serial_class.return_processed_array()
        if all(x is None for x in array):
            return
        else:
            try:
                steering_angle = self.neuralNet.predict(scaler.transform([array]))[0]
            except Exception as e:
                print(e)
                return
            print(steering_angle)
            self.servo.set_pulse(int(steering_angle))
            time.sleep(.2)
