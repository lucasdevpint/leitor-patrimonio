# api/config.py
# Configurações da API — chave JWT e CORS.

import os

SECRET_KEY = os.getenv("SECRET_KEY")

if not SECRET_KEY:
    raise RuntimeError(
        "A variável de ambiente SECRET_KEY não foi configurada."
    )

ALGORITHM = "HS256"
TOKEN_HORAS = 8

# Origens permitidas
CORS_ORIGINS = ["*"]
