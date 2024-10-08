from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer


# Load the sentence transformer model
model = SentenceTransformer('all-mpnet-base-v2')
es_client = Elasticsearch("http://localhost:9200")

def elastic_search(query):
    query_body = {
        "size": 1,
        "query": {
            "match": {
                "itinerary": query
            }
        },
        "fields": ["plan"]
    }
    response = es_client.search(index="tip-index", body=query_body)
    
    response_docs = []
    for hit in response["hits"]["hits"]:
        response_docs.append(hit["_source"])
        
    plan = response_docs[0]['plan']

    return plan.strip(), response_docs[0]['itinerary']

def elastic__vector_search(query):

    vec_query = model.encode(query).tolist()
    
    query = {
        "knn": {
            "field": "itin_vector",
            "query_vector": vec_query,
            "k": 1,
            "num_candidates": 1000
            
            },
        "fields": ["plan"]
        }
    response = es_client.search(index="vec-index", body=query)

    response_docs = []
    for hit in response["hits"]["hits"]:
        response_docs.append(hit["_source"])
        
    plan = response_docs[0]['plan']

    return plan.strip(), response_docs[0]['itinerary']


def fais__vector_search(query):
    
    query_embedding = model.encode([query]).astype(np.float32)
    
    # Perform the search (k=5 means returning the 5 most similar entries)
    D, I = index.search(query_embedding, k=1)

    # D contains the distances, I contains the indices of the nearest neighbors
    plan = text_data[I[0][0]]
    return plan.strip(), I[0][0]
    