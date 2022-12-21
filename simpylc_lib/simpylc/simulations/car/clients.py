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
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score
from serial_port import SerialPort

ss.path += [os.path.abspath(relPath) for relPath in ('..',)]

finity = 20.0  # Needs to be float to obtain ditto numpy array

lidar_input_dim = 15

sampleFileName = 'default.samples'

samples = np.loadtxt("default.samples", delimiter=' ')
X = samples[:, :-1]
Y = samples[:, -1]
x_train, x_test, y_train, y_test = train_test_split(X, Y, test_size=.2, random_state=1)

modelSaveFile = 'model.sav'

def getTargetVelocity(steeringAngle) -> float:
    return (90 - abs(steeringAngle)) / 60

def normalize_data() -> None:
    global x_train_nor, x_test_nor
    scaler = MinMaxScaler()
    x_train_nor = scaler.fit_transform(x_train)
    x_test_nor = scaler.transform(x_test)

class AIClient:
    def __init__(self) -> None:
        self.steeringAngle = 0

    def train_network(self) -> None:
        print("Training...")
        normalize_data()
        self.neuralNet = MLPRegressor(learning_rate_init=.01,
                                      n_iter_no_change=2000,
                                      verbose=True,
                                      random_state=1,
                                      hidden_layer_sizes=(100,50),
                                      max_iter=20000)
        self.neuralNet.fit(x_train_nor, y_train)
        pickle.dump(self.neuralNet, open(modelSaveFile, 'wb'))
        print(f"Training finished in {self.neuralNet.n_iter_} cycles.")

    def use_sim(self) -> None:
        try:
            with open(modelSaveFile, 'rb') as file:
                self.neuralNet = pickle.load(file)
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

    def plot_loss(self) -> None:
        """
        Plots the model loss over the number of iterations it has performed.
        If a model is not found, it wil create a new one.
        """
        try:
            with open(modelSaveFile, 'rb') as file:
                normalize_data()
                self.neuralNet: MLPRegressor = pickle.load(file)
        except Exception:
            self.train_network()
            with open(modelSaveFile, 'rb') as file:
                self.neuralNet: MLPRegressor = pickle.load(file)

        loss_values = self.neuralNet.loss_curve_
        best_loss = self.neuralNet.best_loss_
        best_loss_iteration = loss_values.index(best_loss)
        print(f"r2 score: {r2_score(y_test, self.neuralNet.predict(x_test_nor))}")
        plt.figure("Loss per iteration")
        plt.plot(loss_values, label="Loss")
        plt.plot(best_loss_iteration, best_loss, 'ro', label=f"Best loss: {round(best_loss, 2)}")
        plt.xlabel("Iterations")
        plt.ylabel("Loss")
        plt.legend()
        plt.show()

class RLClient:
    def __init__(self, serial_class: SerialPort) -> None:
        self.motors = PWMMotors()
        self.servo = PWMServo()
        self.serial_class = serial_class
        self.neural_net_rl = ...

    def start_client(self) -> None:
        try:
            with open(modelSaveFile, 'rb') as file:
                self.neural_net_rl = pickle.load(file)
        except Exception:
            raise FileNotFoundError
        print("Loaded model.")

    def run_with_lidar(self) -> None:
        array = self.serial_class.return_processed_array()
        if all(x is None for x in array):
            return
        else:
            try:
                steering_angle = self.neural_net_rl.predict([array])[0]
            except Exception as e:
                print(e)
                return
            print(steering_angle)
            self.servo.set_pulse(int(steering_angle))
            time.sleep(.2)
