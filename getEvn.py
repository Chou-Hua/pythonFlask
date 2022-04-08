import os
import json

def getPrivateKey():
    key = 'private_key'
    value = os.getenv(key)   
    id_key = 'private_key_id'
    id_value = os.getenv(id_key)
    keyDict = {key:value,id_key:id_value}    
    with open('api/pkey.json', 'r') as openfile:    
        json_object = json.load(openfile)
    json_object.update(keyDict)
    covet_json = json.dumps(json_object)
    return json.loads(covet_json)