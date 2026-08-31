# core/patrimonio.py
# Lógica pura de patrimônio — sem input(), sem print().
# Integrado com auditoria automática em toda operação de escrita.

import os
import shutil
from core import auditoria

STATUS_VALIDOS = ["Em uso", "Disponível", "Em manutenção", "Defeito", "Descarte"]

PASTA_FOTOS = os.path.join(os.path.dirname(__file__), "..", "assets", "fotos")
os.makedirs(PASTA_FOTOS, exist_ok=True)


# ── Leitura ──────────────────────────────────────────────────

def listar_patrimonios(conn):
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT
            p.id, p.codigo, p.codigo_secundario, p.tipo_patrimonio,
            p.descricao, p.marca, p.modelo, p.status,
            p.responsavel, p.data_aquisicao, p.valor, p.numero_serie,
            p.observacoes, l.nome AS local
        FROM patrimonio p
        LEFT JOIN locais l ON p.local_id = l.id
        ORDER BY p.codigo
    """)
    resultado = cursor.fetchall()
    cursor.close()
    return resultado


def buscar_patrimonios(conn, termo: str):
    cursor = conn.cursor(dictionary=True)
    v = f"%{termo}%"
    cursor.execute("""
        SELECT
            p.id, p.codigo, p.tipo_patrimonio, p.descricao,
            p.marca, p.modelo, p.status, p.responsavel, l.nome AS local
        FROM patrimonio p
        LEFT JOIN locais l ON p.local_id = l.id
        WHERE p.codigo LIKE %s OR p.descricao LIKE %s
           OR p.marca  LIKE %s OR p.modelo    LIKE %s
           OR p.tipo_patrimonio LIKE %s OR p.responsavel LIKE %s
           OR p.numero_serie LIKE %s
        ORDER BY p.codigo
    """, (v, v, v, v, v, v, v))
    resultado = cursor.fetchall()
    cursor.close()
    return resultado


def buscar_por_codigo(conn, codigo: str):
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT
            p.id, p.codigo, p.codigo_secundario, p.tipo_patrimonio,
            p.descricao, p.marca, p.modelo, p.status,
            p.responsavel, p.data_aquisicao, p.valor, p.numero_serie,
            p.observacoes, p.local_id, l.nome AS local
        FROM patrimonio p
        LEFT JOIN locais l ON p.local_id = l.id
        WHERE p.codigo = %s
    """, (codigo,))
    resultado = cursor.fetchone()
    cursor.close()
    return resultado


def listar_locais(conn):
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, nome FROM locais ORDER BY nome")
    resultado = cursor.fetchall()
    cursor.close()
    return resultado


def patrimonio_existe(conn, codigo: str, excluir_id: int = None):
    cursor = conn.cursor()
    if excluir_id:
        cursor.execute(
            "SELECT COUNT(*) FROM patrimonio WHERE codigo = %s AND id != %s",
            (codigo, excluir_id)
        )
    else:
        cursor.execute(
            "SELECT COUNT(*) FROM patrimonio WHERE codigo = %s", (codigo,)
        )
    existe = cursor.fetchone()[0] > 0
    cursor.close()
    return existe


# ── Escrita ──────────────────────────────────────────────────

def cadastrar_patrimonio(conn, dados: dict):
    """
    dados: codigo, codigo_secundario, tipo_patrimonio, descricao,
           marca, modelo, status, local_id, responsavel,
           data_aquisicao, valor, numero_serie, observacoes
    Retorna (True, msg) ou (False, msg).
    """
    if patrimonio_existe(conn, dados["codigo"]):
        return False, "Já existe um patrimônio com esse código."

    if dados.get("status") and dados["status"] not in STATUS_VALIDOS:
        return False, f"Status inválido. Use: {', '.join(STATUS_VALIDOS)}"

    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO patrimonio (
            codigo, codigo_secundario, tipo_patrimonio, descricao,
            marca, modelo, status, local_id, responsavel,
            data_aquisicao, valor, numero_serie, observacoes
        ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """, (
        dados.get("codigo"),
        dados.get("codigo_secundario"),
        dados.get("tipo_patrimonio"),
        dados.get("descricao"),
        dados.get("marca"),
        dados.get("modelo"),
        dados.get("status", "Disponível"),
        dados.get("local_id"),
        dados.get("responsavel"),
        dados.get("data_aquisicao") or None,
        dados.get("valor") or None,
        dados.get("numero_serie"),
        dados.get("observacoes"),
    ))
    novo_id = cursor.lastrowid
    conn.commit()
    cursor.close()

    auditoria.registrar(conn, "CADASTRAR", f"Patrimônio {dados['codigo']} cadastrado.",
                        "patrimonio", novo_id)
    return True, "Patrimônio cadastrado com sucesso!"


def editar_patrimonio(conn, codigo: str, dados: dict):
    pat = buscar_por_codigo(conn, codigo)
    if not pat:
        return False, "Patrimônio não encontrado."

    if "status" in dados and dados["status"] not in STATUS_VALIDOS:
        return False, f"Status inválido. Use: {', '.join(STATUS_VALIDOS)}"

    cursor = conn.cursor()
    cursor.execute("""
        UPDATE patrimonio SET
            descricao       = %s, marca          = %s,
            modelo          = %s, tipo_patrimonio = %s,
            status          = %s, responsavel     = %s,
            data_aquisicao  = %s, valor           = %s,
            numero_serie    = %s, observacoes     = %s
        WHERE codigo = %s
    """, (
        dados.get("descricao"),      dados.get("marca"),
        dados.get("modelo"),         dados.get("tipo_patrimonio"),
        dados.get("status"),         dados.get("responsavel"),
        dados.get("data_aquisicao") or None,
        dados.get("valor") or None,
        dados.get("numero_serie"),   dados.get("observacoes"),
        codigo,
    ))
    conn.commit()
    cursor.close()

    auditoria.registrar(conn, "EDITAR", f"Patrimônio {codigo} editado.",
                        "patrimonio", pat["id"])
    return True, "Patrimônio atualizado com sucesso!"


def alterar_status(conn, codigo: str, novo_status: str):
    if novo_status not in STATUS_VALIDOS:
        return False, f"Status inválido. Use: {', '.join(STATUS_VALIDOS)}"

    pat = buscar_por_codigo(conn, codigo)
    if not pat:
        return False, "Patrimônio não encontrado."

    cursor = conn.cursor()
    cursor.execute(
        "UPDATE patrimonio SET status = %s WHERE codigo = %s",
        (novo_status, codigo)
    )
    conn.commit()
    cursor.close()

    auditoria.registrar(conn, "ALTERAR_STATUS",
                        f"{codigo}: {pat['status']} → {novo_status}",
                        "patrimonio", pat["id"])
    return True, f"Status alterado para '{novo_status}'."


# ── Fotos ────────────────────────────────────────────────────

def salvar_foto(conn, patrimonio_id: int, caminho_original: str, principal: bool = False):
    """
    Copia a foto para assets/fotos/ e registra no banco.
    Retorna (True, msg) ou (False, msg).
    """
    if not os.path.exists(caminho_original):
        return False, "Arquivo não encontrado."

    ext      = os.path.splitext(caminho_original)[1].lower()
    nome     = f"{patrimonio_id}_{len(listar_fotos(conn, patrimonio_id))+1}{ext}"
    destino  = os.path.join(PASTA_FOTOS, nome)

    shutil.copy2(caminho_original, destino)

    if principal:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE patrimonio_fotos SET principal = FALSE WHERE patrimonio_id = %s",
            (patrimonio_id,)
        )
        conn.commit()
        cursor.close()

    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO patrimonio_fotos (patrimonio_id, caminho, principal) VALUES (%s,%s,%s)",
        (patrimonio_id, nome, principal)
    )
    conn.commit()
    cursor.close()

    auditoria.registrar(conn, "FOTO", f"Foto adicionada ao patrimônio id {patrimonio_id}.",
                        "patrimonio_fotos", patrimonio_id)
    return True, "Foto salva com sucesso!"


def listar_fotos(conn, patrimonio_id: int):
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT id, caminho, principal FROM patrimonio_fotos WHERE patrimonio_id = %s",
        (patrimonio_id,)
    )
    fotos = cursor.fetchall()
    cursor.close()
    for f in fotos:
        f["caminho_completo"] = os.path.join(PASTA_FOTOS, f["caminho"])
    return fotos
