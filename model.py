import numpy as np
import pandas as pd
import tensorflow as tf

trainingdata = pd.read_csv("results.csv", header=0)
testdata = trainingdata[20:25]
trainingdata = trainingdata[:20]

target="marketCap"
learningrate=.001
batchsize=20
epochs=100
l2rate=.000#15
dropoutrate=0#.1
earlyStoppingPatience=20
layersize=128
date="6_9_2022"

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