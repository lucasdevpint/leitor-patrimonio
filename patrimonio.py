from banco import conectar

def cadastrar_patrimonio(conn, dados):
    cursor = conn.cursor()
    

    codigo = dados[0]
    codigo_secundario = dados[1]

    from patrimonio import patrimonio_existe

    if patrimonio_existe(conn, codigo, codigo_secundario):
        print("❌ Patrimônio já existe (código ou secundário duplicado)")
        cursor.close()
        return

    sql = """
    INSERT INTO patrimonio (
        codigo,
        codigo_secundario,
        tipo_patrimonio,
        descricao,
        marca,
        modelo,
        status,
        local_id,
        observacoes
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    cursor.execute(sql, dados)
    conn.commit()
    cursor.close()

    print("✔ Patrimônio cadastrado com sucesso!")
    
def listar_patrimonios(conn):
    cursor = conn.cursor(dictionary=True)

    sql = """
    SELECT
        p.codigo,
        p.codigo_secundario,
        p.tipo_patrimonio,
        p.descricao,
        l.nome AS local,
        p.status
    FROM patrimonio p
    LEFT JOIN locais l ON p.local_id = l.id
    ORDER BY p.codigo
    """

    cursor.execute(sql)
    resultados = cursor.fetchall()

    print("\n=== PATRIMÔNIOS CADASTRADOS ===\n")

    for item in resultados:
        print(
            f"{item['codigo']} | "
            f"{item['tipo_patrimonio']} | "
            f"{item['descricao']} | "
            f"{item['local']} | "
            f"{item['status']}"
        )

    cursor.close()

def patrimonio_existe(conn, codigo, codigo_secundario=None):
    cursor = conn.cursor()

    if codigo_secundario:
        sql = """
        SELECT COUNT(*)
        FROM patrimonio
        WHERE codigo = %s OR codigo_secundario = %s
        """
        cursor.execute(sql, (codigo, codigo_secundario))
    else:
        sql = """
        SELECT COUNT(*)
        FROM patrimonio
        WHERE codigo = %s
        """
        cursor.execute(sql, (codigo,))

    existe = cursor.fetchone()[0]

    cursor.close()

    return existe > 0

def salvar():
    dados = tuple(entry.get() for entry in entradas.values())

    if patrimonio_existe(conn, dados[0], dados[1]):
        print("❌ Já existe patrimônio com esse código")
        return

    cadastrar_patrimonio(conn, dados)

    print("✔ Cadastrado com sucesso!")
    janela.destroy()

def buscar_por_codigo(conn, codigo):
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            p.codigo,
            p.codigo_secundario,
            p.descricao,
            p.marca,
            p.modelo,
            p.status,
            l.nome AS local
        FROM patrimonio p
        LEFT JOIN locais l ON p.local_id = l.id
        WHERE p.codigo = %s
    """, (codigo,))

    resultado = cursor.fetchone()
    cursor.close()

    return resultado

def alterar_status():
    codigo = input("\nCódigo do patrimônio: ")

    conn = conectar()
    cursor = conn.cursor(dictionary=True)

    sql = """
    SELECT codigo, descricao, status
    FROM patrimonio
    WHERE codigo = %s
    """

    cursor.execute(sql, (codigo,))
    patrimonio = cursor.fetchone()

    if not patrimonio:
        print("\nPatrimônio não encontrado.")
        cursor.close()
        conn.close()
        return

    print("\nPatrimônio encontrado:")
    print("Descrição:", patrimonio["descricao"])
    print("Status atual:", patrimonio["status"])

    print("\nNovo status:")
    print("1 - Em uso")
    print("2 - Disponível")
    print("3 - Em manutenção")
    print("4 - Defeito")
    print("5 - Descarte")

    opcao = input("\nEscolha: ")

    status_map = {
        "1": "Em uso",
        "2": "Disponível",
        "3": "Em manutenção",
        "4": "Defeito",
        "5": "Descarte"
    }

    novo_status = status_map.get(opcao)

    if not novo_status:
        print("\nOpção inválida.")
        cursor.close()
        conn.close()
        return

    sql_update = """
    UPDATE patrimonio
    SET status = %s
    WHERE codigo = %s
    """

    cursor.execute(sql_update, (novo_status, codigo))
    conn.commit()

    print("\nStatus atualizado com sucesso!")

    cursor.close()
    conn.close()