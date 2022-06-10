import numpy as np
import pandas as pd
import tensorflow as tf

fileName = 'models\model_6_9_2022'

model = tf.keras.models.load_model(fileName)

data = pd.read_csv("results.csv", header=0)[25:]

target="marketCap"

features = {name: np.array(value) for name, value in data.items()}
label = np.array(features.pop(target))

preds = model.predict(x=features, verbose=1)
input()
model.evaluate(x=features, y=label, verbose=1)
input()
for i in range(len(preds)):
    print("Predicted "+str(preds[i])+" for actual value "+str(label[i]))