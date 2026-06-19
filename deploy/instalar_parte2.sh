#!/bin/bash
# ============================================================
# Parte 2 — Configura venv, systemd e Nginx
# Rode DEPOIS de copiar o projeto para /opt/patrimonio-v3
# e configurar o banco de dados.
# Uso: sudo bash instalar_parte2.sh
# ============================================================

set -e

PROJ=/opt/patrimonio-v3

echo "════════════════════════════════════════════"
echo " Parte 2 — Ambiente Python, Serviço, Nginx"
echo "════════════════════════════════════════════"

# ── 1. Criar ambiente virtual Python ────────────────────────
echo ">> Criando ambiente virtual..."
cd "$PROJ"
python3 -m venv venv
source venv/bin/activate

echo ">> Instalando dependências Python..."
pip install --upgrade pip
pip install fastapi uvicorn[standard] python-multipart \
    "python-jose[cryptography]" "passlib[bcrypt]" \
    mysql-connector-python openpyxl pillow

deactivate

# ── 2. Ajustar permissões ───────────────────────────────────
echo ">> Ajustando permissões..."
chown -R patrimonio:patrimonio "$PROJ"

# ── 3. Instalar serviço systemd ─────────────────────────────
echo ">> Instalando serviço systemd..."
cp "$PROJ/deploy/patrimonio-api.service" /etc/systemd/system/
echo ""
echo "   ⚠️  IMPORTANTE: edite as senhas no arquivo:"
echo "   sudo nano /etc/systemd/system/patrimonio-api.service"
echo "   (DB_PASSWORD e SECRET_KEY)"
echo ""
read -p "   Pressione ENTER depois de editar e salvar..."

systemctl daemon-reload
systemctl enable patrimonio-api
systemctl restart patrimonio-api

# ── 4. Configurar Nginx ──────────────────────────────────────
echo ">> Configurando Nginx..."
cp "$PROJ/deploy/nginx-patrimonio.conf" /etc/nginx/sites-available/patrimonio
ln -sf /etc/nginx/sites-available/patrimonio /etc/nginx/sites-enabled/patrimonio
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl restart nginx

# ── 5. Firewall ───────────────────────────────────────────
echo ">> Configurando firewall..."
ufw allow OpenSSH
ufw allow 'Nginx Full'
ufw --force enable

# ── 6. Status final ──────────────────────────────────────────
echo ""
echo "════════════════════════════════════════════"
echo " Instalação concluída!"
echo "════════════════════════════════════════════"
IP=$(hostname -I | awk '{print $1}')
echo " Acesse em: http://$IP/app"
echo ""
echo " Verificar status da API:"
echo "   sudo systemctl status patrimonio-api"
echo ""
echo " Ver logs em tempo real:"
echo "   sudo journalctl -u patrimonio-api -f"
echo "════════════════════════════════════════════"
