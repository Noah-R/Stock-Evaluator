import numpy as np
import pandas as pd
import tensorflow as tf
import datetime

def predict(model, data, target, future):
    features = {name: np.array(value) for name, value in data.items()}
    labels = np.array(features.pop(target))
    futures = np.array(features.pop(future))

    preds = model.predict(x=features, verbose=1)

    investment = 0
    performance = 0
    
    for i in range(len(preds)):
        pred = preds[i][0]
        label = labels[i]
        actual = futures[i]
        shares = max(int(pred/label), 0)
        cost = shares*label
        profit = round(shares*(actual-label), 2)
        print("Predicted: "+str(pred))
        print("Market price: "+str(label))
        print("True value: "+str(actual))
        print("Shares bought: "+str(shares)+" for $"+str(cost))
        print("Profit: $"+str(profit))
        print("---")
        investment += cost
        performance += profit
    
    print("Model percent return: "+str(round(100*(performance/investment), 2)))
    mktEnd = 1
    mktStart = 1
    print("Market percent return: "+str(round(100*(mktEnd/mktStart-1), 2)))

fileName = 'models\model-'+str(datetime.date.today())
model = tf.keras.models.load_model(fileName)
data = pd.read_csv("results.csv", header=0)[100:]
target = "price_label"
future = "price_future"

predict(model, data, target, future)