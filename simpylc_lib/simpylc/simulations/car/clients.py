import time
import time as tm
from actuators import PWMMotors, PWMServo
import sys as ss
import os
import socket as sc
import numpy as np
import pickle
import socket_wrapper as sw
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt
from serial_port import SerialPort

ss.path += [os.path.abspath(relPath) for relPath in ('..',)]

finity = 20.0  # Needs to be float to obtain ditto numpy array

lidar_input_dim = 15

sampleFileName = 'default.samples'

X = np.loadtxt("default.samples", delimiter=' ')

modelSaveFile = 'model.sav'


def getTargetVelocity(steeringAngle) -> float:
    return (90 - abs(steeringAngle)) / 60

def normalize_data() -> None:
    scaler = MinMaxScaler()
    X[:, :-1] = scaler.fit_transform(X[:, :-1])

class AIClient:
    def __init__(self) -> None:
        self.steeringAngle = 0

    def train_network(self) -> None:
        print("Training...")
        normalize_data()
        self.neuralNet = MLPRegressor(learning_rate_init=0.01,
                                      learning_rate='constant',
                                      n_iter_no_change=1000,
                                      verbose=True,
                                      random_state=1,
                                      hidden_layer_sizes=150,
                                      max_iter=100000)
        self.neuralNet.fit(X[:, :-1], X[:, -1])
        print(self.neuralNet.best_loss_)
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
                self.neuralNet = pickle.load(file)
        except Exception:
            self.train_network()
            with open(modelSaveFile, 'rb') as file:
                self.neuralNet = pickle.load(file)
            
        loss_values = self.neuralNet.loss_curve_
        best_loss = self.neuralNet.best_loss_
        best_loss_iteration = loss_values.index(best_loss)
        plt.figure("Loss per iteration")
        plt.plot(loss_values, label="Loss")
        plt.plot(best_loss_iteration, best_loss, 'ro', label=f"Best loss ({round(best_loss, 2)})")
        plt.xlabel("Iterations")
        plt.ylabel("Loss")
        plt.legend()
        plt.show()


class RLClient:
    def __init__(self,
                 serial_class: SerialPort) -> None:
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

    def run_with_lidar(self):
        steering_angle = self.neural_net_rl.predict(self.serial_class.return_processed_array())
        self.servo.set_pulse(int(steering_angle))
        time.sleep(.2)
