import numpy as np
import pandas as pd
import tensorflow as tf
import datetime
import utils

def parsePrice(symbol, name):
    fileName = "API Archives/"+symbol+"_"+name+".json"
    df = pd.read_json(fileName)

    if("historical" in df):
        return df["historical"].apply(lambda x: round(x["close"], 2))[0]

    return 0

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
    mktEnd = parsePrice("benchmark", "futureDate")
    mktStart = parsePrice("benchmark", "labelDate")
    print("Market percent return: "+str(round(100*(mktEnd/mktStart-1), 2)))

date = str(datetime.date.today())
date = "2022-06-22"#date override
fileName = 'models\model-'+date
model = tf.keras.models.load_model(fileName)
data = pd.read_csv("results.csv", header=0)[100:]
target = "price_label"
future = "price_future"

predict(model, data, target, future)