# api/routes/usuarios.py
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from api.deps import get_conn, get_usuario_atual, requer_admin
from core import auth as auth_core

router = APIRouter(prefix="/usuarios", tags=["Usuários"])


# ── Schemas ──────────────────────────────────────────────────
class UsuarioCreate(BaseModel):
    nome:             str
    login:            str
    email:            Optional[str] = None
    cargo:            Optional[str] = None
    senha:            str
    confirmar_senha:  str
    nivel:            str


class UsuarioUpdate(BaseModel):
    nome:   Optional[str] = None
    email:  Optional[str] = None
    cargo:  Optional[str] = None
    nivel:  Optional[str] = None
    ativo:  Optional[bool] = None


class SenhaAdminBody(BaseModel):
    senha_nova: str
    confirmar:  str


class MinhaSenhaBody(BaseModel):
    senha_atual: str
    senha_nova:  str
    confirmar:   str


# ── ALTERAR MINHA SENHA ──────────────────────────────────────
# Esta rota precisa ficar ANTES de /{usuario_id}
@router.patch("/me/senha")
def alterar_minha_senha(
    body: MinhaSenhaBody,
    conn=Depends(get_conn),
    usuario=Depends(get_usuario_atual)
):
    auth_core._sessao["usuario"] = usuario

    ok, msg = auth_core.trocar_minha_senha(
        conn,
        body.senha_atual,
        body.senha_nova,
        body.confirmar
    )

    if not ok:
        raise HTTPException(status_code=400, detail=msg)

    return {"mensagem": msg}


# ── ROTAS ADMIN ──────────────────────────────────────────────

@router.get("/")
def listar(conn=Depends(get_conn), _=Depends(requer_admin)):
    return auth_core.listar_usuarios(conn)


@router.get("/{usuario_id}")
def detalhe(
    usuario_id: int,
    conn=Depends(get_conn),
    _=Depends(requer_admin)
):
    u = auth_core.buscar_usuario_por_id(conn, usuario_id)

    if not u:
        raise HTTPException(
            status_code=404,
            detail="Usuário não encontrado."
        )

    return u


@router.post("/")
def cadastrar(
    dados: UsuarioCreate,
    conn=Depends(get_conn),
    admin=Depends(requer_admin)
):
    auth_core._sessao["usuario"] = admin

    ok, msg = auth_core.cadastrar_usuario(
        conn,
        dados.dict(),
        criado_por=admin
    )

    if not ok:
        raise HTTPException(status_code=400, detail=msg)

    return {"mensagem": msg}


@router.put("/{usuario_id}")
def editar(
    usuario_id: int,
    dados: UsuarioUpdate,
    conn=Depends(get_conn),
    admin=Depends(requer_admin)
):
    auth_core._sessao["usuario"] = admin

    ok, msg = auth_core.editar_usuario(
        conn,
        usuario_id,
        dados.dict(exclude_none=True)
    )

    if not ok:
        raise HTTPException(status_code=400, detail=msg)

    return {"mensagem": msg}


@router.patch("/{usuario_id}/senha")
def alterar_senha_admin(
    usuario_id: int,
    body: SenhaAdminBody,
    conn=Depends(get_conn),
    admin=Depends(requer_admin)
):
    auth_core._sessao["usuario"] = admin

    ok, msg = auth_core.alterar_senha(
        conn,
        usuario_id,
        body.senha_nova,
        body.confirmar,
        alterado_por_admin=True
    )

    if not ok:
        raise HTTPException(status_code=400, detail=msg)

    return {"mensagem": msg}


@router.patch("/{usuario_id}/desativar")
def desativar(
    usuario_id: int,
    conn=Depends(get_conn),
    admin=Depends(requer_admin)
):
    auth_core._sessao["usuario"] = admin

    ok, msg = auth_core.desativar_usuario(
        conn,
        usuario_id
    )

    if not ok:
        raise HTTPException(status_code=400, detail=msg)

    return {"mensagem": msg}


@router.patch("/{usuario_id}/reativar")
def reativar(
    usuario_id: int,
    conn=Depends(get_conn),
    admin=Depends(requer_admin)
):
    auth_core._sessao["usuario"] = admin

    ok, msg = auth_core.reativar_usuario(
        conn,
        usuario_id
    )

    if not ok:
        raise HTTPException(status_code=400, detail=msg)

    return {"mensagem": msg}
