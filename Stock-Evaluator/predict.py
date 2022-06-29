import numpy as np
import pandas as pd
import tensorflow as tf
import datetime
import utils


def strategy(pred, label):
    """Determine portfolio weight of a single stock symbol

    :param pred: Stock price predicted by model
    :type pred: float
    :param label: Actual stock price
    :type label: float
    :return: Relative weight
    :rtype: float
    """
    if pred<label:
        return 0
    return (pred/label)**2

def getWeights(preds, labels):
    """Determine portfolio weight for each stock symbol

    :param preds: List of stock prices predicted by model
    :type preds: list
    :param labels: List of actual stock prices
    :type labels: list
    :return: List of relative weights for each stock
    :rtype: list
    """
    weights=[]

    for i in range(len(preds)):
        pred = preds[i][0]
        label = labels[i]
        
        weight = strategy(pred, label)
        weights.append(weight)
        
    return weights

def assessProfit(modelName, data, target, future, benchmark = "VTSAX"):
    """Assess profitability of model-based strategy compared to a market benchmark

    :param modelName: Folder name to load model from
    :type modelName: str
    :param data: Dataset to predict using
    :type data: pandas.DataFrame
    :param target: Name of column to predict
    :type target: str
    :param future: Name of column to assess profit/loss using
    :type future: str
    :param benchmark: Stock symbol to compare model return to, defaults to "VTSAX
    :type benchmark: str, optional
    """
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

    mktEnd = utils.parsePrice(benchmark, "2022-06-01")
    mktStart = utils.parsePrice(benchmark, "2022-01-03")
    print("Market percent return: "+str(round(100*(mktEnd/mktStart-1), 2)))