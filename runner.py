import fetcher
import preprocessor
import model
import predict
import utils
import pandas as pd
import datetime

#fetcher
symbols = utils.readSymbols("symbols.txt")
dates = ["2022-01-03", "2022-06-01"]

queries = [
    {"endpoint":"income-statement", "params":"limit=120", "name":"income_statement"},
    {"endpoint":"balance-sheet-statement", "params":"limit=120", "name":"balance_sheet"},
    {"endpoint":"cash-flow-statement", "params":"limit=120", "name":"cash_flow"},
    {"endpoint":"historical-price-full/stock_split", "params":"", "name":"splits"},
    {"endpoint":"historical-price-full/stock_dividend", "params":"", "name":"dividends"}
    ]
for date in dates:
    queries.append({"endpoint":"historical-price-full", "params":"from="+date+"&to="+date, "name":"price_"+date})

input("Input any text to attempt "+str(len(symbols)*len(queries)+len(dates))+" API requests")

result = fetcher.fetchStatements(symbols = symbols, queries = queries)
result += fetcher.fetchBenchmarks(dates)

print("Successfully wrote "+str(result)+" files")

#end fetcher
#preprocessor

features = ['balance_sheet', 'income_statement', 'cash_flow']
startYear = 2019
endYear = 2021
prepare = True

dataset = preprocessor.buildDataset(symbols, features, dates[0], dates[1], startYear, endYear, prepare = prepare)
#dataset = dataset.sort_index(axis=1)#uncomment to alphabetize columns
dataset.to_csv("results.csv", index=False)
print("Successfully built dataset with "+str(len(dataset))+" examples and "+str(len(dataset.keys()))+" features")

#end preprocessor
#model

#dataset = pd.read_csv("results.csv", header=0)
dataset.drop(columns="price_"+dates[1], inplace=True)
#dataset = dataset.sample(frac=1, random_state=1).reset_index()#uncomment to shuffle before split
testdata = dataset[80:100]
predictdata = dataset[100:]
dataset = dataset[:80]

target = "price_"+dates[0]
learningrate = .00001
batchsize = 80
epochs = 100
l2rate = .00015
dropoutrate = 0.1
earlyStoppingPatience = 20
layersize = 192
date = str(datetime.date.today())

model.trainModel(dataset, testdata, target, learningrate, batchsize, epochs, l2rate, dropoutrate, earlyStoppingPatience, layersize, date)

#end model
#predict

#date = "2022-06-25"#date override
modelName = 'models\model-'+date
future = "price_"+dates[1]

predict.predict(modelName, predictdata, target, future)