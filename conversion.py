import json
import os

def encode_cesar(string, decalage):
    minusules = "abcdefghijklmnopqrstuvwxyz"
    majuscules = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    res = ""
    for letter in string:
        if letter in minusules:
            ind = minusules.index(letter)
            ind = (ind+decalage)%26
            res_letter = minusules[ind]
        elif letter in majuscules:
            ind = majuscules.index(letter)
            ind = (ind+decalage)%26
            res_letter = majuscules[ind]
        else:
            res_letter = letter
        res = res+res_letter
    return res

def decode_cesar(string, decalage):
    return encode_cesar(string, -decalage)

# file_days = os.listdir("json_days")
# for file_name in file_days:
#     file_path = "json_days/"+file_name
#     with open(file_path, 'r') as f:
#         data = json.load(f)
#     day_tasks = data["tasks"]
#     for task in day_tasks:
#         task["infos"]["title"] = decode_cesar(task["infos"]["title"], 10)
#         task["infos"]["content"] = decode_cesar(task["infos"]["content"], 10)
#         task["infos"]["category"] = decode_cesar(task["infos"]["category"], 10)
#     with open(file_path, 'w+') as outfile:
#         json.dump(data, outfile, indent=4)
#
#
# file_path = "settings/"+"forbidden_websites.json"
# with open(file_path, 'r') as f:
#     data = json.load(f)
# sites = data["sites"]
# for i in range(len(sites)):
#     sites[i] = decode_cesar(sites[i], 10)
# with open(file_path, 'w+') as outfile:
#     json.dump(data, outfile, indent=4)
