# api/routes/patrimonios.py
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from api.deps import get_conn, get_usuario_atual, requer_editor
from core import patrimonio as pat_core

router = APIRouter(prefix="/patrimonios", tags=["Patrimônios"])


# ── Schemas ──────────────────────────────────────────────────
class PatrimonioCreate(BaseModel):
    codigo:             str
    codigo_secundario:  Optional[str] = None
    tipo_patrimonio:    Optional[str] = None
    descricao:          Optional[str] = None
    marca:              Optional[str] = None
    modelo:             Optional[str] = None
    numero_serie:       Optional[str] = None
    status:             Optional[str] = "Disponível"
    local_id:           Optional[int] = None
    responsavel:        Optional[str] = None
    data_aquisicao:     Optional[str] = None
    valor:              Optional[float] = None
    observacoes:        Optional[str] = None


class PatrimonioUpdate(BaseModel):
    tipo_patrimonio:    Optional[str] = None
    descricao:          Optional[str] = None
    marca:              Optional[str] = None
    modelo:             Optional[str] = None
    numero_serie:       Optional[str] = None
    status:             Optional[str] = None
    responsavel:        Optional[str] = None
    data_aquisicao:     Optional[str] = None
    valor:              Optional[float] = None
    observacoes:        Optional[str] = None


class StatusUpdate(BaseModel):
    status: str


# ── Rotas ────────────────────────────────────────────────────
@router.get("/")
def listar(conn=Depends(get_conn), _=Depends(get_usuario_atual)):
    return pat_core.listar_patrimonios(conn)


@router.get("/buscar/{termo}")
def buscar(termo: str, conn=Depends(get_conn), _=Depends(get_usuario_atual)):
    return pat_core.buscar_patrimonios(conn, termo)


@router.get("/locais")
def listar_locais(conn=Depends(get_conn), _=Depends(get_usuario_atual)):
    return pat_core.listar_locais(conn)


@router.get("/{codigo}")
def detalhe(codigo: str, conn=Depends(get_conn), _=Depends(get_usuario_atual)):
    pat = pat_core.buscar_por_codigo(conn, codigo)
    if not pat:
        raise HTTPException(status_code=404, detail="Patrimônio não encontrado.")
    return pat


@router.post("/")
def cadastrar(dados: PatrimonioCreate, conn=Depends(get_conn),
              _=Depends(requer_editor)):
    ok, msg = pat_core.cadastrar_patrimonio(conn, dados.dict())
    if not ok:
        raise HTTPException(status_code=400, detail=msg)
    return {"mensagem": msg}


@router.put("/{codigo}")
def editar(codigo: str, dados: PatrimonioUpdate, conn=Depends(get_conn),
           _=Depends(requer_editor)):
    ok, msg = pat_core.editar_patrimonio(conn, codigo, dados.dict(exclude_none=True))
    if not ok:
        raise HTTPException(status_code=400, detail=msg)
    return {"mensagem": msg}


@router.patch("/{codigo}/status")
def alterar_status(codigo: str, body: StatusUpdate, conn=Depends(get_conn),
                   _=Depends(requer_editor)):
    ok, msg = pat_core.alterar_status(conn, codigo, body.status)
    if not ok:
        raise HTTPException(status_code=400, detail=msg)
    return {"mensagem": msg}
