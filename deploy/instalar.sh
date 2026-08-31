#!/bin/bash
# ============================================================
# Script de instalação — Sistema Patrimonial no servidor Linux
# Testado em Ubuntu/Debian. Rode como root ou com sudo.
# Uso: sudo bash instalar.sh
# ============================================================

set -e  # para no primeiro erro

echo "════════════════════════════════════════════"
echo " Instalação do Sistema Patrimonial"
echo "════════════════════════════════════════════"

# ── 1. Atualizar sistema ────────────────────────────────────
echo ">> Atualizando pacotes..."
apt update && apt upgrade -y

# ── 2. Instalar dependências ────────────────────────────────
echo ">> Instalando Python, MySQL e Nginx..."
apt install -y python3 python3-venv python3-pip mysql-server nginx git ufw

# ── 3. Criar usuário de sistema (sem privilégios de login) ──
echo ">> Criando usuário 'patrimonio'..."
if ! id "patrimonio" &>/dev/null; then
    useradd -r -s /bin/false -d /opt/patrimonio-v3 patrimonio
fi

# ── 4. Criar pastas ───────────────────────────────────────
mkdir -p /opt/patrimonio-v3
mkdir -p /var/log/patrimonio
chown -R patrimonio:patrimonio /var/log/patrimonio

echo ""
echo "════════════════════════════════════════════"
echo " Próximos passos manuais:"
echo "════════════════════════════════════════════"
echo "1. Copie a pasta do projeto para /opt/patrimonio-v3"
echo "   (use scp, git clone, ou pendrive)"
echo ""
echo "2. Configure o MySQL:"
echo "   sudo mysql_secure_installation"
echo "   sudo mysql -e \"CREATE DATABASE patrimonio;\""
echo "   sudo mysql -e \"CREATE USER 'patrimonio_user'@'localhost' IDENTIFIED BY 'SUA_SENHA';\""
echo "   sudo mysql -e \"GRANT ALL PRIVILEGES ON patrimonio.* TO 'patrimonio_user'@'localhost';\""
echo "   sudo mysql -e \"FLUSH PRIVILEGES;\""
echo ""
echo "3. Importe seus dados existentes (se tiver backup .sql):"
echo "   sudo mysql patrimonio < seu_backup.sql"
echo ""
echo "4. Rode o restante da instalação:"
echo "   sudo bash /opt/patrimonio-v3/deploy/instalar_parte2.sh"
echo "════════════════════════════════════════════"
