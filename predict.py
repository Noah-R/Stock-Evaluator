import numpy as np
import pandas as pd
import tensorflow as tf
import datetime

def predict(model, data, target, future):
    features = {name: np.array(value) for name, value in data.items()}
    labels = np.array(features.pop(target))
    actuals = np.array(features.pop(future))

    preds = model.predict(x=features, verbose=1)

    investment = 0
    performance = 0
    
    for i in range(len(preds)):
        pred = preds[i][0]
        label = labels[i]
        actual = actuals[i]
        holding = round(pred/label*1000, 2)
        profit = round(actual/label*holding-holding, 2)
        print("Predicted: "+str(pred))
        print("Market value: "+str(label))
        print("True value: "+str(actual))
        print("Bought: $"+str(holding))
        print("Profit: $"+str(profit))
        print("---")
        investment += holding
        performance += profit
    
    print("Total invested: $"+str(round(investment, 2)))
    print("Total return: $"+str(round(performance, 2)))
    #todo fetch market return data rather than hard code
    print("Market return on investment: $"+str(round(3666.77/3900.86*investment-investment, 2)))

fileName = 'models\model-'+str(datetime.date.today())
model = tf.keras.models.load_model(fileName)
data = pd.read_csv("results.csv", header=0)[100:]#todo proper train/test/predict split
target = "marketCap"
future = "futureMarketCap"

predict(model, data, target, future)