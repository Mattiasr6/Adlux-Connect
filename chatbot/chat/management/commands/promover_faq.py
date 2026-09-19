from pathlib import Path

import chromadb
from chromadb.utils import embedding_functions
from django.conf import settings
from django.core.management.base import BaseCommand
from sentence_transformers import SentenceTransformer

from chat.models import Interaction

MODELO_EMBEDDINGS = 'all-mpnet-base-v2'
COLECCION = 'hospital_qanda2'


class Command(BaseCommand):
    help = 'Promueve a la FAQ las respuestas con feedback >= umbral. Idempotente.'

    def add_arguments(self, parser):
        parser.add_argument('--umbral', type=int, default=3,
                            help='Feedback mínimo para promover (default: 3).')

    def handle(self, *args, umbral, **opciones):
        persist = str(Path(settings.BASE_DIR) / 'chat' / 'appollo_chatbot_chroma2')
        cliente = chromadb.PersistentClient(path=persist)
        ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=MODELO_EMBEDDINGS)
        col = cliente.get_or_create_collection(name=COLECCION, metadata={'hnsw:space': 'cosine'}, embedding_function=ef)

        existentes = set(col.get()['ids'])
        buenas = Interaction.objects.filter(feedback__gte=umbral).order_by('created_at')
        modelo = SentenceTransformer(MODELO_EMBEDDINGS)
        nuevas = 0
        for inter in buenas:
            # El id en Chroma es el UUID de la Interaction: procedencia
            # incluida y segunda pasada gratis (ya existe -> se omite).
            pid = str(inter.interaction_id)
            if pid in existentes:
                continue
            emb = modelo.encode([inter.user_message.lower()])[0].tolist()
            col.add(ids=[pid], documents=[inter.bot_response],
                    metadatas=[{'source': pid, 'question': inter.user_message}],
                    embeddings=[emb])
            nuevas += 1
        self.stdout.write(self.style.SUCCESS(
            f'{nuevas} promovidas (umbral {umbral}). Total en {COLECCION}: {col.count()}'))
