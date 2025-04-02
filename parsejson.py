import json

with open('myfile_12214737.json','r') as json_file:
    ourjson = json.load(json_file)
    print(ourjson)