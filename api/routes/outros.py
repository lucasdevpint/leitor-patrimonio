# api/routes/outros.py
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
from api.deps import get_conn, get_usuario_atual, requer_editor, requer_admin
from core import movimentacao as mov_core
from core import dashboard as dash_core
from core import manutencao as man_core
from core import auditoria as aud_core
from core import inventario as inv_core
from core import relatorios as rel_core

router = APIRouter(tags=["Outros"])


# ── Movimentação ─────────────────────────────────────────────
class MoverBody(BaseModel):
    codigo:       str
    novo_local_id: int


@router.post("/movimentacoes")
def mover(body: MoverBody, conn=Depends(get_conn), _=Depends(requer_editor)):
    ok, msg = mov_core.movimentar_patrimonio(conn, body.codigo, body.novo_local_id)
    if not ok:
        raise HTTPException(status_code=400, detail=msg)
    return {"mensagem": msg}


@router.get("/movimentacoes/{codigo}")
def historico(codigo: str, conn=Depends(get_conn), _=Depends(get_usuario_atual)):
    hist = mov_core.historico_patrimonio(conn, codigo)
    return [{"data": str(h["data_movimentacao"])[:16],
             "origem": h["origem"], "destino": h["destino"]} for h in hist]


# ── Dashboard ────────────────────────────────────────────────
@router.get("/dashboard")
def dashboard(conn=Depends(get_conn), _=Depends(get_usuario_atual)):
    return dash_core.obter_estatisticas(conn)


# ── Inventário ───────────────────────────────────────────────
@router.get("/inventario")
def inventario(local_id: Optional[int] = None,
               conn=Depends(get_conn), _=Depends(get_usuario_atual)):
    return inv_core.listar_por_local(conn, local_id)


# ── Manutenção ───────────────────────────────────────────────
class ManutencaoBody(BaseModel):
    patrimonio_id: int
    tipo:          str
    descricao:     Optional[str] = None
    data_prevista: str
    responsavel:   Optional[str] = None
    custo:         Optional[float] = None


class ConcluirBody(BaseModel):
    data_realizada: str
    custo:          Optional[float] = None


@router.get("/manutencoes/pendentes")
def manutencoes_pendentes(conn=Depends(get_conn), _=Depends(get_usuario_atual)):
    dados = man_core.listar_pendentes(conn)
    return [{**d, "data_prevista": str(d["data_prevista"])} for d in dados]


@router.get("/manutencoes/alertas")
def alertas(dias: int = 7, conn=Depends(get_conn), _=Depends(get_usuario_atual)):
    dados = man_core.alertas_proximos(conn, dias)
    return [{**d, "data_prevista": str(d["data_prevista"])} for d in dados]


@router.post("/manutencoes")
def agendar(body: ManutencaoBody, conn=Depends(get_conn), _=Depends(requer_editor)):
    ok, msg = man_core.agendar(conn, body.patrimonio_id, body.dict())
    if not ok:
        raise HTTPException(status_code=400, detail=msg)
    return {"mensagem": msg}


@router.patch("/manutencoes/{manutencao_id}/concluir")
def concluir(manutencao_id: int, body: ConcluirBody,
             conn=Depends(get_conn), _=Depends(requer_editor)):
    ok, msg = man_core.registrar_realizada(
        conn, manutencao_id, body.data_realizada, body.custo)
    if not ok:
        raise HTTPException(status_code=400, detail=msg)
    return {"mensagem": msg}


# ── Auditoria (admin) ────────────────────────────────────────
@router.get("/auditoria")
def auditoria_logs(limite: int = 200, usuario_login: Optional[str] = None,
                   acao: Optional[str] = None,
                   conn=Depends(get_conn), _=Depends(requer_admin)):
    logs = aud_core.listar_logs(conn, limite, usuario_login, acao)
    return [{**l, "criado_em": str(l["criado_em"])} for l in logs]


# ── Relatórios ───────────────────────────────────────────────
@router.get("/relatorios/excel")
def relatorio_excel(conn=Depends(get_conn), usuario=Depends(requer_editor)):
    caminho, msg = rel_core.gerar_relatorio_completo(conn)
    if not caminho:
        raise HTTPException(status_code=500, detail=msg)
    aud_core.registrar(conn, "EXPORTAR",
                       f"Relatório Excel gerado via app web.", "relatorios")
    import os
    return FileResponse(
        caminho,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=os.path.basename(caminho)
    )
