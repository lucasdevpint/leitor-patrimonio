# core/manutencao.py
from core import auditoria
from datetime import date

TIPOS   = ["preventiva", "corretiva", "calibracao"]
STATUS  = ["pendente", "realizada", "cancelada"]


def agendar(conn, patrimonio_id: int, dados: dict):
    """
    dados: tipo, descricao, data_prevista, responsavel, custo (opcional)
    """
    if dados.get("tipo") not in TIPOS:
        return False, f"Tipo inválido. Use: {', '.join(TIPOS)}"

    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO manutencoes
            (patrimonio_id, tipo, descricao, data_prevista, responsavel, custo)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (
        patrimonio_id,
        dados["tipo"],
        dados.get("descricao"),
        dados["data_prevista"],
        dados.get("responsavel"),
        dados.get("custo") or None,
    ))
    conn.commit()
    cursor.close()

    auditoria.registrar(conn, "MANUTENCAO_AGENDAR",
                        f"Manutenção {dados['tipo']} agendada para patrimônio id {patrimonio_id}.",
                        "manutencoes", patrimonio_id)
    return True, "Manutenção agendada com sucesso!"


def registrar_realizada(conn, manutencao_id: int, data_realizada: str, custo=None):
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE manutencoes
        SET status = 'realizada', data_realizada = %s, custo = COALESCE(%s, custo)
        WHERE id = %s
    """, (data_realizada, custo, manutencao_id))
    conn.commit()
    cursor.close()

    auditoria.registrar(conn, "MANUTENCAO_REALIZADA",
                        f"Manutenção id {manutencao_id} marcada como realizada.",
                        "manutencoes", manutencao_id)
    return True, "Manutenção registrada como realizada!"


def listar_pendentes(conn):
    """Retorna todas as manutenções pendentes, ordenadas pela data prevista."""
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT
            m.id, m.tipo, m.descricao, m.data_prevista,
            m.responsavel, m.custo,
            p.codigo, p.descricao AS patrimonio,
            l.nome AS local,
            DATEDIFF(m.data_prevista, CURDATE()) AS dias_restantes
        FROM manutencoes m
        JOIN patrimonio p ON m.patrimonio_id = p.id
        LEFT JOIN locais l ON p.local_id = l.id
        WHERE m.status = 'pendente'
        ORDER BY m.data_prevista
    """)
    resultado = cursor.fetchall()
    cursor.close()
    return resultado


def listar_por_patrimonio(conn, patrimonio_id: int):
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT id, tipo, descricao, data_prevista, data_realizada,
               responsavel, custo, status
        FROM manutencoes
        WHERE patrimonio_id = %s
        ORDER BY data_prevista DESC
    """, (patrimonio_id,))
    resultado = cursor.fetchall()
    cursor.close()
    return resultado


def alertas_proximos(conn, dias: int = 7):
    """Retorna manutenções que vencem nos próximos X dias."""
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT
            m.id, m.tipo, m.data_prevista,
            p.codigo, p.descricao AS patrimonio,
            DATEDIFF(m.data_prevista, CURDATE()) AS dias_restantes
        FROM manutencoes m
        JOIN patrimonio p ON m.patrimonio_id = p.id
        WHERE m.status = 'pendente'
          AND m.data_prevista BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL %s DAY)
        ORDER BY m.data_prevista
    """, (dias,))
    resultado = cursor.fetchall()
    cursor.close()
    return resultado
