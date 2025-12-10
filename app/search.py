import json
import os
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"    # ligth & fast model for retrieval | MiniLM is a compressed Transformer
INDEX_DIR = "index"                                      # folder for what concerns the index files
META_PATH = os.path.join(INDEX_DIR, 'meta.json')         # meta.json is the metadata dictionnairy
INDEX_PATH = os.path.join(INDEX_DIR, 'faiss_index.bin')  # binary file containing thousands of vectors  


"""
Load the model only one time, at the start of the program.
It avoids to load the model at each request, which makes the system faster.
"""
model = SentenceTransformer(MODEL_NAME)  



########################################
########## load JSONL files  ########### 
########################################

def load_documents(jsonl_path="data/processed/documents.jsonl"):
    docs = []
    with open(jsonl_path, "r", encoding="utf-8") as f:
        for line in f:
            docs.append(json.loads(line))
    return docs



########################################
######## build FAISS index  ############
########################################

def build_faiss_index(jsonl_path="data/processed/documents.jsonl"):
    docs = load_documents(jsonl_path)
    texts = [doc['text'] for doc in docs]  # extract all text and only text from documents -> strings list
    
    """Generate embedding """
    embeddings = model.encode(texts, convert_to_numpy=True, show_progress_bar=True)  # model.encode() transform each text into vectors (approx. 384)
                                                                                     # convert_to_numpy=True -> return numpy array float32 due to FAISS
    
    """ Vector sizes """
    dim = embeddings.shape[1]  # get the dimension of each vector (384 for MiniLM) --> FAISS needs to know each vector's size


    """ Create FAISS index """
    index = faiss.IndexFlatL2(dim)  # build the index with L2 distance metric. Flat is for no compression. L2 is for Euclidian distances/metrics wich are faster


    """ Add vectors in FAISS """
    index.add(embeddings)           # add all vectors to the index and add an ID to each vector from the embedding


    """ Save index to disk """
    faiss.write_index(index, INDEX_PATH)  # save the index in a binary file -> faiss_index.bin contains all the vectors + the FAISS structure -> will be able to reload without recalculate the embeddings

    """ Save metadata to """
    meta = {i: {"id": docs[i]["id"], "title": docs[i]["title"]} for i in range(len(docs))} # create a dictionnary making a link between the FAISS index and the real document (id+title)
    with open(META_PATH, 'w', encoding='utf-8') as f:
        json.dump(meta, f, indent=2) # save the meta dictionnary in meta.json
    # meta.json contains the mapping: which document is linked with which vector, which title is linked with which vector, etc...
    # meta.json is a linker

    print(f"FAISS index created -> {INDEX_PATH}")
    print(f"Metadata saved -> {META_PATH}")



#####################################
####### Load the FAISS index ########
#####################################

def load_index():
    index = faiss.read_index(INDEX_PATH)  # load the FAISS file in memory
    with open(META_PATH, 'r', encoding='utf-8') as f:
        meta = json.load(f)                # load the matadata
    return index, meta



#####################################
####### Semantic Search #############
#####################################

def semantic_search(query: str, top_k: int =5):
    index, meta = load_index()                    # load the index and metadata (index in memory)

    """Encode the query"""
    query_embedding = model.encode([query], convert_to_numpy=True) # encode the query to get the vector representation in 384D


    """ Search in FAISS """
    distances, indices = index.search(query_embedding, top_k) # search the closest top_k vectors 
                                                              # return 2 matrix: L2 distance for each result, and FAISS index (ex: 0, 5, 12...)
    results = []
    for score, idx in zip(distances[0], indices[0]):  # distance[0] is a table containing the scores of the top_k results & indices[0] the FAISS corresponding indices
        doc_meta = meta[str(idx)]  # get the metadata for the document
        results.append({
            "doc_id": doc_meta["id"],
            "title": doc_meta["title"],
            "score": float(score)   # L2 distance score
        })
    return results
