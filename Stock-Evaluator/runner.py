import fetcher
import preprocessor
import model
import predict
import utils
import pandas as pd
import datetime
import os

dates = ["2022-01-03", "2022-06-01"]
symbols = utils.readSymbols('Stock-Evaluator/symbols.txt')
benchmarks = ["VTSAX"]
queries = [
    {"endpoint":"income-statement", "params":"limit=120", "name":"income_statement"},
    {"endpoint":"balance-sheet-statement", "params":"limit=120", "name":"balance_sheet"},
    {"endpoint":"cash-flow-statement", "params":"limit=120", "name":"cash_flow"},
    {"endpoint":"historical-price-full/stock_split", "params":"", "name":"splits"},
    {"endpoint":"historical-price-full/stock_dividend", "params":"", "name":"dividends"}
    ]
for date in dates:
    queries.append({"endpoint":"historical-price-full", "params":"from="+date+"&to="+date, "name":"price_"+date})

features = ['balance_sheet', 'income_statement', 'cash_flow']
startYear = 2019
endYear = 2021
debug = False

future = "price_"+dates[1]
target = "price_"+dates[0]
learningrate = .0001
batchsize = 256
epochs = 100
l2rate = .00015
dropoutrate = 0.0
earlyStoppingPatience = 20
layersize = 192

modelName = str(datetime.date.today())
modelName = "2022-06-30"#date override
modelName = 'Stock-Evaluator/models/model-'+modelName
adjustments = ['splits', 'dividends']










if(input("Input 0 to skip attempting "+str((len(symbols)+len(benchmarks))*len(queries))+" API requests") !="0"):
    result = fetcher.fetchEndpoints(symbols+benchmarks, queries)
    print("Successfully wrote "+str(result)+" files")

if(input("Input 0 to skip building dataset(Rebuilding the dataset after training the model will lead to in-sample predictions)") !="0"):
    dataset = preprocessor.buildDataset(symbols, features, dates, startYear, endYear, debug = debug)
    dataset.to_csv("Stock-Evaluator/results.csv", index=False)
    print("Successfully built dataset with "+str(len(dataset))+" examples and "+str(len(dataset.keys()))+" features")
else:
    dataset = pd.read_csv("Stock-Evaluator/results.csv", header=0)
    print("Loaded dataset from existing file")

predictData = dataset[int(len(dataset)*.8):]
if(input("Input 0 to skip training model") !="0"):
    valData = dataset[int(len(dataset)*.6):int(len(dataset)*.8)]
    dataset = dataset[:int(len(dataset)*.6)]

    dataset.drop(columns=[future, "symbol"], inplace=True)
    valData.drop(columns=[future, "symbol"], inplace=True)

    model.trainModel(dataset, valData, target, learningrate, batchsize, epochs, l2rate, dropoutrate, earlyStoppingPatience, layersize)
    print("Successfully trained model")

if(input("Input 0 to skip prediction") !="0"):
    predict.assessModel(modelName, predictData, dates[0], dates[1], benchmarks[0])