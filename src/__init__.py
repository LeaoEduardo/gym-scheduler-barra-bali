import os

BUCKET_NAME = os.environ.get("BUCKET_NAME", None)
BOT_TOKEN = os.environ.get('BOT_TOKEN', None)
WEBHOOK = os.environ.get('WEBHOOK', None)
PORT = int(os.environ.get('PORT', 5000))
TIMEZONE = os.environ.get('TIMEZONE', 'America/Sao_Paulo')

days_of_the_week = {
    0: 'Segunda',
    1: 'Terça',
    2: 'Quarta',
    3: 'Quinta',
    4: 'Sexta',
    5: 'Sábado',
    6: 'Domingo',
}

translate = {
    "hoje": "today",
    "hj": "today",
    "amanhã": "tomorrow",
    "amanha": "tomorrow",
    "amn": "tomorrow",
    "musc": "musc",
    "musculacao": "musc",
    "musculação": "musc",
    "musculaçao": "musc",
    "aerobio":"aerobio",
    "aer":"aerobio",
    "aeróbio": "aerobio",
    "salinha":"salinha",
    "sala": "salinha"
}

inverse_translate = {
    "today":"hoje",
    "tomorrow": "amanhã",
    "musc": "musculação",
    "aerobio": "aeróbio",
}