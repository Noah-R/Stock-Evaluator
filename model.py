import numpy as np
import pandas as pd
import tensorflow as tf

trainingdata = pd.read_csv("results.csv", header=0)
testdata = trainingdata[24:]
trainingdata = trainingdata[:24]


target="marketCap"
learningrate=.001
batchsize=30
epochs=20
l2rate=.00015
dropoutrate=0.1
earlyStoppingPatience=10
layersize=64
date="6_8_2022"

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
    tf.keras.layers.Dense(units=1, activation=tf.sigmoid, name="Output")
])

model.compile(
    optimizer=tf.keras.optimizers.RMSprop(learning_rate=learningrate),
    loss=tf.keras.losses.BinaryCrossentropy(),
    metrics=["mse"]
)

features = {name: np.array(value) for name, value in trainingdata.items()}
label = np.array(features.pop(target))

testfeatures = {name: np.array(value) for name, value in testdata.items()}
testlabel = np.array(testfeatures.pop(target))

tensorboardCallback = tf.keras.callbacks.TensorBoard(log_dir="models/tensorboard_"+date, histogram_freq=1)
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

model.save("models/model_"+date)