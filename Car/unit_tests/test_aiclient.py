from unittest import TestCase, main
import pickle
import os
import matplotlib.pyplot as plt
from ..clients import AIClient

modelSaveFile = os.path.realpath('Car\\model.sav')

class TestAIClient(TestCase):
    
    def setUp(self) -> None:
        """
        Tries loading the model and otherwise creates a new one.
        """
        try:
            with open(modelSaveFile, 'rb') as file:
                self.neuralNet = pickle.load(file)
        except Exception:
            client = AIClient()
            client.train_network()
            with open(modelSaveFile, 'rb') as file:
                self.neuralNet = pickle.load(file)

    def test_best_loss(self) -> None:
        """
        Test will fail if the best loss of the model 
        is higher than the threshold specifies.
        """
        best_loss_threshold = 27.0
        best_loss = self.neuralNet.best_loss_
        self.assertLess(best_loss, best_loss_threshold)

def plot_loss():
    """
    Plots the model loss over the number of iterations it has performed
    """
    model = pickle.load(open(modelSaveFile, 'rb'))
    loss_values = model.loss_curve_
    best_loss = model.best_loss_
    iteration = loss_values.index(best_loss)
    plt.figure("Loss per iteration")
    plt.plot(loss_values, label="Loss")
    plt.plot(iteration, best_loss, 'ro', label="Best loss")
    plt.xlabel("Iterations")
    plt.ylabel("Loss")
    plt.legend()
    plt.show()
    
if __name__ == "__main__":
    plot_loss()
    main()