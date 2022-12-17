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
from sklearn.model_selection import GridSearchCV, cross_val_score, cross_validate

ss.path += [os.path.abspath(relPath) for relPath in ('..',)]

finity = 20.0  # Needs to be float to obtain ditto numpy array

lidar_input_dim = 15

sampleFileName = 'default.samples'

samples = np.loadtxt("default.samples", delimiter=' ')
X = samples[:, :-1]
Y = samples[:, -1]

modelSaveFile = 'tempmodel.sav'#'model.sav'


def getTargetVelocity(steeringAngle) -> float:
    return (90 - abs(steeringAngle)) / 60

def normalize_data() -> None:
    global X
    scaler = MinMaxScaler()
    X = scaler.fit_transform(X)

class AIClient:
    def __init__(self) -> None:
        self.steeringAngle = 0

    def train_network(self) -> None:
        print("Training...")
        normalize_data()
        self.neuralNet = MLPRegressor(learning_rate_init=.01,
                                      n_iter_no_change=2000,
                                      learning_rate='constant',
                                      activation='tanh',
                                      verbose=True,
                                      alpha=0.05,
                                      random_state=1,
                                      hidden_layer_sizes=(50, 100, 50),
                                      max_iter=30000)
        self.neuralNet.fit(X, Y)
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
        
    def tune_hyperparameters(self) -> None:
        """
        Used to find the best parameters for tuning the neural network.
        """
        network = MLPRegressor()
        param_grid = {
            'hidden_layer_sizes': [(50,100,50)],
            'activation': ['relu','tanh','logistic'],
            'learning_rate_init': [.01, .015, .02],
            'alpha': [.01, .025, .05],
            'learning_rate': ['constant','adaptive'],
            'solver': ['adam'],
            'max_iter': [30000],
            'n_iter_no_change': [1000]
        }

        gsc = GridSearchCV(network,
                           param_grid,
                           cv=2, 
                           scoring='neg_mean_squared_error', 
                           verbose=1, 
                           n_jobs=-1)
        
        grid_result = gsc.fit(X, Y)
        best_params = grid_result.best_params_

        best_mlp = MLPRegressor(hidden_layer_sizes = best_params["hidden_layer_sizes"], 
                                activation = best_params["activation"],
                                verbose = True,
                                learning_rate = best_params['learning_rate'],
                                alpha = best_params['alpha'],
                                solver = best_params["solver"],
                                max_iter = 30000,
                                n_iter_no_change = 1000
        )
        scoring = {
            'abs_error': 'neg_mean_absolute_error',
            'squared_error': 'neg_mean_squared_error',
            'r2':'r2'
        }
        scores = cross_validate(best_mlp, X, Y, cv=2, scoring=scoring, return_train_score=True, return_estimator = True)
        print(best_params)
        print(scores)
    
    def plot_loss(self) -> None:
        """
        Plots the model loss over the number of iterations it has performed.
        If a model is not found, it wil create a new one.
        """
        try:
            with open(modelSaveFile, 'rb') as file:
                self.neuralNet : MLPRegressor = pickle.load(file)
        except Exception:
            self.train_network()
            with open(modelSaveFile, 'rb') as file:
                self.neuralNet : MLPRegressor = pickle.load(file)
            
        loss_values = self.neuralNet.loss_curve_
        best_loss = self.neuralNet.best_loss_
        best_loss_iteration = loss_values.index(best_loss)
        r2_score = cross_val_score(self.neuralNet, X, Y, cv=5, scoring='r2')
        print(r2_score)
        plt.figure("Loss per iteration")
        plt.subplot(2, 1, 1)
        plt.plot(loss_values, label="Loss")
        plt.plot(best_loss_iteration, best_loss, 'ro', label=f"Best loss: {round(best_loss, 2)}")
        plt.xlabel("Iterations")
        plt.ylabel("Loss")
        plt.legend()
        plt.show()

class RLClient:
    def __init__(self) -> None:
        self.motors = PWMMotors()
        self.servo = PWMServo()
