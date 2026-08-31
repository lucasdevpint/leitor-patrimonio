# core/dashboard.py

def obter_estatisticas(conn):
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT COUNT(*) AS total FROM patrimonio")
    total = cursor.fetchone()["total"]

    status_list = ["Em uso", "Disponível", "Em manutenção", "Defeito", "Descarte"]
    por_status = {}
    for s in status_list:
        cursor.execute("SELECT COUNT(*) AS qtd FROM patrimonio WHERE status = %s", (s,))
        por_status[s] = cursor.fetchone()["qtd"]

    cursor.execute("""
        SELECT l.nome AS local, COUNT(p.id) AS quantidade
        FROM patrimonio p
        JOIN locais l ON p.local_id = l.id
        GROUP BY l.nome ORDER BY quantidade DESC LIMIT 10
    """)
    por_local = cursor.fetchall()

    # Valor total do patrimônio
    cursor.execute("SELECT COALESCE(SUM(valor), 0) AS total_valor FROM patrimonio")
    total_valor = float(cursor.fetchone()["total_valor"])

    # Manutenções pendentes próximas (7 dias)
    cursor.execute("""
        SELECT COUNT(*) AS qtd FROM manutencoes
        WHERE status = 'pendente'
          AND data_prevista BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 7 DAY)
    """)
    manutencoes_proximas = cursor.fetchone()["qtd"]

    # Manutenções atrasadas
    cursor.execute("""
        SELECT COUNT(*) AS qtd FROM manutencoes
        WHERE status = 'pendente' AND data_prevista < CURDATE()
    """)
    manutencoes_atrasadas = cursor.fetchone()["qtd"]

    cursor.close()
    return {
        "total":                 total,
        "total_valor":           total_valor,
        "por_status":            por_status,
        "por_local":             por_local,
        "manutencoes_proximas":  manutencoes_proximas,
        "manutencoes_atrasadas": manutencoes_atrasadas,
    }
