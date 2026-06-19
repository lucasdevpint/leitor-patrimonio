# core/auth.py
# Autenticação, controle de sessão e gerenciamento de usuários.

import hashlib

NIVEIS = ["admin", "editor", "visualizador"]

# Sessão global (usuário logado no momento)
_sessao = {"usuario": None}


def _hash(senha: str) -> str:
    return hashlib.sha256(senha.encode()).hexdigest()


# ── Autenticação ─────────────────────────────────────────────

def login(conn, login: str, senha: str):
    """
    Tenta autenticar o usuário.
    Retorna (True, dict_usuario) ou (False, mensagem_erro).
    """
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM usuarios WHERE login = %s AND ativo = TRUE",
        (login,)
    )
    usuario = cursor.fetchone()
    cursor.close()

    if not usuario:
        return False, "Usuário não encontrado ou inativo."

    if usuario["senha_hash"] != _hash(senha):
        return False, "Senha incorreta."

    _sessao["usuario"] = usuario
    return True, usuario


def logout():
    _sessao["usuario"] = None


def usuario_atual():
    return _sessao.get("usuario")


def requer_nivel(nivel_minimo: str):
    """
    Verifica se o usuário logado tem permissão suficiente.
    Hierarquia: admin > editor > visualizador
    Retorna True se permitido, False caso contrário.
    """
    hierarquia = {"admin": 3, "editor": 2, "visualizador": 1}
    usuario = usuario_atual()
    if not usuario:
        return False
    return hierarquia.get(usuario["nivel"], 0) >= hierarquia.get(nivel_minimo, 99)


# ── CRUD de usuários (só admin) ──────────────────────────────

def listar_usuarios(conn):
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT id, nome, login, nivel, ativo, criado_em FROM usuarios ORDER BY nome"
    )
    resultado = cursor.fetchall()
    cursor.close()
    return resultado


def cadastrar_usuario(conn, dados: dict):
    """
    dados: nome, login, senha, nivel
    Retorna (True, msg) ou (False, msg).
    """
    if dados.get("nivel") not in NIVEIS:
        return False, f"Nível inválido. Use: {', '.join(NIVEIS)}"

    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO usuarios (nome, login, senha_hash, nivel) VALUES (%s, %s, %s, %s)",
            (dados["nome"], dados["login"], _hash(dados["senha"]), dados["nivel"])
        )
        conn.commit()
        cursor.close()
        return True, "Usuário cadastrado com sucesso!"
    except Exception as e:
        cursor.close()
        if "Duplicate" in str(e):
            return False, "Já existe um usuário com esse login."
        return False, str(e)


def alterar_senha(conn, usuario_id: int, senha_nova: str):
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE usuarios SET senha_hash = %s WHERE id = %s",
        (_hash(senha_nova), usuario_id)
    )
    conn.commit()
    cursor.close()
    return True, "Senha alterada com sucesso!"


def desativar_usuario(conn, usuario_id: int):
    cursor = conn.cursor()
    cursor.execute("UPDATE usuarios SET ativo = FALSE WHERE id = %s", (usuario_id,))
    conn.commit()
    cursor.close()
    return True, "Usuário desativado."
