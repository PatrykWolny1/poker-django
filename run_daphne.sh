#!/bin/bash
daphne -e ssl:8000:privateKey=key.pem:certKey=cert.pem pokerweb.asgi:application
