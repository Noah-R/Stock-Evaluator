import numpy as np
import pandas as pd
import tensorflow as tf
import utils
import datetime

def strategy(pred, label):
    """Determine portfolio weight of a single stock symbol

    :param pred: Stock price predicted by model
    :type pred: float
    :param label: Actual stock price
    :type label: float
    :return: Relative weight
    :rtype: float
    """
    if label == None or pred<label:
        return 0
    return (pred/label)**2

def getWeights(preds, labels):
    """Determine portfolio weight for each stock symbol

    :param preds: List of future stock prices predicted by model
    :type preds: list
    :param labels: List of current stock prices
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

def assessModel(modelName, data, currentDate, futureDate, benchmark):
    """Assess profitability of model-based strategy compared to a market benchmark

    :param modelName: Folder name to load model from
    :type modelName: str
    :param data: Dataset to predict using
    :type data: pandas.DataFrame
    :param currentDate: Date to predict price os
    :type currentDate: str
    :param futureDate: Date to assess profit/loss using
    :type futureDate: str
    :param benchmark: Stock symbol to compare model return to
    :type benchmark: str
    """
    model = tf.keras.models.load_model(modelName)
    features = {name: np.array(value) for name, value in data.items()}
    futurePrices = np.array(features.pop("price"))
    symbols = np.array(features.pop("symbol"))
    currentPrices = [utils.parsePrice(s, currentDate) for s in symbols]

    preds = model.predict(x=features, verbose=1)
    weights = getWeights(preds, currentPrices)
    weightTotal = sum(weights)

    investment = 10000
    cashout = investment

    for i in range(len(preds)):
        currentPrice = currentPrices[i]
        futurePrice = futurePrices[i]
        symbol = symbols[i]
        proportion = weights[i]/weightTotal
        shares=0
        try:
            shares = int(investment*proportion/currentPrice)
        except:
            shares=0
        
        if(shares>0):
            print("Bought "+str(shares)+" shares of "+str(symbol)+" at "+str(currentPrice)+" each, returning "+str(futurePrice)+" after splits and dividends")
            cashout += (futurePrice-currentPrice)*shares

    print("Model percent return: "+str(round(100*(cashout/investment-1), 2)))

    mktEnd = utils.parsePrice(benchmark, futureDate)
    mktStart = utils.parsePrice(benchmark, currentDate)
    mktReturn = utils.getSymbolReturn(benchmark, mktEnd, currentDate, futureDate)
    print("Market percent return: "+str(round(100*(mktReturn/mktStart-1), 2)))