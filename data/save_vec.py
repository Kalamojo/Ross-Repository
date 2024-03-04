import numpy as np
from scipy import sparse

doc_emb = np.load(f"case_embeddings.npy")
doc_tfidf = sparse.load_npz(f"case_tfidf.npz")
doc_emb = sparse.csr_matrix(doc_emb)
doc_tfidf = sparse.csr_matrix(doc_tfidf)

final_emb = sparse.hstack((doc_emb, doc_tfidf))

sparse.save_npz(f"final_embeddings.npz", final_emb)