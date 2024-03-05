import sqlite3
from sqlite3 import Cursor
from scraper import LawScraper
from datetime import datetime

def print_table(db: Cursor, name: str) -> None:
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

scraper = LawScraper(headless=True)
start_date = datetime(1760, 1, 1)
end_date = datetime(2024, 12, 31)
caseDict = scraper.get_cases(start_date, end_date, pageStart=1, pageLimit=300)

con = sqlite3.connect('courtCases.db')
cur = con.cursor()

command = """
CREATE TABLE Cases (
    name text,
    citation text,
    docket_no text,
    decision_date date,
    court text,
    content text,
    url text,
    PRIMARY KEY (citation)
);
"""
cur.execute(command)

for case in caseDict:
    cur.execute("INSERT INTO Cases VALUES (?, ?, ?, ?, ?, ?)", 
                (case['name'], case.get("Citation", None), case.get("Docket No", None), 
                 datetime.strptime(case['Decided'], ' %B %d, %Y').strftime("%Y-%m-%d"), 
                 case['Court'], case['content'], case['url']))

con.commit()
print_table(cur, "Cases")
