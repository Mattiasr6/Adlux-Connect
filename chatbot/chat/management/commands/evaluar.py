import json

from django.core.management.base import BaseCommand
from django.test import Client
from django.test.utils import setup_test_environment

# Set HSJD: pares curados + 2 fuera de alcance (prueban honestidad).
PREGUNTAS = [
    '¿Dónde queda el hospital?',
    '¿Cómo saco una ficha digital?',
    '¿Qué es la hoja de referencia?',
    '¿Cuántas especialidades tienen?',
    '¿Atienden niños o pediatría?',
    '¿Atienden con el SUS?',
    '¿Cuáles son los horarios de visita para internados?',
    '¿Cuál es el teléfono del hospital?',
    'Who won the 2026 world cup?',
    'conoces los vectores bidimensionales en c#?',
]


class Command(BaseCommand):
    help = 'Corre el set de evaluación y muestra latencia y fuente por pregunta.'

    def handle(self, *args, **opciones):
        setup_test_environment()
        c = Client()
        if not c.login(username='admin', password='admin123'):
            self.stderr.write('no se pudo entrar como admin')
            return

        filas, con_fuente = [], 0
        for q in PREGUNTAS:
            r = c.post('/chat/', data=json.dumps({'message': q}), content_type='application/json')
            d = r.json()
            lat = str(d.get('response_time', '-'))
            fuente = d.get('fuente') or '-'
            if fuente != '-':
                con_fuente += 1
            filas.append((q, lat, fuente, (d.get('response') or '')[:100].replace('\n', ' ')))

        self.stdout.write('| pregunta | latencia | fuente | respuesta |')
        self.stdout.write('|---|---|---|---|')
        for q, lat, fuente, resp in filas:
            self.stdout.write(f'| {q} | {lat} | {fuente[:60]} | {resp} |')
        self.stdout.write(f'\ncon fuente: {con_fuente}/{len(filas)}')
