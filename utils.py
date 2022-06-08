import os

def readSymbols(filename):
    symbolList = open(filename, "r")
    symbols = []
    for line in symbolList:
            symbols.append(str(line).strip().upper())
    return symbols

def getFileNames(folder):
    fileNames = []
    for file in os.listdir(folder):
        filename = os.fsdecode(file)
        fileNames.append(folder+"/"+filename)
    return fileNames