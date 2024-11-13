FROM python:3.9-slim

WORKDIR /poker-django

COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["daphne" "-e" "ssl:8000:privateKey=key.pem:certKey=cert.pem" "pokerweb.asgi:application"]