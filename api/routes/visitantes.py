# api/routes/visitantes.py
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from api.deps import get_conn, get_usuario_atual, requer_admin
from core import visitantes as vis_core

router = APIRouter(prefix="/visitantes", tags=["Visitantes"])


class VisitanteCreate(BaseModel):
    nome:        str
    documento:   Optional[str] = None
    empresa:     Optional[str] = None
    telefone:    Optional[str] = None
    email:       Optional[str] = None
    observacoes: Optional[str] = None


class VisitanteUpdate(BaseModel):
    nome:        Optional[str] = None
    documento:   Optional[str] = None
    empresa:     Optional[str] = None
    telefone:    Optional[str] = None
    email:       Optional[str] = None
    observacoes: Optional[str] = None


@router.get("/")
def listar(conn=Depends(get_conn), _=Depends(requer_admin)):
    return vis_core.listar_visitantes(conn)


@router.get("/buscar/{termo}")
def buscar(termo: str, conn=Depends(get_conn), _=Depends(requer_admin)):
    return vis_core.buscar_visitantes(conn, termo)


@router.get("/{visitante_id}")
def detalhe(visitante_id: int, conn=Depends(get_conn), _=Depends(requer_admin)):
    v = vis_core.buscar_por_id(conn, visitante_id)
    if not v:
        raise HTTPException(status_code=404, detail="Visitante não encontrado.")
    return v


@router.post("/")
def cadastrar(dados: VisitanteCreate, conn=Depends(get_conn), _=Depends(requer_admin)):
    ok, msg = vis_core.cadastrar_visitante(conn, dados.dict())
    if not ok:
        raise HTTPException(status_code=400, detail=msg)
    return {"mensagem": msg}


@router.put("/{visitante_id}")
def editar(visitante_id: int, dados: VisitanteUpdate, conn=Depends(get_conn),
           _=Depends(requer_admin)):
    ok, msg = vis_core.editar_visitante(conn, visitante_id, dados.dict(exclude_none=True))
    if not ok:
        raise HTTPException(status_code=400, detail=msg)
    return {"mensagem": msg}


@router.patch("/{visitante_id}/desativar")
def desativar(visitante_id: int, conn=Depends(get_conn), _=Depends(requer_admin)):
    ok, msg = vis_core.desativar_visitante(conn, visitante_id)
    return {"mensagem": msg}


@router.patch("/{visitante_id}/reativar")
def reativar(visitante_id: int, conn=Depends(get_conn), _=Depends(requer_admin)):
    ok, msg = vis_core.reativar_visitante(conn, visitante_id)
    return {"mensagem": msg}
