import os

def readSymbols(filename):
    symbolList = open(filename, "r")
    symbols = []
    for line in symbolList:
        symbol = str(line).strip().upper()
        if(symbol not in symbols):
            symbols.append(symbol)
    return symbols

def getFileNames(folder):
    fileNames = []
    for file in os.listdir(folder):
        filename = os.fsdecode(file)
        fileNames.append(folder+"/"+filename)
    return fileNames

def symbolOverlap(file1, file2):
    a = readSymbols(file1)
    b = readSymbols(file2)
    overlap = []
    for symbol in a:
        if symbol in b:
            overlap.append(symbol)
    return overlap

def symbolMerge(fileNames):
    mergedSymbols = []
    for name in fileNames:
        symbols = readSymbols(name)
        for symbol in symbols:
            if symbol not in mergedSymbols:
                mergedSymbols.append(symbol)
    return mergedSymbols

def writeSymbols(symbols, target):
    f = open(target, "w")
    for symbol in symbols:
        f.write(symbol+"\n")
    f.close()