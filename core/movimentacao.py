# core/movimentacao.py
from core import auditoria


def movimentar_patrimonio(conn, codigo: str, novo_local_id: int):
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT p.id, p.codigo, p.descricao, p.local_id, l.nome AS local
        FROM patrimonio p
        JOIN locais l ON p.local_id = l.id
        WHERE p.codigo = %s
    """, (codigo,))
    pat = cursor.fetchone()

    if not pat:
        cursor.close()
        return False, "Patrimônio não encontrado."

    cursor.execute("SELECT id, nome FROM locais WHERE id = %s", (novo_local_id,))
    local_dest = cursor.fetchone()
    if not local_dest:
        cursor.close()
        return False, "Local de destino não encontrado."

    if pat["local_id"] == novo_local_id:
        cursor.close()
        return False, "O patrimônio já está nesse local."

    cursor.execute(
        "UPDATE patrimonio SET local_id = %s WHERE id = %s",
        (novo_local_id, pat["id"])
    )
    cursor.execute("""
        INSERT INTO movimentacoes (patrimonio_id, local_origem_id, local_destino_id)
        VALUES (%s, %s, %s)
    """, (pat["id"], pat["local_id"], novo_local_id))
    conn.commit()
    cursor.close()

    auditoria.registrar(
        conn, "MOVER",
        f"{codigo}: {pat['local']} → {local_dest['nome']}",
        "movimentacoes", pat["id"]
    )
    return True, "Movimentação registrada com sucesso!"


def historico_patrimonio(conn, codigo: str):
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT
            m.data_movimentacao,
            COALESCE(lo.nome, 'Cadastro Inicial') AS origem,
            ld.nome AS destino
        FROM movimentacoes m
        JOIN patrimonio p ON m.patrimonio_id = p.id
        LEFT JOIN locais lo ON m.local_origem_id = lo.id
        JOIN locais ld ON m.local_destino_id = ld.id
        WHERE p.codigo = %s
        ORDER BY m.data_movimentacao
    """, (codigo,))
    resultado = cursor.fetchall()
    cursor.close()
    return resultado
