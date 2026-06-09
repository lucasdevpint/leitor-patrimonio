def dashboard_patrimonio(conn):
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM patrimonio")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM patrimonio WHERE status = 'Em uso'")
    em_uso = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM patrimonio WHERE status = 'Disponível'")
    disponivel = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM patrimonio WHERE status = 'Em manutenção'")
    manutencao = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM patrimonio WHERE status = 'Defeito'")
    defeito = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM patrimonio WHERE status = 'Descarte'")
    descarte = cursor.fetchone()[0]

    print("\n=== DASHBOARD PATRIMÔNIO ===")
    print(f"Total: {total}")
    print(f"Em uso: {em_uso}")
    print(f"Disponível: {disponivel}")
    print(f"Em manutenção: {manutencao}")
    print(f"Defeito: {defeito}")
    print(f"Descarte: {descarte}")
    print("============================\n")