FROM python:3.12-slim

WORKDIR .

COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

ENV IS_DEV="yes"
ENV redis_url=redis://localhost

CMD ["daphne", "-e", "ssl:8000:privateKey=key.pem:certKey=cert.pem", "pokerweb.asgi:application"]
