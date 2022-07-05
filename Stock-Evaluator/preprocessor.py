import pandas as pd
from regex import DEBUG
import utils

def parseFinancialStatement(symbol, statement, startYear = 1970, endYear = 2039):
    """Reads financial statement data from a fetched file between two given years

    :param symbol: Stock symbol to parse data for
    :type symbol: str
    :param statement: Financial statement to read features from
    :type statement: str
    :param startYear: First year to include features from, defaults to 1970
    :type startYear: int, optional
    :param endYear: Last year to include features from, defaults to 2039
    :type endYear: int, optional
    :return: Single-row DataFrame, containing values of each feature for each year
    :rtype: pandas.DataFrame
    """
    fileName = "Stock-Evaluator/API Archives/"+symbol+"_"+statement+".json"
    df = pd.read_json(fileName)

    dropCols = ["date", "reportedCurrency", "cik", "fillingDate", "acceptedDate", "period", "link", "finalLink"]
    df.drop(labels = dropCols, axis = 1, inplace = True)

    df = df[df["calendarYear"]<=endYear]
    df = df[df["calendarYear"]>=startYear]
    df["calendarYear"] = df["calendarYear"].astype("int64")
    df = df.drop_duplicates('calendarYear')

    df = df.melt(id_vars=["symbol", "calendarYear"])

    df["column"] = "y"+(df["calendarYear"]-endYear).astype(str)+"_"+statement+"_"+df["variable"]
    df.drop(labels = ["calendarYear", "variable"], axis = 1, inplace = True)

    df = pd.pivot(df, index="symbol", columns="column", values="value")

    return df

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
    df = df.dropna(thresh = 3)
    df = df.fillna(value = 0)

    for column in df.keys():
        if column not in excludeFromNormalization:
            df[column] = df[column] / coefficient

    df = df.sample(frac=1, random_state=1).reset_index(drop=True)

    return df

def buildPeriodDataset(symbols, features, startYear, endYear, targetDate):
    """Builds dataset from fetched files for a given time period

    :param symbols: List of stock symbols to include
    :type symbols: list
    :param features: List of financial statements to read features from
    :type features: list
    :param startYear: First year to include features from
    :type startYear: int
    :param endYear: Last year to include features from
    :type endYear: int
    :param targetDate: Date for which model will predict price
    :type targetDate: str, "yyyy-mm-dd"
    :return: Built dataset
    :rtype: pandas.DataFrame
    """
    df = pd.DataFrame()

    for symbol in symbols:
        rowdf = pd.DataFrame()
        rowdf["symbol"] = [symbol]

        price = utils.parsePrice(symbol, targetDate)
        rowdf["price"] = [price]

        for statement in features:
            statementdf = parseFinancialStatement(symbol, statement, startYear, endYear)

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
        perioddf = buildPeriodDataset(symbols, features, period["startYear"], period["endYear"], period["endDate"])
        masterdf = pd.concat([masterdf, perioddf])
    
    if (not debug):
        exclude = ["symbol", "price"]
        masterdf = prepareForTraining(masterdf, requiredColumns = exclude, excludeFromNormalization = exclude)

    return masterdf