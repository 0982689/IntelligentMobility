import time as tm
import traceback as tb
import math as mt
from actuators import PWMMotors, PWMServo
import sys as ss
import os
import socket as sc
import numpy as np
import pickle
from sklearn.neural_network import MLPRegressor

ss.path += [os.path.abspath(relPath) for relPath in ('..',)]

finity = 20.0  # Needs to be float to obtain ditto numpy array

lidar_input_dim = 15

sampleFileName = 'default.samples'

X = np.loadtxt("default.samples", delimiter=' ')

modelSaveFile = 'model.sav'


def getTargetVelocity(steeringAngle) -> float:
    return (90 - abs(steeringAngle)) / 60



class RLClient:
    def __init__(self) -> None:
        self.motors = PWMMotors()
        self.servo = PWMServo()
