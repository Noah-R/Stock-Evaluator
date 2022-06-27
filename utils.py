import os
import json

def readSymbols(filename):
    """Parses a text file of line-separated stock symbols into a list

    :param filename: Relative path of file
    :type filename: str
    :return: List of stock symbols
    :rtype: list
    """
    symbolList = open(filename, "r")
    symbols = []
    for line in symbolList:
        symbol = str(line).strip().upper()
        if(symbol not in symbols):
            symbols.append(symbol)
    return symbols

def getFileNames(folder):
    """Returns a list of every file name in a given folder

    :param folder: Relative path of folder to search
    :type folder: str
    :return: List of file names
    :rtype: list
    """
    fileNames = []
    for file in os.listdir(folder):
        filename = os.fsdecode(file)
        fileNames.append(folder+"/"+filename)
    return fileNames

def writeSymbols(symbols, target):
    """Writes a list of stock symbols to a line-separated text file

    :param symbols: List of stock symbols
    :type symbols: list
    :param target: Relative path of file to write to
    :type target: str
    """
    f = open(target, "w")
    for symbol in symbols:
        f.write(symbol+"\n")
    f.close()