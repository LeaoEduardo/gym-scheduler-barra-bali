FROM python:3.8-slim

WORKDIR /app

COPY bot.py /app
COPY schedule.json /app
COPY requirements.txt /app

RUN pip install -r requirements.txt

CMD ["python", "bot.py"]