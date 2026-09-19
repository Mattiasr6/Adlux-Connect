import json
import os
from pathlib import Path

import chromadb
from chromadb.utils import embedding_functions
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils.translation import gettext as _
from sentence_transformers import SentenceTransformer

MODELO_EMBEDDINGS = 'all-mpnet-base-v2'
COLECCION = os.environ.get('COLECCION_FAQ', 'hospital_qanda2')


class Command(BaseCommand):
    help = _('Index Q&A pairs from a JSON file into Chroma. Idempotent: skips existing ids.')

    def add_arguments(self, parser):
        parser.add_argument('--archivo', default='chat/data/faq_semilla.json',
                            help=_('Path to the JSON file (relative to BASE_DIR or absolute).'))
        parser.add_argument('--coleccion', default=COLECCION)

    def handle(self, *args, archivo, coleccion, **opciones):
        ruta = Path(archivo)
        if not ruta.is_absolute():
            ruta = Path(settings.BASE_DIR) / ruta
        if not ruta.exists():
            raise CommandError(_('missing file: {path}').format(path=ruta))
        pares = json.loads(ruta.read_text(encoding='utf-8'))

        persist = str(Path(settings.BASE_DIR) / 'chat' / 'appollo_chatbot_chroma2')
        cliente = chromadb.PersistentClient(path=persist)
        ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=MODELO_EMBEDDINGS)
        col = cliente.get_or_create_collection(name=coleccion, metadata={'hnsw:space': 'cosine'}, embedding_function=ef)

        existentes = set(col.get()['ids'])
        modelo = SentenceTransformer(MODELO_EMBEDDINGS)
        nuevos = 0
        for i, par in enumerate(pares):
            pid = par.get('id', f'semilla_{i}')
            if pid in existentes:
                continue
            emb = modelo.encode([par['question'].lower()])[0].tolist()
            col.add(ids=[pid], documents=[par['answer']],
                    metadatas=[{'source': pid, 'question': par['question']}],
                    embeddings=[emb])
            nuevos += 1
        self.stdout.write(self.style.SUCCESS(
            _('{new} new, {existing} already indexed. Total in {collection}: {total}').format(
                new=nuevos, existing=len(existentes), collection=coleccion, total=col.count())))
