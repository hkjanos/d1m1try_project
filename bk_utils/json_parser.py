import json

def parse(filePath):
    # This function parse a json file into az output table
    # which is then returned for usage in the program.
    with open(filePath) as json_file:
        table = json.load(json_file)
    return table
