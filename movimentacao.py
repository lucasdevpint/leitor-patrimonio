from banco import conectar
def movimentar_patrimonio():

    codigo = input("\nCódigo do patrimônio: ")

    conn = conectar()
    cursor = conn.cursor(dictionary=True)

    sql = """
    SELECT
        p.id,
        p.codigo,
        p.descricao,
        p.local_id,
        l.nome AS local
    FROM patrimonio p
    JOIN locais l ON p.local_id = l.id
    WHERE p.codigo = %s
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
    print("Local atual:", patrimonio["local"])

    print("\nLocais disponíveis:")

    cursor.execute("""
        SELECT id, nome
        FROM locais
        ORDER BY nome
    """)

    locais = cursor.fetchall()

    for local in locais:
        print(f"{local['id']} - {local['nome']}")

    novo_local = int(input("\nNovo local (ID): "))

    cursor.execute("""
        UPDATE patrimonio
        SET local_id = %s
        WHERE id = %s
    """, (novo_local, patrimonio["id"]))

    cursor.execute("""
        INSERT INTO movimentacoes
        (
            patrimonio_id,
            local_origem_id,
            local_destino_id
        )
        VALUES (%s, %s, %s)
    """, (
        patrimonio["id"],
        patrimonio["local_id"],
        novo_local
    ))

    conn.commit()

    print("\nMovimentação registrada com sucesso!")

    cursor.close()
    conn.close()
def historico_patrimonio():

    codigo = input("\nCódigo do patrimônio: ")

    conn = conectar()
    cursor = conn.cursor(dictionary=True)

    sql = """
    SELECT
        m.data_movimentacao,
        lo.nome AS origem,
        ld.nome AS destino
    FROM movimentacoes m
    JOIN patrimonio p
        ON m.patrimonio_id = p.id
    LEFT JOIN locais lo
        ON m.local_origem_id = lo.id
    JOIN locais ld
        ON m.local_destino_id = ld.id
    WHERE p.codigo = %s
    ORDER BY m.data_movimentacao
    """

    cursor.execute(sql, (codigo,))
    historico = cursor.fetchall()

    if not historico:
        print("\nNenhuma movimentação encontrada.")
        cursor.close()
        conn.close()
        return

    print("\n=== HISTÓRICO DE MOVIMENTAÇÕES ===\n")

    for mov in historico:

        origem = mov["origem"]

        if origem is None:
            origem = "Cadastro Inicial"

        print(
            f"{mov['data_movimentacao']}"
        )

        print(
            f"{origem} -> {mov['destino']}"
        )

        print("-" * 50)

    cursor.close()
    conn.close()