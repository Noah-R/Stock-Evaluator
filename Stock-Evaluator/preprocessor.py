import pandas as pd
import utils

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
    fileName = "Stock-Evaluator/API Archives/"+symbol+"_"+statement+".json"
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

def prepareForTraining(df, coefficient = 1000000, requiredColumns = [], columnsToExclude = []):
    """Performs final preprocessing transformations on assembled dataset

    :param df: Assembled dataset
    :type df: pandas.DataFrame
    :param coefficient: Number to divide all values by, defaults to 1000000
    :type coefficient: int, optional
    :param requiredColumns: Columns to require, any row missing any required column will be dropped, defaults to []
    :type requiredColumns: list, optional
    :param columnsToExclude: Columns to exclude from division by coefficient, defaults to []
    :type columnsToExclude: list, optional
    :return: Preprocessed dataset
    :rtype: pandas.DataFrame
    """
    df = df.dropna(subset = requiredColumns)
    df = df.dropna(thresh = 3)
    df = df.fillna(value = 0)

    for column in df.keys():
        if column not in columnsToExclude:
            df[column] = df[column] / coefficient

    df = df.sample(frac=1, random_state=1).reset_index(drop=True)

    return df

def buildDataset(symbols, features, dates, startYear, endYear, debug=False):
    """Builds dataset from fetched files

    :param symbols: List of stock symbols to include
    :type symbols: list
    :param features: List of financial statements to read features from
    :type features: list
    :param labelDate: List of dates to parse prices for
    :type labelDate: list of strs, "yyyy-mm-dd"
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

        for date in dates:
            price = utils.parsePrice(symbol, date)
            rowdf["price_"+date] = [price]

        for statement in features:
            df = parseFinancialStatement(symbol, statement, startYear, endYear)

            rowdf = rowdf.merge(df, how='outer', on='symbol')   

        masterdf = pd.concat([masterdf, rowdf])
        
    if (not debug):
        exclude = ["symbol"]
        for date in dates:
            exclude.append("price_"+date)
        masterdf = prepareForTraining(masterdf, requiredColumns = exclude, columnsToExclude = exclude)
    return masterdf