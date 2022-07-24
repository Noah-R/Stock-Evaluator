import fetcher
import preprocessor
import model
import predict
import utils
import pandas as pd
import datetime
import os

APIlimit = 300
overwrite = False
confirms = False
#todo: standardize time period by endYear/length, startYear = endYear-length, startDate 1/1, endDate 7/4
timePeriods = [
    {"startDate": "2012-01-02", "endDate": "2012-06-01", "startYear": 2009, "endYear": 2011},
    {"startDate": "2013-01-02", "endDate": "2013-06-01", "startYear": 2010, "endYear": 2012},
    {"startDate": "2014-01-02", "endDate": "2014-06-01", "startYear": 2011, "endYear": 2013},
    {"startDate": "2015-01-02", "endDate": "2015-06-01", "startYear": 2012, "endYear": 2014},
    {"startDate": "2016-01-04", "endDate": "2016-06-01", "startYear": 2013, "endYear": 2015},
    {"startDate": "2017-01-02", "endDate": "2017-06-01", "startYear": 2014, "endYear": 2016},
    {"startDate": "2018-01-02", "endDate": "2018-06-01", "startYear": 2015, "endYear": 2017},
    {"startDate": "2019-01-02", "endDate": "2019-06-01", "startYear": 2016, "endYear": 2018},
    {"startDate": "2020-01-02", "endDate": "2020-06-01", "startYear": 2017, "endYear": 2019},
    {"startDate": "2021-01-04", "endDate": "2021-06-01", "startYear": 2018, "endYear": 2020},
    {"startDate": "2022-01-03", "endDate": "2022-06-01", "startYear": 2019, "endYear": 2021}
]
symbols = utils.readSymbols('Stock-Evaluator/symbols.txt')
benchmarks = ["VTSAX"]
queries = [
    {"endpoint":"income-statement", "params":"limit=120", "name":"income_statement"},
    {"endpoint":"balance-sheet-statement", "params":"limit=120", "name":"balance_sheet"},
    {"endpoint":"cash-flow-statement", "params":"limit=120", "name":"cash_flow"},
    {"endpoint":"historical-price-full/stock_split", "params":"", "name":"splits"},
    {"endpoint":"historical-price-full/stock_dividend", "params":"", "name":"dividends"}
    ]
for period in timePeriods:
    date = period["endDate"]
    queries.append({"endpoint":"historical-price-full", "params":"from="+date+"&to="+date, "name":"price_"+date})
date = timePeriods[-1]["startDate"]
queries.append({"endpoint":"historical-price-full", "params":"from="+date+"&to="+date, "name":"price_"+date})

features = ['balance_sheet', 'income_statement', 'cash_flow']
debug = False

target = "price"
learningrate = .0001
batchsize = 512
epochs = 100
l2rate = .00015
dropoutrate = 0.0
earlyStoppingPatience = epochs
layersize = 192

modelName = str(datetime.date.today())
modelName = 'Stock-Evaluator/models/model-'+modelName
adjustments = ['splits', 'dividends']










if(input("Input 0 to skip attempting "+str((len(symbols)+len(benchmarks))*len(queries))+" API requests") !="0"):
    result = fetcher.fetchEndpoints(symbols+benchmarks, queries, overwrite = overwrite, limit = APIlimit, confirmEach = confirms)
    print("Successfully wrote "+str(result)+" files")

if(input("Input 0 to skip building training set(Rebuilding the dataset after training the model will lead to in-sample predictions)") !="0"):
    trainingSet = preprocessor.buildDataset(symbols, features, timePeriods[:-1], debug = debug)
    trainingSet.to_csv("Stock-Evaluator/trainingData.csv", index=False)
    print("Successfully built dataset with "+str(len(trainingSet))+" examples and "+str(len(trainingSet.keys()))+" features")
else:
    trainingSet = pd.read_csv("Stock-Evaluator/trainingData.csv", header=0)
    print("Loaded dataset from existing file")

if(input("Input 0 to skip training model") !="0"):
    trainingSet.drop(columns=["symbol", "startYear", "endYear"], inplace=True)

    valData = trainingSet[int(len(trainingSet)*.8):]
    trainingSet = trainingSet[:int(len(trainingSet)*.8)]

    model.trainModel(trainingSet, valData, target, learningrate, batchsize, epochs, l2rate, dropoutrate, earlyStoppingPatience, layersize)
    print("Successfully trained model")

if(input("Input 0 to skip prediction") !="0"):
    predictData = preprocessor.buildDataset(symbols, features, [timePeriods[-1]], debug = debug)
    predict.assessModel(modelName, predictData, timePeriods[-1]["startDate"], timePeriods[-1]["endDate"], benchmarks[0])