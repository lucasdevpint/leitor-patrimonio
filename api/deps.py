# api/deps.py
# Dependências injetadas nas rotas via FastAPI Depends().

from fastapi import Depends, HTTPException, status, Query
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
import hashlib

from api.config import SECRET_KEY, ALGORITHM, TOKEN_HORAS
from db.banco import conectar

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)


# ── Banco ────────────────────────────────────────────────────
def get_conn():
    conn = conectar()
    try:
        yield conn
    finally:
        conn.close()


# ── JWT ──────────────────────────────────────────────────────
def criar_token(dados: dict) -> str:
    payload = dados.copy()
    payload["exp"] = datetime.utcnow() + timedelta(hours=TOKEN_HORAS)
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def _validar_token(token: str, conn):
    erro = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido ou expirado.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        login: str = payload.get("sub")
        if not login:
            raise erro
    except JWTError:
        raise erro

    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT id, nome, login, nivel, ativo FROM usuarios WHERE login = %s",
        (login,)
    )
    usuario = cursor.fetchone()
    cursor.close()

    if not usuario or not usuario["ativo"]:
        raise erro
    return usuario


def get_usuario_atual(
    token: Optional[str] = Depends(oauth2_scheme),
    token_query: Optional[str] = Query(None, alias="token"),
    conn=Depends(get_conn)
):
    """
    Aceita o token via header Authorization (uso normal da API)
    OU via querystring ?token=... (necessário para downloads abertos
    em nova aba, onde não é possível enviar headers customizados).
    """
    usado = token or token_query
    if not usado:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token não fornecido.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return _validar_token(usado, conn)


def requer_editor(usuario=Depends(get_usuario_atual)):
    hierarquia = {"admin": 3, "editor": 2, "visualizador": 1}
    if hierarquia.get(usuario["nivel"], 0) < 2:
        raise HTTPException(status_code=403, detail="Sem permissão.")
    return usuario


def requer_admin(usuario=Depends(get_usuario_atual)):
    if usuario["nivel"] != "admin":
        raise HTTPException(status_code=403, detail="Requer nível admin.")
    return usuario
