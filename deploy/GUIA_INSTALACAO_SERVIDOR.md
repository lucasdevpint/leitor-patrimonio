# Guia de Instalação no Servidor Linux (UERGS)

Este guia coloca o Sistema Patrimonial rodando 24/7 em um servidor Linux
da própria instituição, acessível por toda a rede interna (cabo e Wi-Fi).

---

## Visão geral da arquitetura final

```
Servidor Linux (sempre ligado)
├── MySQL          → banco de dados
├── API (FastAPI)  → rodando como serviço systemd (porta 8000, interna)
└── Nginx          → recebe na porta 80 e repassa pra API

         │
         │  Rede interna da UERGS (cabo + Wi-Fi)
         │
   ┌─────┴─────┬──────────────┬─────────────┐
   PC sala 1   PC sala 2    Celular       Notebook
```

Todo mundo acessa digitando apenas `http://IP_DO_SERVIDOR/app` — sem
precisar da porta `:8000`.

---

## Pré-requisitos

- Um servidor/computador Linux (Ubuntu ou Debian) dentro da rede da UERGS
- Acesso root ou sudo nesse servidor
- O projeto `patrimonio-v3` (esse mesmo que você já tem)
- Backup do seu banco MySQL atual (se já tiver dados)

---

## Passo 1 — Tirar backup do banco atual

No seu PC atual, exporte os dados que já existem:

```bash
mysqldump -u root -p patrimonio > backup_patrimonio.sql
```

Isso gera um arquivo `backup_patrimonio.sql` com todos os seus dados.

---

## Passo 2 — Copiar arquivos para o servidor

Envie a pasta do projeto e o backup para o servidor Linux. Pode usar `scp`:

```bash
scp -r patrimonio-v3 usuario@IP_DO_SERVIDOR:/tmp/
scp backup_patrimonio.sql usuario@IP_DO_SERVIDOR:/tmp/
```

(Troque `usuario` e `IP_DO_SERVIDOR` pelos dados reais de acesso.)

---

## Passo 3 — Conectar no servidor via SSH

```bash
ssh usuario@IP_DO_SERVIDOR
```

---

## Passo 4 — Rodar a primeira parte da instalação

```bash
sudo mv /tmp/patrimonio-v3 /opt/patrimonio-v3
sudo bash /opt/patrimonio-v3/deploy/instalar.sh
```

Esse script instala Python, MySQL, Nginx e cria as pastas necessárias.

---

## Passo 5 — Configurar o MySQL

```bash
sudo mysql_secure_installation
```
Siga as instruções (definir senha root, remover usuários anônimos, etc).

Depois crie o banco e o usuário:
```bash
sudo mysql -e "CREATE DATABASE patrimonio;"
sudo mysql -e "CREATE USER 'patrimonio_user'@'localhost' IDENTIFIED BY 'SUA_SENHA_FORTE';"
sudo mysql -e "GRANT ALL PRIVILEGES ON patrimonio.* TO 'patrimonio_user'@'localhost';"
sudo mysql -e "FLUSH PRIVILEGES;"
```

---

## Passo 6 — Importar seus dados existentes

```bash
sudo mysql patrimonio < /tmp/backup_patrimonio.sql
```

Depois aplique as tabelas novas da v3:
```bash
sudo mysql patrimonio < /opt/patrimonio-v3/db/schema_atualizacao.sql
```

Se der erro de coluna duplicada (como já aconteceu no seu caso), rode os
comandos um por um — veja o arquivo `db/schema_atualizacao.sql` e adapte
conforme a estrutura real das suas tabelas.

---

## Passo 7 — Rodar a segunda parte da instalação

```bash
sudo bash /opt/patrimonio-v3/deploy/instalar_parte2.sh
```

Esse script vai:
1. Criar o ambiente virtual Python e instalar as dependências
2. Pedir para você editar o arquivo de serviço com a senha do banco
3. Configurar o serviço para iniciar automaticamente
4. Configurar o Nginx
5. Liberar o firewall

Quando ele pausar pedindo para editar o arquivo, rode em outro terminal
(ou pressione `Ctrl+X`, depois `Y`, depois `Enter` se estiver usando nano):

```bash
sudo nano /etc/systemd/system/patrimonio-api.service
```

Altere essas duas linhas com os valores reais:
```
Environment="DB_PASSWORD=SUA_SENHA_FORTE"
Environment="SECRET_KEY=qualquer-texto-longo-e-aleatorio-aqui-123456"
```

Salve (`Ctrl+O`, Enter, `Ctrl+X`) e volte ao terminal da instalação,
pressione Enter para continuar.

---

## Passo 8 — Descobrir o IP do servidor

```bash
hostname -I
```

Anote o primeiro IP que aparecer (ex: `10.34.1.50`).

---

## Passo 9 — Testar

No navegador de qualquer computador ou celular **dentro da rede da UERGS**:

```
http://10.34.1.50/app
```

(Substitua pelo IP real do seu servidor.)

---

## Comandos úteis do dia a dia

```bash
# Ver se a API está rodando
sudo systemctl status patrimonio-api

# Reiniciar a API (depois de uma atualização de código)
sudo systemctl restart patrimonio-api

# Ver os logs em tempo real
sudo journalctl -u patrimonio-api -f

# Ver logs de erro do Nginx
sudo tail -f /var/log/nginx/patrimonio-error.log
```

---

## Atualizando o sistema no futuro

Quando eu te entregar uma nova versão do código:

```bash
# 1. Copie os arquivos atualizados para /opt/patrimonio-v3
scp -r patrimonio-v3-novo/* usuario@IP_DO_SERVIDOR:/opt/patrimonio-v3/

# 2. No servidor, reinicie o serviço
sudo systemctl restart patrimonio-api
```

Não precisa reinstalar nada — só substituir os arquivos e reiniciar.

---

## Sobre IP fixo

Se o servidor pegar IP por DHCP, ele pode mudar depois de reiniciar.
Vale pedir para o setor de TI da UERGS reservar um **IP fixo** para esse
servidor na rede — assim o endereço nunca muda e todo mundo pode salvar
o link nos favoritos do navegador.

---

## Sobre acesso fora da rede da UERGS

Como decidido, o acesso é restrito à rede interna por enquanto. Se no
futuro a universidade quiser liberar acesso externo (ex: para
fiscalização remota), aí sim entra a conversa sobre VPN ou hospedagem em
nuvem — com aval da gestão, já que envolve expor dados institucionais.
