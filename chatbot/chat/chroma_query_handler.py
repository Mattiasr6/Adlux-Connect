from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer

MODELO = 'all-mpnet-base-v2'
COLECCION = 'hospital_qanda2'

model = None
client = None


def _persist_path():
    # Junto a este archivo: no depende del directorio de trabajo.
    return str(Path(__file__).resolve().parent / 'appollo_chatbot_chroma2')


def setup_chroma_client():
    global client, model
    model = SentenceTransformer(MODELO)
    client = chromadb.PersistentClient(path=_persist_path())


def get_query_embedding(query):
    return model.encode([query.lower()])[0].tolist()


def retrieve_documents(query, top_k=3):
    """Devuelve (texto, pregunta_origen) del mejor documento, o (None, None)."""
    if client is None:
        return None, None
    try:
        collection = client.get_collection(COLECCION)
    except Exception:
        return None, None
    res = collection.query(query_embeddings=[get_query_embedding(query)], n_results=top_k)
    docs = res.get('documents', [[]])[0]
    metas = res.get('metadatas', [[{}]])[0]
    if not docs:
        return None, None
    meta = metas[0] if metas else {}
    return docs[0], meta.get('question', meta.get('source', ''))
