from banco import conectar

def consultar_patrimonio():
    codigo = input("\nLeia o patrimônio: ")

    conn = conectar()
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
    JOIN locais l ON p.local_id = l.id
    WHERE p.codigo = %s
    """

    cursor.execute(sql, (codigo,))
    resultado = cursor.fetchone()

    if resultado:
        print("\nPatrimônio encontrado")
        print("---------------------")
        print("Código:", resultado["codigo"])
        print("Código Secundário:", resultado["codigo_secundario"])
        print("Tipo:", resultado["tipo_patrimonio"])
        print("Descrição:", resultado["descricao"])
        print("Local:", resultado["local"])
        print("Status:", resultado["status"])
    else:
        print("\nPatrimônio não encontrado.")
        print("Vamos cadastrá-lo.\n")

        print("Tipo de patrimônio:")
        print("1 - UERGS")
        print("2 - Estado RS")
        print("3 - UERGS + Estado RS")
        print("4 - Doação")
        print("5 - Outro")

        tipo_opcao = input("\nEscolha: ")

        tipo_map = {
            "1": "UERGS",
            "2": "Estado RS",
            "3": "UERGS + Estado RS",
            "4": "Doação",
            "5": "Outro"
        }

        tipo_patrimonio = tipo_map.get(tipo_opcao, "UERGS")

        codigo_secundario = input("\nCódigo secundário (ENTER se não existir): ")
        descricao = input("Descrição do equipamento: ")

        print("\nLocais disponíveis:")
        cursor.execute("SELECT id, nome FROM locais ORDER BY nome")
        locais = cursor.fetchall()

        for local in locais:
            print(f"{local['id']} - {local['nome']}")

        local_id = int(input("\nDigite o ID do local: "))

        print("\nStatus:")
        print("1 - Em uso")
        print("2 - Disponível")
        print("3 - Em manutenção")
        print("4 - Defeito")
        print("5 - Descarte")

        opcao = input("Escolha: ")

        status_map = {
            "1": "Em uso",
            "2": "Disponível",
            "3": "Em manutenção",
            "4": "Defeito",
            "5": "Descarte"
        }

        status = status_map.get(opcao, "Em uso")

        sql_insert = """
        INSERT INTO patrimonio
        (
            codigo,
            codigo_secundario,
            tipo_patrimonio,
            descricao,
            local_id,
            status
        )
        VALUES (%s, %s, %s, %s, %s, %s)
        """

        cursor.execute(
            sql_insert,
            (
                codigo,
                codigo_secundario,
                tipo_patrimonio,
                descricao,
                local_id,
                status
            )
        )

        conn.commit()
        print("\nPatrimônio cadastrado com sucesso!")

    cursor.close()
    conn.close()


def listar_patrimonios():
    conn = conectar()
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
    JOIN locais l ON p.local_id = l.id
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
    conn.close()


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