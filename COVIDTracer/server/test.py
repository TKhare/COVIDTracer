from enum import Enum
import json
import requests

class POSTTYPE(Enum):
    NEW = 1
    UPD = 2

BASE = 'http://127.0.0.1:5000/'

data = {'A_': {'type':1, 'name' : 'A', 'lat' : 40.47594627507722, 'lng' : -74.67324425826672},
        'B_': {'type':1, 'name' : 'B', 'lat' : 40.47986353452867, 'lng' : -74.66818024797742},
        'C_': {'type':1, 'name' : 'C', 'lat' : 40.47780700181534, 'lng' : -74.65822388876458},
        'D_': {'type':1, 'name' : 'D', 'lat' : 40.47372639326658, 'lng' : -74.67393090372967},
        'E_': {'type':1, 'name' : 'E', 'lat' : 40.47026584289723, 'lng' : -74.66521908941843}, 
        'F_': {'type':1, 'name' : 'F', 'lat': 40.474226029154735, 'lng' : -74.6668437527676},
        'G_': {'type':1, 'name' : 'G', 'lat': 40.4701679001974, 'lng' : -74.66745068717303}, 
        'H': {'type':1, 'name' : 'H', 'lat' : 40.470004662046954, 'lng' : -74.66101338595783}}

for key, value in data.items():
    print(requests.post(BASE + 'database/' + key, value).json())

requests.post(BASE + 'database/B_', {'type' : 2, 'lat' : 40.47, 'lng' : -74.67, 'list' : 'A_,G_'})
requests.post(BASE + 'database/G_', {'type' : 2, 'lat' : 40.47, 'lng' : -74.67, 'list' : 'D_'})
requests.post(BASE + 'database/C_', {'type' : 2, 'lat' : 40.47, 'lng' : -74.67, 'list' : 'H_'})
requests.post(BASE + 'database/F_', {'type' : 2, 'lat' : 40.47, 'lng' : -74.67, 'list' : 'E_'})

requests.post(BASE + 'database/G_', {'type' : 3, 'covid' : True})

print(requests.get(BASE + 'database/2').json()) 