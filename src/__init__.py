import os

BUCKET_NAME = os.environ.get("BUCKET_NAME", None)
BOT_TOKEN = os.environ.get('BOT_TOKEN', None)
WEBHOOK = os.environ.get('WEBHOOK', None)
PORT = int(os.environ.get('PORT', 5000))

days_of_the_week = {
    0: 'Segunda',
    1: 'Terça',
    2: 'Quarta',
    3: 'Quinta',
    4: 'Sexta',
    5: 'Sábado',
    6: 'Domingo',
}