FROM python:3.8-slim

WORKDIR /app

COPY requirements.txt /app

RUN pip install -r requirements.txt

COPY src/* /app/src/
COPY artifacts/* /app/

CMD ["python", "-m", "src.app", "None"]