import numpy as np
import pandas as pd
import tensorflow as tf
import datetime

def trainModel(trainingdata, testdata, target, learningrate, batchsize, epochs, l2rate, dropoutrate, earlyStoppingPatience, layersize, date):
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

    tensorboardCallback = tf.keras.callbacks.TensorBoard(log_dir="models/tensorboard-"+date, histogram_freq=1)
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

    model.save("models/model-"+date)

trainingdata = pd.read_csv("results.csv", header=0)
trainingdata.drop(columns="price_future", inplace=True)
#trainingdata = trainingdata.sample(frac=1, random_state=1).reset_index()#uncomment to shuffle before split
testdata = trainingdata[80:100]
trainingdata = trainingdata[:80]

target = "price_label"
learningrate = .00001
batchsize = 80
epochs = 100
l2rate = .00015
dropoutrate = 0.1
earlyStoppingPatience = 20
layersize = 192
date = str(datetime.date.today())

trainModel(trainingdata, testdata, target, learningrate, batchsize, epochs, l2rate, dropoutrate, earlyStoppingPatience, layersize, date)