import os.path
import sqlite3
import cohere
import numpy as np
import os
from dotenv import load_dotenv
import pickle
from scipy import sparse

version = '_old'

load_dotenv()

cohere_key = os.getenv("COHERE_API_KEY")
co = cohere.Client(cohere_key)

def cosine_sim(vector, matrix):
    scores = []
    for mat in matrix:
        cos_sim = np.dot(vector, mat.toarray()[0])/(np.linalg.norm(vector)*np.linalg.norm(mat.toarray()[0]))
        scores.append(cos_sim)
    return np.asarray(scores)

def give_lists(db, name, columns, rows):
    command = f"""
    SELECT {', '.join(columns)} FROM (
        SELECT ROW_NUMBER() OVER (ORDER BY decision_date) AS RowNum, *
        FROM {name} CA
    ) C
    WHERE C.RowNum IN {tuple(ind + 1 for ind in rows)}
    ORDER BY {', '.join([f'C.RowNum={ind+1} DESC' for ind in rows])}
    """
    res_table = db.execute(command)
    rows = [' '.join(row) for row in res_table]
    return rows

con = sqlite3.connect(f'./data/courtCases{version}.db')
cur = con.cursor()

document_matrix = sparse.load_npz(f'./data/final_embeddings{version}.npz')
with open(f'./data/vectorizer{version}.pk', 'rb') as f:
    vectorizer = pickle.load(f)

query = "What are the possible charges of stealing food from a grocery store?"
print("Query:", query)
query_emb = co.embed([query], input_type="search_query", model="embed-english-v3.0").embeddings
query_emb = np.asarray(query_emb)
query_tfidf = vectorizer.transform([query])
query_matrix = np.concatenate((query_emb[0], query_tfidf[0].toarray()[0]))

scores = cosine_sim(query_matrix, document_matrix)
max_idx = np.argsort(-scores)
print("Semantic/Term Search top three document indices:", max_idx[:5].tolist())

docs = give_lists(cur, 'Cases', ['name', 'content'], max_idx[:20])
results = co.rerank(query=query, documents=docs, top_n=3, model="rerank-english-v2.0")
result_indices = [max_idx[res.index] for res in results]

print("ReRanking top five document indices:", result_indices[:5])
