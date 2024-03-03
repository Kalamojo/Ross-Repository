import os
import sqlite3
import pandas as pd
from scraper import LawScraper
from datetime import datetime
import json

def print_table(db, name):
    print(name + ':')
    res_table = db.execute(f'SELECT * FROM {name}')
    rows = [[item[0] for item in res_table.description]] + [row for row in res_table]
    lens = []
    for col in zip(*rows):
        lens.append(min(max([len(str(v)) for v in col]), 30))
    format = "  ".join(["{:." + str(l) + "}" for l in lens])
    for row in rows:
        row = [str(x) for x in row]
        print(format.format(*row))
    print('')

#"""
scraper = LawScraper(headless=True)
start_date = datetime(1760, 1, 1)
end_date = datetime(2024, 12, 31)
caseDict = scraper.get_cases(start_date, end_date, pageStart=1, pageLimit=300)
#"""

"""
with open("tempCases.json", 'r') as f:
    caseDict = json.load(f)
#"""

#os.remove("./courtCases.db")

con = sqlite3.connect('courtCases.db')
cur = con.cursor()

### Musicians table

command = """
CREATE TABLE Cases (
    name text,
    citation text,
    docket_no text,
    decision_date date,
    court text,
    content text,
    PRIMARY KEY (citation)
);
"""
cur.execute(command)
#"""
for case in caseDict:
    cur.execute("INSERT INTO Cases VALUES (?, ?, ?, ?, ?, ?)", 
                (case['name'], case.get("Citation", None), case.get("Docket No", None), case['Decided'], case['Court'], case['content']))
#"""
con.commit()
print_table(cur, "Cases")
