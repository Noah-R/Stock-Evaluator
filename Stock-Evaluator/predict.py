import numpy as np
import pandas as pd
import tensorflow as tf
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

def getSymbolReturn(symbol, startPrice, endPrice, startDate, endDate):
    """For a given symbol between two dates, sequentially tabulate all dividends and factor for all splits, and return the adjusted return on investment

    :param symbol: Stock symbol
    :type symbol: str
    :param startPrice: Price on startDate
    :type startPrice: float
    :param endPrice: Price on endDate
    :type endPrice: float
    :param startDate: Date to begin tabulating
    :type startDate: str
    :param endDate: Date to end tabulating
    :type endDate: str
    :return: Total return on investment per share over time period
    :rtype: float
    """
    return endPrice-startPrice

def assessProfit(modelName, data, targetDate, futureDate, benchmark):
    """Assess profitability of model-based strategy compared to a market benchmark

    :param modelName: Folder name to load model from
    :type modelName: str
    :param data: Dataset to predict using
    :type data: pandas.DataFrame
    :param targetDate: Date to predict price os
    :type targetDate: str
    :param futureDate: Date to assess profit/loss using
    :type futureDate: str
    :param benchmark: Stock symbol to compare model return to
    :type benchmark: str
    """
    model = tf.keras.models.load_model(modelName)
    features = {name: np.array(value) for name, value in data.items()}
    labels = np.array(features.pop("price_"+targetDate))
    futures = np.array(features.pop("price_"+futureDate))
    symbols = np.array(features.pop("symbol"))

    preds = model.predict(x=features, verbose=1)
    weights = getWeights(preds, labels)
    weightTotal = sum(weights)

    investment = 10000
    cashout = investment

    for i in range(len(preds)):
        actual = labels[i]
        future = futures[i]
        symbol = symbols[i]
        proportion = weights[i]/weightTotal
        shares = int(investment*proportion/actual)
        
        if(shares>0):
            ret = getSymbolReturn(symbol, actual, future, targetDate, futureDate)
            cashout += (ret)*shares
            print("Bought "+str(shares)+" shares of "+symbol+" for "+str(actual)+" each, and sold for "+str(future)+" each, earning $"+str((future-actual)*shares)+" total profit after splits and dividends")

    print("Model percent return: "+str(round(100*(cashout/investment-1), 2)))

    mktEnd = utils.parsePrice(benchmark, futureDate)
    mktStart = utils.parsePrice(benchmark, targetDate)
    print("Market percent return: "+str(round(100*(mktEnd/mktStart-1), 2)))