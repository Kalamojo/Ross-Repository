import os.path
import sqlite3
import cohere
import numpy as np
import os
from dotenv import load_dotenv
from sklearn.feature_extraction.text import TfidfVectorizer
import pickle
import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords
from scipy import sparse

version = '_old'

load_dotenv()

cohere_key = os.getenv("COHERE_API_KEY")
co = cohere.Client(cohere_key)
stop_words = list(stopwords.words('english'))

def give_list(db, name=''):
	if len(name) != 0:
		res_table = db.execute(f'SELECT * FROM {name}')
		rows = [row[0] for row in res_table]
		return rows
	else:
		rows = [row[0] for row in db]
		return rows

def get_table(db, name, orderBy):
    table_list = []
    res_table = db.execute(f'SELECT * FROM {name} ORDER BY {orderBy}')
    rows = [[item[0] for item in res_table.description][:-1]] + [row for row in res_table]
    lens = []
    for col in zip(*rows):
        lens.append(max([len(str(v)) for v in col]))
    format = "  ".join(["{:." + str(l) + "}" for l in lens])
    for row in rows:
        row = [str(x) for x in row]
        table_list.append(format.format(*row))
    return table_list[1:]

con = sqlite3.connect(f'courtCases{version}.db')
cur = con.cursor()

command = """
SELECT content
FROM Cases C
ORDER BY decision_date ASC
"""
res_table = cur.execute(command)
docs = give_list(res_table)
tableList = get_table(cur, 'Cases', 'decision_date')
docs_clean = [doc.replace("\n"," ") for doc in docs]
full_docs = [n + " " + m for n, m in zip(tableList, docs_clean)]

doc_emb = co.embed(docs, input_type="search_document", model="embed-english-v3.0").embeddings
doc_emb = np.asarray(doc_emb)
np.save(f"case_embeddings{version}.npy", doc_emb)

vectorizer = TfidfVectorizer(ngram_range=(2, 2), stop_words=stop_words)
doc_tfidf = vectorizer.fit_transform(full_docs)
sparse.save_npz(f"case_tfidf{version}.npz", doc_tfidf)
with open(f'vectorizer{version}.pk', 'wb') as f:
    pickle.dump(vectorizer, f)

doc_emb = sparse.csr_matrix(doc_emb)
final_emb = sparse.hstack((doc_emb, doc_tfidf))
sparse.save_npz(f"final_embeddings{version}.npz", final_emb)
