import numpy as np
from train import train_model, get_model_metrics
import pytest


@pytest.mark.skip(reason="TODO: test simple Keras model")
def test_train_model():
    X_train = np.array([1, 2, 3, 4, 5, 6]).reshape(-1, 1)
    y_train = np.array([10, 9, 8, 8, 6, 5])
    data = {"train": {"X": X_train, "y": y_train}}

    reg_model = train_model(data, {"alpha": 1.2})

    preds = reg_model.predict([[1], [2]])
    np.testing.assert_almost_equal(preds, [9.93939393939394, 9.03030303030303])


def test_get_model_metrics():

    class MockHistory:

        history = {
                    'loss': [1.5012110471725464, 0.6115774512290955],
                    'accuracy': [0.5195071697235107, 0.7885010242462158],
                    'val_loss': [0.6773713827133179, 0.5661255717277527],
                    'val_accuracy': [0.7746031880378723, 0.8095238208770752]
        }

    metrics = get_model_metrics(MockHistory())

    assert 'loss' in metrics
    mse = metrics['loss']
    np.testing.assert_almost_equal(mse, 0.6115774512290955)
