# api/routes/auth.py
import hashlib
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from api.deps import get_conn, criar_token, get_usuario_atual
from core import auditoria

router = APIRouter(prefix="/auth", tags=["Auth"])


def _hash(senha: str) -> str:
    return hashlib.sha256(senha.encode()).hexdigest()


@router.post("/login")
def login(
    form: OAuth2PasswordRequestForm = Depends(),
    conn=Depends(get_conn)
):
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT id, nome, login, nivel, ativo, senha_hash FROM usuarios WHERE login = %s",
        (form.username,)
    )
    usuario = cursor.fetchone()
    cursor.close()

    if not usuario or not usuario["ativo"]:
        raise HTTPException(status_code=401, detail="Usuário não encontrado ou inativo.")

    if usuario["senha_hash"] != _hash(form.password):
        raise HTTPException(status_code=401, detail="Senha incorreta.")

    auditoria.registrar(conn, "LOGIN", f"Login via API — usuário {form.username}")

    token = criar_token({"sub": usuario["login"], "nivel": usuario["nivel"]})
    return {
        "access_token": token,
        "token_type":   "bearer",
        "usuario": {
            "nome":  usuario["nome"],
            "login": usuario["login"],
            "nivel": usuario["nivel"],
        }
    }


@router.get("/me")
def me(usuario=Depends(get_usuario_atual)):
    return usuario
