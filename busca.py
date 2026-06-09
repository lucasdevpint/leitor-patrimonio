def buscar_patrimonio(conn, termo):
    cursor = conn.cursor()

    sql = """
    SELECT 
        codigo,
        descricao,
        marca,
        modelo,
        status,
        tipo_patrimonio
    FROM patrimonio
    WHERE 
        codigo LIKE %s OR
        descricao LIKE %s OR
        marca LIKE %s OR
        modelo LIKE %s OR
        tipo_patrimonio LIKE %s
    """

    valor = f"%{termo}%"

    cursor.execute(sql, (valor, valor, valor, valor, valor))

    resultados = cursor.fetchall()

    print("\n=== RESULTADOS DA BUSCA ===")

    if not resultados:
        print("Nada encontrado.")
        return

    for r in resultados:
        print(f"""
Código: {r[0]}
Descrição: {r[1]}
Marca: {r[2]}
Modelo: {r[3]}
Status: {r[4]}
Tipo: {r[5]}
------------------------
""")