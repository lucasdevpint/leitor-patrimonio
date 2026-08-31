# core/inventario.py

def listar_por_local(conn, local_id: int = None):
    cursor = conn.cursor(dictionary=True)
    if local_id:
        cursor.execute("""
            SELECT l.nome AS local, p.codigo, p.descricao,
                   p.status, p.tipo_patrimonio, p.responsavel
            FROM patrimonio p
            JOIN locais l ON p.local_id = l.id
            WHERE p.local_id = %s ORDER BY l.nome, p.codigo
        """, (local_id,))
    else:
        cursor.execute("""
            SELECT l.nome AS local, p.codigo, p.descricao,
                   p.status, p.tipo_patrimonio, p.responsavel
            FROM patrimonio p
            JOIN locais l ON p.local_id = l.id
            ORDER BY l.nome, p.codigo
        """)
    resultado = cursor.fetchall()
    cursor.close()
    return resultado


def resumo_por_local(conn):
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT l.nome AS local, COUNT(p.id) AS total
        FROM locais l
        LEFT JOIN patrimonio p ON p.local_id = l.id
        GROUP BY l.nome ORDER BY l.nome
    """)
    resultado = cursor.fetchall()
    cursor.close()
    return resultado
