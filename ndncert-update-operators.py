#!/usr/bin/env python3

from pymongo import MongoClient
import json
import argparse

parser = argparse.ArgumentParser(description='Update NDNCERT operators')
parser.add_argument('file', metavar='file', type=str, nargs='+', help='''operators.json file''')
args = parser.parse_args()

client = MongoClient()
db = client.ndncert

data = json.load(open(args.file[0]))

db.operators.remove()

for key, item in data.items():
    print(key)
    if type(item['site_emails']) == str:
        item['site_emails'] = [item['site_emails']]
    db.operators.insert(item)
