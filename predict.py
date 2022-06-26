import numpy as np
import pandas as pd
import tensorflow as tf
import datetime
import utils


def strategy(pred, label):
    if pred<label:
        return 0
    return (pred/label)**2

def getWeights(preds, labels):
    weights=[]

    for i in range(len(preds)):
        pred = preds[i][0]
        label = labels[i]
        
        weight = strategy(pred, label)
        weights.append(weight)
        
    return weights

def parsePrice(symbol, date):
    fileName = "API Archives/"+symbol+"_price_"+date+".json"
    df = pd.read_json(fileName)

    if("historical" in df):
        return df["historical"].apply(lambda x: round(x["close"], 2))[0]

    return 0

def predict(modelName, data, target, future):
    model = tf.keras.models.load_model(modelName)
    features = {name: np.array(value) for name, value in data.items()}
    labels = np.array(features.pop(target))
    futures = np.array(features.pop(future))

    preds = model.predict(x=features, verbose=1)
    weights = getWeights(preds, labels)
    weightTotal = sum(weights)

    investment = 10000
    cashout = investment

    for i in range(len(preds)):
        actual = labels[i]
        future = futures[i]
        proportion = weights[i]/weightTotal
        shares = int(investment*proportion/actual)
        
        cashout += (future-actual)*shares

    print("Model percent return: "+str(round(100*(cashout/investment-1), 2)))

    mktEnd = parsePrice("benchmark", "2022-06-01")
    mktStart = parsePrice("benchmark", "2022-01-03")
    print("Market percent return: "+str(round(100*(mktEnd/mktStart-1), 2)))