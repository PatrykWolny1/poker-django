#!/bin/bash
CUDA_VISIBLE_DEVICES="" daphne -e ssl:8000:privateKey=key.pem:certKey=cert.pem pokerweb.asgi:application
