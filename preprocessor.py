import pandas as pd
import utils
import os

def parseFinancialStatement(symbol, statement, startYear, endYear):
    """Reads financial statement data from a fetched file

    :param symbol: Stock symbol to parse data for
    :type symbol: str
    :param statement: Financial statement to read features from
    :type statement: str
    :param startYear: First year to include features from
    :type startYear: int
    :param endYear: Last year to include features from
    :type endYear: int
    :return: Single-row DataFrame, containing values of each feature for each year
    :rtype: pandas.DataFrame
    """
    fileName = "API Archives/"+symbol+"_"+statement+".json"
    df = pd.read_json(fileName)

    dropCols = ["date", "reportedCurrency", "cik", "fillingDate", "acceptedDate", "period", "link", "finalLink"]
    df.drop(labels = dropCols, axis = 1, inplace = True)

    df = df[df["calendarYear"]<=endYear]
    df = df[df["calendarYear"]>=startYear]
    df["calendarYear"] = df["calendarYear"].astype("int64")
    df = df.drop_duplicates('calendarYear')

    #placeholder code for identifying symbols with missing data
    #for year in range(startYear, endYear+1):
    #    if(year not in set(df["calendarYear"])):
    #        print(df["symbol"].iloc[0]+" is missing "+statement+" data from "+str(year))

    df = df.melt(id_vars=["symbol", "calendarYear"])

    df["column"] = df["calendarYear"].astype(str)+"_"+statement+"_"+df["variable"]
    df.drop(labels = ["calendarYear", "variable"], axis = 1, inplace = True)

    df = pd.pivot(df, index="symbol", columns="column", values="value")

    return df

def prepareForTraining(df, coefficient = 1000000, columnsToExclude = []):
    """Performs final preprocessing transformations on assembled dataset

    :param df: Assembled dataset
    :type df: pandas.DataFrame
    :param coefficient: Number to divide all values by, defaults to 1000000
    :type coefficient: int, optional
    :param columnsToExclude: Columns to exclude from division by coefficient, defaults to []
    :type columnsToExclude: list, optional
    :return: Preprocessed dataset
    :rtype: pandas.DataFrame
    """
    df.drop(labels = "symbol", axis = 1, inplace = True)
    df = df.dropna(thresh = 3)
    df = df.fillna(value = 0)

    for column in columnsToExclude:
        df[column] = df[column] * coefficient
    df = df/coefficient

    return df

def buildDataset(symbols, features, labelDate, futureDate, startYear, endYear, debug=False):
    """Builds dataset from fetched files

    :param symbols: List of stock symbols to include
    :type symbols: list
    :param features: List of financial statements to read features from
    :type features: list
    :param labelDate: Date to predict stock price on
    :type labelDate: str, "yyyy-mm-dd"
    :param futureDate: Future date to assess profit/loss on
    :type futureDate: str, "yyyy-mm-dd"
    :param startYear: First year to include features from
    :type startYear: int
    :param endYear: Last year to include features from
    :type endYear: int
    :param debug: Whether to skip final preprocessing transformations for debug purposes, defaults to False
    :type debug: bool, optional
    :return: Built dataset
    :rtype: pandas.DataFrame
    """
    masterdf = pd.DataFrame()

    for symbol in symbols:
        rowdf = pd.DataFrame()
        rowdf["symbol"] = [symbol]

        labelPrice = utils.parsePrice(symbol, labelDate)
        futurePrice = utils.parsePrice(symbol, futureDate)
        if(labelPrice == -1 or futurePrice == -1):
            continue
        rowdf["price_"+labelDate] = [labelPrice]
        rowdf["price_"+futureDate] = [futurePrice]

        for statement in features:
            df = parseFinancialStatement(symbol, statement, startYear, endYear)

            rowdf = rowdf.merge(df, how='outer', on='symbol')   

        masterdf = pd.concat([masterdf, rowdf])
        
    if (not debug):
        masterdf = prepareForTraining(masterdf, columnsToExclude = ["price_"+labelDate, "price_"+futureDate])
    return masterdf