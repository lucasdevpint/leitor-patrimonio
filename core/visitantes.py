# core/visitantes.py
# Lógica pura de visitantes — sem input(), sem print().

from core import auditoria


def listar_visitantes(conn, somente_ativos: bool = True):
    cursor = conn.cursor(dictionary=True)
    if somente_ativos:
        cursor.execute("""
            SELECT id, nome, documento, empresa, telefone, email,
                   observacoes, ativo, criado_em
            FROM visitantes WHERE ativo = TRUE ORDER BY nome
        """)
    else:
        cursor.execute("""
            SELECT id, nome, documento, empresa, telefone, email,
                   observacoes, ativo, criado_em
            FROM visitantes ORDER BY nome
        """)
    resultado = cursor.fetchall()
    cursor.close()
    return resultado


def buscar_visitantes(conn, termo: str):
    """Busca por nome, documento ou empresa."""
    cursor = conn.cursor(dictionary=True)
    v = f"%{termo}%"
    cursor.execute("""
        SELECT id, nome, documento, empresa, telefone, email, observacoes, ativo, criado_em
        FROM visitantes
        WHERE ativo = TRUE
          AND (nome LIKE %s OR documento LIKE %s OR empresa LIKE %s)
        ORDER BY nome
    """, (v, v, v))
    resultado = cursor.fetchall()
    cursor.close()
    return resultado


def buscar_por_id(conn, visitante_id: int):
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM visitantes WHERE id = %s", (visitante_id,))
    resultado = cursor.fetchone()
    cursor.close()
    return resultado


def cadastrar_visitante(conn, dados: dict):
    """
    dados: nome, documento, empresa, telefone, email, observacoes
    """
    nome = (dados.get("nome") or "").strip()
    if not nome:
        return False, "O nome é obrigatório."

    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO visitantes (nome, documento, empresa, telefone, email, observacoes)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (
        nome,
        dados.get("documento") or None,
        dados.get("empresa") or None,
        dados.get("telefone") or None,
        dados.get("email") or None,
        dados.get("observacoes") or None,
    ))
    novo_id = cursor.lastrowid
    conn.commit()
    cursor.close()

    auditoria.registrar(conn, "CRIAR_VISITANTE",
                        f"Visitante '{nome}' cadastrado.",
                        "visitantes", novo_id)
    return True, "Visitante cadastrado com sucesso!"


def editar_visitante(conn, visitante_id: int, dados: dict):
    alvo = buscar_por_id(conn, visitante_id)
    if not alvo:
        return False, "Visitante não encontrado."

    cursor = conn.cursor()
    cursor.execute("""
        UPDATE visitantes
        SET nome = %s, documento = %s, empresa = %s,
            telefone = %s, email = %s, observacoes = %s
        WHERE id = %s
    """, (
        dados.get("nome", alvo["nome"]),
        dados.get("documento", alvo["documento"]),
        dados.get("empresa", alvo["empresa"]),
        dados.get("telefone", alvo["telefone"]),
        dados.get("email", alvo["email"]),
        dados.get("observacoes", alvo["observacoes"]),
        visitante_id,
    ))
    conn.commit()
    cursor.close()

    auditoria.registrar(conn, "EDITAR_VISITANTE",
                        f"Visitante id {visitante_id} editado.",
                        "visitantes", visitante_id)
    return True, "Visitante atualizado com sucesso!"


def desativar_visitante(conn, visitante_id: int):
    """Exclusão lógica."""
    cursor = conn.cursor()
    cursor.execute("UPDATE visitantes SET ativo = FALSE WHERE id = %s", (visitante_id,))
    conn.commit()
    cursor.close()

    auditoria.registrar(conn, "EDITAR_VISITANTE",
                        f"Visitante id {visitante_id} desativado.",
                        "visitantes", visitante_id)
    return True, "Visitante desativado."


def reativar_visitante(conn, visitante_id: int):
    cursor = conn.cursor()
    cursor.execute("UPDATE visitantes SET ativo = TRUE WHERE id = %s", (visitante_id,))
    conn.commit()
    cursor.close()

    auditoria.registrar(conn, "EDITAR_VISITANTE",
                        f"Visitante id {visitante_id} reativado.",
                        "visitantes", visitante_id)
    return True, "Visitante reativado."
