import pandas as pd
import utils

def prepareForTraining(df, coefficient = 1000000, requiredColumns = [], excludeFromNormalization = []):
    """Performs final preprocessing transformations on assembled dataset

    :param df: Assembled dataset
    :type df: pandas.DataFrame
    :param coefficient: Number to divide all values by, defaults to 1000000
    :type coefficient: int, optional
    :param requiredColumns: Columns to require, any row missing any required column will be dropped, defaults to []
    :type requiredColumns: list, optional
    :param excludeFromNormalization: Columns to exclude from division by coefficient, defaults to []
    :type excludeFromNormalization: list, optional
    :return: Preprocessed dataset
    :rtype: pandas.DataFrame
    """
    df = df.dropna(subset = requiredColumns)
    df = df.dropna(thresh = len(df.keys())-3)
    df = df.fillna(value = 0)

    for column in df.keys():
        if column not in excludeFromNormalization:
            df[column] = df[column] / coefficient

    df = df.sample(frac=1, random_state=1).reset_index(drop=True)

    return df

def buildPeriodDataset(symbols, features, startYear, endYear, startDate, targetDate):
    """Builds dataset from fetched files for a given time period

    :param symbols: List of stock symbols to include
    :type symbols: list
    :param features: List of financial statements to read features from
    :type features: list
    :param startYear: First year to include features from
    :type startYear: int
    :param endYear: Last year to include features from
    :type endYear: int
    :param startDate: Date on which model will predict future price
    :type startDate: str, "yyyy-mm-dd"
    :param targetDate: Date for which model will predict price
    :type targetDate: str, "yyyy-mm-dd"
    :return: Built dataset
    :rtype: pandas.DataFrame
    """
    df = pd.DataFrame()

    for symbol in symbols:
        rowdf = pd.DataFrame()
        rowdf["symbol"] = [symbol]
        rowdf["startYear"] = [startYear]
        rowdf["endYear"] = [endYear]

        price = utils.parsePrice(symbol, targetDate)
        #todo: debug this if/else through full workflow
        if(price == None):
            rowdf["price"] = 0
        else:
            rowdf["price"] = [utils.getSymbolReturn(symbol, price, startDate, targetDate)]

        for statement in features:
            statementdf = utils.parseFinancialStatement(symbol, statement, startYear, endYear)

            rowdf = rowdf.merge(statementdf, how='outer', on='symbol')   
        
        df = pd.concat([df, rowdf])

    return df

def buildDataset(symbols, features, timePeriods, debug = False):
    """Builds dataset from fetched files for a given list of time periods

    :param symbols: List of stock symbols to include
    :type symbols: list
    :param features: List of financial statements to read features from
    :type features: list
    :param timePeriods: List of time periods to assemble data over
    :type timePeriods: list of dicts with keys {"endDate", "startYear", "endYear"}
    :param debug: Whether to skip final preprocessing transformations for debug purposes, defaults to False
    :type debug: bool, optional
    :return: Built dataset
    :rtype: pandas.DataFrame
    """
    masterdf = pd.DataFrame()
    
    for period in timePeriods:
        perioddf = buildPeriodDataset(symbols, features, period["startYear"], period["endYear"], period["startDate"], period["endDate"])
        masterdf = pd.concat([masterdf, perioddf])
    
    if (not debug):
        exclude = ["symbol", "startYear", "endYear", "price"]
        masterdf = prepareForTraining(masterdf, requiredColumns = exclude, excludeFromNormalization = exclude)

    return masterdf