import tempfile
from pathlib import Path
import unittest
import analyze_image
from seye.learning.linear import fit
from seye.learning.prototypes import predict, save_model, load_model


class IndependentSGDTests(unittest.TestCase):
    def data(self):
        training = [{'id': 'a', 'label': 'left', 'capture_group': 'train-a', 'features': [-1., -1.]},
                    {'id': 'b', 'label': 'right', 'capture_group': 'train-b', 'features': [1., 1.]}]
        validation = [{'id': 'av', 'label': 'left', 'capture_group': 'val-a', 'features': [-.9, -.9]},
                      {'id': 'bv', 'label': 'right', 'capture_group': 'val-b', 'features': [.9, .9]}]
        return training, validation

    def test_independent_initialization_training_loss_and_determinism(self):
        training, validation = self.data()
        first, second = fit(training, validation, epochs=40), fit(training, validation, epochs=40)
        self.assertEqual(first, second)
        self.assertFalse(first['pretrained_weights_used'])
        self.assertLess(first['training_history'][-1]['training']['cross_entropy'], first['training_history'][0]['training']['cross_entropy'])
        self.assertEqual(predict(first, [-1., -1.])['label'], 'left')
        self.assertEqual(predict(first, [1., 1.])['label'], 'right')
        self.assertFalse(predict(first, [0., 0.])['accepted'])
        self.assertIsNone(predict(first, [1., 1.])['confidence_probability'])

    def test_linear_checkpoint_restore_and_incompatible_features(self):
        training, validation = self.data(); model = fit(training, validation, epochs=10)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'linear.json'; save_model(path, model)
            self.assertEqual(predict(load_model(path), [1., 1.]), predict(model, [1., 1.]))
        with self.assertRaises(ValueError):
            predict(model, [1.])

    def test_configuration_and_leakage_rejected(self):
        training, validation = self.data()
        with self.assertRaises(ValueError):
            fit(training, validation, seed=True)
        validation[0]['capture_group'] = 'train-a'
        with self.assertRaisesRegex(ValueError, 'leakage'):
            fit(training, validation)
