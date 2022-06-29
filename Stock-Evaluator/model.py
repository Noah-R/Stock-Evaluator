import numpy as np
import pandas as pd
import tensorflow as tf
import datetime

def trainModel(trainingdata, testdata, target, learningrate, batchsize, epochs, l2rate, dropoutrate, earlyStoppingPatience, layersize, modelName = str(datetime.date.today())):
    """Trains predictive model

    :param trainingdata: Dataset to learn from
    :type trainingdata: pandas.DataFrame
    :param testdata: Dataset to validate with
    :type testdata: pandas.DataFrame
    :param target: Name of column to predict
    :type target: str
    :param learningrate: Learning rate of model
    :type learningrate: float
    :param batchsize: Batch size for gradient descent
    :type batchsize: int
    :param epochs: Maximum number of epochs
    :type epochs: int
    :param l2rate: L2 regularization rate
    :type l2rate: float
    :param dropoutrate: Dropout regularization rate
    :type dropoutrate: float
    :param earlyStoppingPatience: Number of epochs without improvement to allow before stopping
    :type earlyStoppingPatience: int
    :param layersize: Number of nodes in each model layer
    :type layersize: int
    :param modelName: Unique identifier to write to file names, defaults to current date as "yyyy-mm-dd"
    :type modelName: str
    """
    features=[]

    for col in trainingdata.keys():
        if(col!=target):
            features.append(tf.feature_column.numeric_column(col))

    model = tf.keras.models.Sequential([
        tf.keras.layers.DenseFeatures(features),
        tf.keras.layers.Dense(units=layersize, activation='relu', kernel_regularizer=tf.keras.regularizers.l2(l=l2rate), name='Hidden1'),
        tf.keras.layers.Dropout(rate=dropoutrate),
        tf.keras.layers.Dense(units=layersize, activation='relu', kernel_regularizer=tf.keras.regularizers.l2(l=l2rate), name='Hidden2'),
        tf.keras.layers.Dropout(rate=dropoutrate),
        tf.keras.layers.Dense(units=1, activation='linear', name="Output")
    ])

    model.compile(
        optimizer=tf.keras.optimizers.RMSprop(learning_rate=learningrate),
        loss=tf.keras.losses.MeanSquaredError(),
        metrics=["mse"]
    )

    features = {name: np.array(value) for name, value in trainingdata.items()}
    label = np.array(features.pop(target))

    testfeatures = {name: np.array(value) for name, value in testdata.items()}
    testlabel = np.array(testfeatures.pop(target))

    tensorboardCallback = tf.keras.callbacks.TensorBoard(log_dir="models/tensorboard-"+modelName, histogram_freq=1)
    earlyStoppingCallback = tf.keras.callbacks.EarlyStopping(patience=earlyStoppingPatience, verbose=1, restore_best_weights=True)

    model.fit(
        x = features,
        y = label,
        batch_size = batchsize,
        epochs = epochs,
        shuffle = False,
        verbose = 2,
        validation_data = (testfeatures, testlabel), 
        callbacks=[tensorboardCallback, earlyStoppingCallback]
    )

    model.save("models/model-"+modelName)