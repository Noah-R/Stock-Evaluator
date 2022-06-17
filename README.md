Early work in progress

This will be a machine learning system which attempts to predict the long-run value of publicly traded companies.

This will not be a day-trading bot, it will not learn from market price history, and it will at most attempt to predict the price of a stock in several years' time, not tomorrow or next year.

---
To do:

    -Drop futureMarketCap in model/predict
    -Test rate of return compared to overall market for model-based strategy
    -Parameter to choose current/future date for preprocessor.transformMarketCaps
    -Data to collect:

        - Get data for more symbols
        - Get older data from premium API