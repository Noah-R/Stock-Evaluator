import numpy as np
import pandas as pd
import tensorflow as tf
import datetime

def predict(model, data, target):
    features = {name: np.array(value) for name, value in data.items()}
    label = np.array(features.pop(target))

    preds = model.predict(x=features, verbose=1)
    #model.evaluate(x=features, y=label, verbose=1)
    for i in range(len(preds)):
        pred = preds[i][0]
        actual = label[i]
        ratio = round(pred/actual, 2)
        print("Predicted "+str(pred)+" for actual value "+str(actual)+", prediction was "+str(ratio)+"x the actual value")

fileName = 'models\model-'+str(datetime.date.today())
model = tf.keras.models.load_model(fileName)
data = pd.read_csv("results.csv", header=0)[100:]#todo proper train/test/predict split
target="marketCap"

predict(model, data, target)