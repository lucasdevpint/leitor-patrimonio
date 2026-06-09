from banco import conectar

def iniciar_inventario():

    conn = conectar()
    cursor = conn.cursor(dictionary=True)

    print("\n=== INVENTÁRIO ===")

    cursor.execute("""
        SELECT id, nome
        FROM locais
        ORDER BY nome
    """)

    locais = cursor.fetchall()

    for local in locais:
        print(f"{local['id']} - {local['nome']}")

    local_id = int(input("\nEscolha o local: "))

    cursor.execute("""
        INSERT INTO inventarios(local_id)
        VALUES (%s)
    """, (local_id,))

    conn.commit()

    inventario_id = cursor.lastrowid

    print("\nInventário iniciado.")
    print("Leia os patrimônios.")
    print("Digite FIM para encerrar.\n")

    encontrados = set()

    while True:

        codigo = input("Código: ")

        if codigo.upper() == "FIM":
            break

        cursor.execute("""
            SELECT id
            FROM patrimonio
            WHERE codigo = %s
        """, (codigo,))

        patrimonio = cursor.fetchone()

        if not patrimonio:
            print("Patrimônio não encontrado.")
            continue

        patrimonio_id = patrimonio["id"]

        if patrimonio_id in encontrados:
            print("Já lido.")
            continue

        encontrados.add(patrimonio_id)

        cursor.execute("""
            INSERT INTO inventario_itens
            (
                inventario_id,
                patrimonio_id
            )
            VALUES (%s, %s)
        """, (
            inventario_id,
            patrimonio_id
        ))

        conn.commit()

        print("✓ Registrado")

    print("\nInventário encerrado.")

    cursor.execute("""
        SELECT
            p.codigo,
            p.descricao
        FROM patrimonio p
        WHERE p.local_id = %s
        AND p.id NOT IN (
            SELECT patrimonio_id
            FROM inventario_itens
            WHERE inventario_id = %s
        )
    """, (
        local_id,
        inventario_id
    ))

    faltantes = cursor.fetchall()

    print("\n=== RESULTADO ===")

    if not faltantes:
        print("\nNenhum patrimônio faltando.")
    else:

        print("\nPatrimônios não encontrados:\n")

        for item in faltantes:
            print(
                f"{item['codigo']} - "
                f"{item['descricao']}"
            )

    cursor.close()
    conn.close()