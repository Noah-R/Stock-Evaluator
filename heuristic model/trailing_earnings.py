import json
import numpy as np

f = open('jblu_earnings.json')
data = json.load(f)

lastyear = 2021
firstyear = 2012
earnings = []
weights = []

for entry in data["annualEarnings"]:
    year = int(entry["fiscalDateEnding"][:4])
    if(year>=firstyear and year<=lastyear):
        earnings.append(float(entry["reportedEPS"]))

for num in range(lastyear-firstyear, -1, -1):
    weights.append(num)

print(earnings)
print(weights)
print("Predicted 2022 earnings per share: "+str(np.average(earnings, weights=weights)))