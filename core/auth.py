# core/auth.py
# Autenticação, controle de sessão e gerenciamento de usuários.

import hashlib
import re
from core import auditoria

NIVEIS = ["admin", "editor", "visualizador"]

# Sessão global (usuário logado no momento)
_sessao = {"usuario": None}


def _hash(senha: str) -> str:
    return hashlib.sha256(senha.encode()).hexdigest()


def _email_valido(email: str) -> bool:
    return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email or ""))


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
    """
    hierarquia = {"admin": 3, "editor": 2, "visualizador": 1}
    usuario = usuario_atual()
    if not usuario:
        return False
    return hierarquia.get(usuario["nivel"], 0) >= hierarquia.get(nivel_minimo, 99)


# ── CRUD de usuários (admin) ──────────────────────────────────

def listar_usuarios(conn):
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT id, nome, login, email, cargo, nivel, ativo, criado_em
        FROM usuarios ORDER BY nome
    """)
    resultado = cursor.fetchall()
    cursor.close()
    return resultado


def buscar_usuario_por_id(conn, usuario_id: int):
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT id, nome, login, email, cargo, nivel, ativo, criado_em
        FROM usuarios WHERE id = %s
    """, (usuario_id,))
    resultado = cursor.fetchone()
    cursor.close()
    return resultado


def cadastrar_usuario(conn, dados: dict, criado_por: dict = None):
    """
    dados: nome, login, email, cargo, senha, confirmar_senha, nivel
    Retorna (True, msg) ou (False, msg).
    """
    nome   = (dados.get("nome") or "").strip()
    login_ = (dados.get("login") or "").strip()
    email  = (dados.get("email") or "").strip()
    cargo  = (dados.get("cargo") or "").strip()
    senha  = dados.get("senha") or ""
    confirmar = dados.get("confirmar_senha") or ""
    nivel  = dados.get("nivel")

    if not nome or not login_:
        return False, "Nome e login são obrigatórios."

    if nivel not in NIVEIS:
        return False, f"Nível inválido. Use: {', '.join(NIVEIS)}"

    if email and not _email_valido(email):
        return False, "E-mail inválido."

    if len(senha) < 8:
        return False, "A senha deve ter no mínimo 8 caracteres."

    if senha != confirmar:
        return False, "As senhas não coincidem."

    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO usuarios (nome, login, email, cargo, senha_hash, nivel, ativo)
            VALUES (%s, %s, %s, %s, %s, %s, TRUE)
        """, (nome, login_, email or None, cargo or None, _hash(senha), nivel))
        novo_id = cursor.lastrowid
        conn.commit()
        cursor.close()
    except Exception as e:
        cursor.close()
        msg = str(e)
        if "login" in msg.lower():
            return False, "Já existe um usuário com esse login."
        if "email" in msg.lower():
            return False, "Já existe um usuário com esse e-mail."
        return False, "Erro ao cadastrar usuário."

    quem = criado_por["login"] if criado_por else (usuario_atual() or {}).get("login")
    auditoria.registrar(conn, "CRIAR_USUARIO",
                        f"Usuário '{login_}' criado por '{quem}'.",
                        "usuarios", novo_id)
    return True, "Usuário cadastrado com sucesso!"


def editar_usuario(conn, usuario_id: int, dados: dict):
    """
    dados pode conter: nome, email, cargo, nivel, ativo
    Aplica as regras de segurança:
      - admin não pode remover o próprio nível admin
      - admin não pode desativar a própria conta
    """
    alvo = buscar_usuario_por_id(conn, usuario_id)
    if not alvo:
        return False, "Usuário não encontrado."

    quem_edita = usuario_atual()
    eh_a_propria_conta = quem_edita and quem_edita["id"] == usuario_id

    nivel = dados.get("nivel", alvo["nivel"])
    ativo = dados.get("ativo", alvo["ativo"])

    if eh_a_propria_conta:
        if alvo["nivel"] == "admin" and nivel != "admin":
            return False, "Você não pode remover seu próprio nível de administrador."
        if not ativo:
            return False, "Você não pode desativar sua própria conta."

    if nivel not in NIVEIS:
        return False, f"Nível inválido. Use: {', '.join(NIVEIS)}"

    email = dados.get("email", alvo["email"])
    if email and not _email_valido(email):
        return False, "E-mail inválido."

    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE usuarios
            SET nome = %s, email = %s, cargo = %s, nivel = %s, ativo = %s
            WHERE id = %s
        """, (
            dados.get("nome", alvo["nome"]),
            email or None,
            dados.get("cargo", alvo["cargo"]),
            nivel,
            ativo,
            usuario_id,
        ))
        conn.commit()
        cursor.close()
    except Exception as e:
        cursor.close()
        if "email" in str(e).lower():
            return False, "Já existe um usuário com esse e-mail."
        return False, "Erro ao atualizar usuário."

    quem = quem_edita["login"] if quem_edita else "sistema"
    auditoria.registrar(conn, "EDITAR_USUARIO",
                        f"Usuário id {usuario_id} editado por '{quem}'.",
                        "usuarios", usuario_id)
    return True, "Usuário atualizado com sucesso!"


def alterar_senha(conn, usuario_id: int, senha_nova: str, confirmar: str = None,
                  alterado_por_admin: bool = False):
    """
    Altera a senha de um usuário.
    Se confirmar for fornecido, valida que as senhas coincidem.
    """
    if len(senha_nova) < 8:
        return False, "A senha deve ter no mínimo 8 caracteres."

    if confirmar is not None and senha_nova != confirmar:
        return False, "As senhas não coincidem."

    cursor = conn.cursor()
    cursor.execute(
        "UPDATE usuarios SET senha_hash = %s WHERE id = %s",
        (_hash(senha_nova), usuario_id)
    )
    conn.commit()
    cursor.close()

    quem = usuario_atual()
    quem_login = quem["login"] if quem else "sistema"
    descricao = (
        f"Senha do usuário id {usuario_id} alterada por admin '{quem_login}'."
        if alterado_por_admin else
        f"Usuário '{quem_login}' alterou a própria senha."
    )
    auditoria.registrar(conn, "ALTERAR_SENHA", descricao, "usuarios", usuario_id)
    return True, "Senha alterada com sucesso!"


def trocar_minha_senha(conn, senha_atual: str, senha_nova: str, confirmar: str):
    """
    Fluxo de 'Alterar minha senha' — exige confirmação da senha atual.
    """
    usuario = usuario_atual()
    if not usuario:
        return False, "Sessão inválida."

    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT senha_hash FROM usuarios WHERE id = %s", (usuario["id"],))
    row = cursor.fetchone()
    cursor.close()

    if not row or row["senha_hash"] != _hash(senha_atual):
        return False, "Senha atual incorreta."

    return alterar_senha(conn, usuario["id"], senha_nova, confirmar,
                         alterado_por_admin=False)


def desativar_usuario(conn, usuario_id: int):
    """Exclusão lógica — nunca remove o registro do banco."""
    alvo = buscar_usuario_por_id(conn, usuario_id)
    if not alvo:
        return False, "Usuário não encontrado."

    quem = usuario_atual()
    if quem and quem["id"] == usuario_id:
        return False, "Você não pode desativar sua própria conta."

    cursor = conn.cursor()
    cursor.execute("UPDATE usuarios SET ativo = FALSE WHERE id = %s", (usuario_id,))
    conn.commit()
    cursor.close()

    quem_login = quem["login"] if quem else "sistema"
    auditoria.registrar(conn, "EDITAR_USUARIO",
                        f"Usuário id {usuario_id} desativado por '{quem_login}'.",
                        "usuarios", usuario_id)
    return True, "Usuário desativado."


def reativar_usuario(conn, usuario_id: int):
    cursor = conn.cursor()
    cursor.execute("UPDATE usuarios SET ativo = TRUE WHERE id = %s", (usuario_id,))
    conn.commit()
    cursor.close()

    quem = usuario_atual()
    quem_login = quem["login"] if quem else "sistema"
    auditoria.registrar(conn, "EDITAR_USUARIO",
                        f"Usuário id {usuario_id} reativado por '{quem_login}'.",
                        "usuarios", usuario_id)
    return True, "Usuário reativado."
