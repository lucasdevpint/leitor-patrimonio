# api/config.py
# Configurações da API — chave JWT e CORS.

import os

# Troque essa chave por algo longo e aleatório em produção
SECRET_KEY  = os.getenv("SECRET_KEY", "patrimonio-sistema-chave-secreta-2024")
ALGORITHM   = "HS256"
TOKEN_HORAS = 8   # token expira em 8 horas

# Origens permitidas (em produção coloque o IP/domínio do servidor)
CORS_ORIGINS = ["*"]
