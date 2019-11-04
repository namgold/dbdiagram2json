import re, time, json

regexTables = r"""[Tt]able[ ]+(?P<TableName>[^\s]+)(?:[ ]+as[ ]+(?P<TableShortName>[^\s]+))?[ ]*(?:\[(?P<TableOption>.*?)\])?[ ]*\{(?P<DeclBody>.*?)\}"""
regexFields = r"""(?P<FieldName>[^\s]+)[ ]+(?P<FieldType>[^\s]+)(?:[ ]*\[(?P<FieldOption>.*?)\])?[ ]*\n"""
inputPath = "./dbdiagram.input"
outputPath = "./dbdiagram.json"

def buildFieldOption(optionString):
    if optionString == None:
        return None
    options = {
    #    "ref":         None,
    #    "default" :    None,
    #    "increment":   None,
    #    "nullable":    None,
    #    "primary key": None,
    #    "unique":      None,
    #    "note":        None
    }
    optionString = optionString.replace('\n', ' ').strip().split(',')
    for i in optionString:
        words = i.strip().split(' ')
        if words[0] == "default:":
            default = re.findall("(?:\"([^\"]*)\")|(?:'([^']*)')", i)[0]
            options["default"] = default[0] if default[1] == "" else default[1]
        elif words[0] == "ref:":
            matchRef = re.findall("([<>-])[ ]+([^.]+)\.([^,\]]+)", i)[0]
            options["ref"] = {
                "op": matchRef[0],
                "table": matchRef[1],
                "column": matchRef[2]
            }
        elif words[0] == "note:":
            note = re.findall("(?:\"([^\"]*)\")|(?:'([^']*)')", i)[0]
            options["note"] = note[0] if note[1] == "" else note[1]
        elif words[0] == "increment":
            options[words[0]] = True
        elif words[0] == "null":
            options["nullable"] = True
        elif words[0] == "not":
            options["nullable"] = False
        elif words[0] == "primary" or words[0] == "pk":
            options["primary key"] = True
        elif words[0] == "unique":
            options["unique"] = True
    return options

def buildFields(fieldsString):
    fields = []
    matchesField = re.finditer(regexFields, fieldsString)
    for pi, i in enumerate(matchesField):
        group = i.groups()
        field = {
            "name": group[0],
            "type": group[1],
            "options": buildFieldOption(group[2])
        }
        fields += [field]
    return fields

def buildTableOption(tableOptionString):
    return None

def buildTables(tableString):
    result = {"Table": []}
    matches = re.finditer(regexTables, tableString, re.MULTILINE | re.VERBOSE | re.DOTALL)
    for matchNum, match in enumerate(matches, start=1):
        group = match.groups()
        table = {
            "name": group[0],
            "shortName": group[1],
            "option": buildTableOption(group[2]),
            "fields": buildFields(group[3])
        }
        result["Table"] += [table]
    return result

print("Generating")
now = time.time()

dbdiagraminput = open(inputPath, 'r').read().replace('"',"'")

tableObject = buildTables(dbdiagraminput)
tableOutput = json.dumps(tableObject, indent=4)

open(outputPath, 'w').write(tableOutput)

print("\nGenerate succeeded", len(tableObject["Table"]),
      "tables in {0:0.4f} second(s)".format(time.time()-now))
