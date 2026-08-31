# api/app.py
# Ponto de entrada da API REST.
# Rode com: uvicorn api.app:app --host 0.0.0.0 --port 8000 --reload

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from api.config import CORS_ORIGINS
from api.routes import auth, patrimonios, outros, usuarios, visitantes, importacao
app = FastAPI(
    title="Sistema Patrimonial API",
    description="API REST do sistema de controle patrimonial.",
    version="3.0.0",
)

# CORS — permite que o app web no celular acesse a API
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rotas da API
app.include_router(auth.router)
app.include_router(patrimonios.router)
app.include_router(outros.router)
app.include_router(usuarios.router)
app.include_router(visitantes.router)
app.include_router(importacao.router)

# Serve o app web (frontend) na raiz
FRONTEND = os.path.join(os.path.dirname(__file__), "..", "web")
if os.path.exists(FRONTEND):
    app.mount("/static", StaticFiles(directory=FRONTEND), name="static")

    @app.get("/app")
    def frontend():
        return FileResponse(os.path.join(FRONTEND, "index.html"))


@app.get("/")
def raiz():
    return {
        "sistema": "Patrimônio API",
        "versao":  "3.0.0",
        "docs":    "/docs",
        "app_web": "/app",
    }
