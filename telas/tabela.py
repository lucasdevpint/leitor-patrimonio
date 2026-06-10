import customtkinter as ctk

from telas.detalhes import abrir_detalhes


def listar(conn, tabela):

    tabela.delete(*tabela.get_children())

    cursor = conn.cursor()

    cursor.execute("""
        SELECT p.codigo, p.descricao, l.nome, p.status
        FROM patrimonio p
        LEFT JOIN locais l ON p.local_id = l.id
    """)

    for row in cursor.fetchall():
        tabela.insert("", "end", values=row)


def carregar_tabela(conn, tabela):

    tabela.delete(*tabela.get_children())

    cursor = conn.cursor()

    cursor.execute("""
        SELECT p.codigo, p.descricao, l.nome, p.status
        FROM patrimonio p
        LEFT JOIN locais l ON p.local_id = l.id
    """)

    for row in cursor.fetchall():
        tabela.insert("", "end", values=row)


def buscar_tabela(conn, tabela, entry_busca):

    termo = entry_busca.get()

    tabela.delete(*tabela.get_children())

    cursor = conn.cursor()

    cursor.execute("""
        SELECT p.codigo, p.descricao, l.nome, p.status
        FROM patrimonio p
        LEFT JOIN locais l ON p.local_id = l.id
        WHERE
            p.codigo LIKE %s OR
            p.descricao LIKE %s OR
            p.marca LIKE %s OR
            p.modelo LIKE %s OR
            p.tipo_patrimonio LIKE %s
    """, (
        f"%{termo}%",
        f"%{termo}%",
        f"%{termo}%",
        f"%{termo}%",
        f"%{termo}%"
    ))

    for row in cursor.fetchall():
        tabela.insert("", "end", values=row)


def ao_clicar_tabela(event, app, conn, tabela):

    item = tabela.selection()

    if not item:
        return

    valores = tabela.item(item, "values")

    codigo = valores[0]

    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT p.*, l.nome AS local
        FROM patrimonio p
        LEFT JOIN locais l ON p.local_id = l.id
        WHERE p.codigo = %s
    """, (codigo,))

    dados = cursor.fetchone()

    abrir_detalhes(app, conn, dados)