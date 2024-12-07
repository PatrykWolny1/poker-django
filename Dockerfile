FROM python:3.9-slim

WORKDIR /poker-django

COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
EXPOSE 443

ENV PATH="/usr/local/bin/:$PATH"
ENV REDIS_URL="redis://red-ct7i211u0jms73drikm0:6379"
ENV DJANGO_SETTINGS_MODULE="pokerweb.settings"
ENV DJANGO_ALLOWED_HOSTS="pokersimulation.onrender.com"
ENV IS_DEV="no"

CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "pokerweb.asgi:application"]
