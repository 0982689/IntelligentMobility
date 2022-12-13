from unittest import TestCase, main
import pickle
import os
from ..clients import AIClient

modelSaveFile = os.path.realpath('driving_class\\model.sav')

"""
Run with pytest
"""
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
    
if __name__ == "__main__":
    main()