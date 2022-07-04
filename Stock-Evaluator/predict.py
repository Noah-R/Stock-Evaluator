import numpy as np
import pandas as pd
import tensorflow as tf
import utils
import datetime

def parseHistorical(fileName, type, startDateTime = datetime.date(1970, 1, 1), endDateTime = datetime.date.today()):
    #todo: Dividends should count if bought before and sold on/after date, splits should count if bought on/before and sold after date
    """Parses a file of historical records, either dividends or splits, into a list of processing instructions

    :param fileName: File to parse
    :type fileName: str
    :param type: Type of instruction
    :type type: str
    :param startDateTime: Date to begin reading, defaults to 1970-01-01
    :type startDateTime: datetime.date, optional
    :param endDateTime: Date to end reading, defaults to current day
    :type endDateTime: datetime.date, optional
    :return: List of instructions
    :rtype: list of dicts with keys {"type", "date", "amount"}
    """
    df = pd.read_json(fileName)
    instructions = []
    if("historical" in df):
        l = list(df['historical'])
        for i in l:
            date = utils.dateFromStr(i["date"])
            if(date>=startDateTime and date<=endDateTime):
                if(type == "split"):
                    instructions.append({"type": "split", "date": i["date"], "amount": i["numerator"]/i["denominator"]})
                elif(type == "dividend"):
                    instructions.append({"type": "dividend", "date": i["date"], "amount": i["dividend"]})
                else:
                    print("Unknown instruction type")
    return instructions


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

def getSymbolReturn(symbol, endPrice, startDate, endDate):
    """For a given symbol between two dates, sequentially tabulate all dividends and factor for all splits, and return the adjusted return on investment

    :param symbol: Stock symbol
    :type symbol: str
    :param endPrice: Price on endDate
    :type endPrice: float
    :param startDate: Date to begin tabulating
    :type startDate: str
    :param endDate: Date to end tabulating
    :type endDate: str
    :return: Total return on investment per share over time period
    :rtype: float
    """
    startDateTime = utils.dateFromStr(startDate)
    endDateTime = utils.dateFromStr(endDate)
    
    dividends = "Stock-Evaluator/API Archives/"+symbol+"_dividends.json"
    splits = "Stock-Evaluator/API Archives/"+symbol+"_splits.json"

    instructions = parseHistorical(splits, "split", startDateTime, endDateTime)
    instructions += parseHistorical(dividends, "dividend", startDateTime, endDateTime)    
    instructions = sorted(instructions, key = lambda i: i['date'])

    shares = 1
    dividends = 0
    for i in instructions:
        if(i["type"] == "split"):
            shares *= i["amount"]
        elif(i["type"] == "dividend"):
            dividends += i["amount"]*shares
        else:
            print("Unknown instruction type")

    return endPrice*shares+dividends

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
        shares = int(investment*proportion/currentPrice)
        
        if(shares>0):
            ret = getSymbolReturn(symbol, futurePrice, currentDate, futureDate)
            cashout += (ret-currentPrice)*shares

    print("Model percent return: "+str(round(100*(cashout/investment-1), 2)))

    mktEnd = utils.parsePrice(benchmark, futureDate)
    mktStart = utils.parsePrice(benchmark, currentDate)
    mktReturn = getSymbolReturn(benchmark, mktEnd, currentDate, futureDate)
    print("Market percent return: "+str(round(100*(mktReturn/mktStart-1), 2)))