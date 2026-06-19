# core/auditoria.py
# Registra ações dos usuários para rastreabilidade completa.

from core.auth import usuario_atual


def registrar(conn, acao: str, descricao: str,
               tabela: str = None, registro_id: int = None):
    """
    Registra uma ação no log de auditoria.

    Exemplos de ação: CADASTRAR, EDITAR, MOVER, ALTERAR_STATUS,
                      LOGIN, LOGOUT, EXCLUIR, EXPORTAR
    """
    usuario = usuario_atual()
    usuario_id    = usuario["id"]    if usuario else None
    usuario_login = usuario["login"] if usuario else "sistema"

    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO auditoria
            (usuario_id, usuario_login, acao, tabela, registro_id, descricao)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (usuario_id, usuario_login, acao, tabela, registro_id, descricao))
    conn.commit()
    cursor.close()


def listar_logs(conn, limite: int = 200, usuario_login: str = None, acao: str = None):
    """
    Retorna os últimos logs de auditoria, com filtros opcionais.
    """
    cursor = conn.cursor(dictionary=True)
    filtros = []
    params  = []

    if usuario_login:
        filtros.append("usuario_login = %s")
        params.append(usuario_login)
    if acao:
        filtros.append("acao = %s")
        params.append(acao)

    where = ("WHERE " + " AND ".join(filtros)) if filtros else ""
    params.append(limite)

    cursor.execute(f"""
        SELECT id, usuario_login, acao, tabela, registro_id, descricao, criado_em
        FROM auditoria
        {where}
        ORDER BY criado_em DESC
        LIMIT %s
    """, params)

    resultado = cursor.fetchall()
    cursor.close()
    return resultado
