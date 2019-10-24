import re
import time

regexTables = r"""[Tt]able[ ]+(?P<TableName>[^\s]+)(?:[ ]+as[ ]+(?P<TableShortName>[^\s]+))?[ ]*(?:\[(?P<TableOption>.*?)\])?[ ]*\{(?P<DeclBody>.*?)\}"""
regexFields = r"""(?P<FieldName>[^\s]+)[ ]+(?P<FieldType>[^\s]+)(?:[ ]+\[(?P<FieldOption>.*?)\])?[ ]*\n"""
regexOption = r"\b(?=\w)[^,]+"
tableArrayPrefix = "\t"
tableElementPrefix = "\t\t"
tablePropsPrefix = "\t\t\t"
fieldElementPrefix = "\t\t\t\t"
fieldPropsPrefix = "\t\t\t\t\t"
fieldOptionPrefix = "\t\t\t\t\t\t"
inputPath = "./dbdiagram.input"
outputPath = "./dbdiagram.json"

def renderOption(optionString, basePrefix):
    if optionString == None:
        return "null"
    result = "["
    matches = re.finditer(regexOption, optionString)
    for pi, i in enumerate(matches):
        if pi > 0:
            result += ','
        result += '\n'+ basePrefix + '"' + i.group() + '"'
    result += '\n' + basePrefix[:-1] + "]"
    return result

def renderFields(fieldsString):
    result = ""
    matchesField = re.finditer(regexFields, fieldsString)
    for pi, i in enumerate(matchesField):
        if pi > 0:
            result += ",\n"
        result += fieldElementPrefix + "{\n"
        group = i.groups()
        result += fieldPropsPrefix + '"name": "{0}",\n'.format(group[0])
        result += fieldPropsPrefix + '"type": "{0}",\n'.format(group[1])
        result += fieldPropsPrefix + \
            '"options": {0}\n'.format(
                renderOption(group[2], fieldOptionPrefix))
        result += fieldElementPrefix + "}"
    return result

def renderTables(tableString):
    result = ""
    matches = re.finditer(regexTables, tableString,
                              re.MULTILINE | re.VERBOSE | re.DOTALL)
    result = ""
    result += '{\n'
    result += tableArrayPrefix + '"Table":[\n'
    for matchNum, match in enumerate(matches, start=1):
        if matchNum > 1:
            result += ",\n"
        result += tableElementPrefix + "{\n"
        group = match.groups()
        result += tablePropsPrefix + '"name": "{0}",\n'.format(group[0])
        result += tablePropsPrefix + '"shortName": "{0}",\n'.format(group[1])
        result += tablePropsPrefix + \
            '"option": {0},\n'.format(renderOption(group[2], fieldElementPrefix))
        result += tablePropsPrefix + \
            '"fields": [\n{0}\n'.format(renderFields(group[3]))
        result += tablePropsPrefix + "]\n"
        result += tableElementPrefix + "}"
        print('.', end='')
    result += "\n" + tableArrayPrefix + "]\n"
    result += "}"
    return (result, matchNum)

print("Generating")
now = time.time()

dbdiagraminput = open(inputPath, 'r').read()

tableOutput = renderTables(dbdiagraminput)

open(outputPath, 'w').write(tableOutput[0])

print("\nGenerate succeeded", tableOutput[1],
      "tables in {0:0.4f} second(s)".format(time.time()-now))
