#!/bin/bash
source ~/django/bin/activate
export REDIS_URL='redis://127.0.0.1:6379/1'
sudo systemctl enable redis-server
CUDA_VISIBLE_DEVICES="" daphne -e ssl:8000:privateKey=key.pem:certKey=cert.pem pokerweb.asgi:application
