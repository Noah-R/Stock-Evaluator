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
learningrate = .00001
batchsize = 80
epochs = 100
l2rate = .00015
dropoutrate = 0.1
earlyStoppingPatience = 20
layersize = 192

modelName = str(datetime.date.today())
#modelName = "2022-06-29"#date override
modelName = 'Stock-Evaluator/models/model-'+modelName

#All non-contingent field declarations above, all function calls below

input("Input any text to attempt "+str((len(symbols)+len(benchmarks))*len(queries))+" API requests")

result = fetcher.fetchEndpoints(symbols+benchmarks, queries)
input("Successfully wrote "+str(result)+" files, input any text to continue")

dataset = preprocessor.buildDataset(symbols, features, dates[0], dates[1], startYear, endYear, debug = debug)
#dataset = dataset.sort_index(axis=1)#uncomment to alphabetize columns
dataset.to_csv("Stock-Evaluator/results.csv", index=False)
print("Successfully built dataset with "+str(len(dataset))+" examples and "+str(len(dataset.keys()))+" features, input any text to continue")

#dataset = pd.read_csv("Stock-Evaluator/results.csv", header=0)#uncomment if skipping buildDataset
#dataset = dataset.sample(frac=1, random_state=1).reset_index()#uncomment to shuffle before split
testdata = dataset[80:100]
predictdata = dataset[100:]
dataset = dataset[:80]

dataset.drop(columns=[future, "symbol"], inplace=True)
testdata.drop(columns=[future, "symbol"], inplace=True)

model.trainModel(dataset, testdata, target, learningrate, batchsize, epochs, l2rate, dropoutrate, earlyStoppingPatience, layersize)
input("Successfully trained model, input any text to continue")

predict.assessProfit(modelName, predictdata, target, future)