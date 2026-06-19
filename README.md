# Sistema Patrimonial v3

## Instalação

```bash
pip install customtkinter mysql-connector-python openpyxl pillow
```

## Configurar banco

1. Abra `db/config.py` e preencha suas credenciais MySQL.
2. Execute o script de atualização no seu banco **existente** (não apaga dados):

```bash
mysql -u root -p patrimonio < db/schema_atualizacao.sql
```

## Executar

```bash
python gui/main.py
```

## Primeiro acesso

Login: `admin`  
Senha: `admin123`

⚠️ **Troque a senha no primeiro acesso** — acesse o banco e rode:
```sql
UPDATE usuarios SET senha_hash = SHA2('nova_senha', 256) WHERE login = 'admin';
```

## O que há de novo na v3

| Recurso                | Descrição |
|------------------------|-----------|
| **Login com níveis**   | admin / editor / visualizador |
| **Log de auditoria**   | Toda ação fica registrada com usuário e horário |
| **Foto no cadastro**   | Vincula imagem ao patrimônio |
| **Manutenção**         | Agende, acompanhe e conclua manutenções |
| **Alertas automáticos**| Aviso ao abrir se há manutenções nos próximos 7 dias |
| **Relatório Excel**    | 4 abas: patrimônios, status, manutenções, auditoria |
| **Busca ampliada**     | Busca por Nº série e responsável também |
| **Dashboard ampliado** | Valor total do acervo + contadores de manutenção |

## Níveis de acesso

| Nível          | Pode visualizar | Pode editar/cadastrar | Vê auditoria |
|----------------|:-:|:-:|:-:|
| visualizador   | ✅ | ❌ | ❌ |
| editor         | ✅ | ✅ | ❌ |
| admin          | ✅ | ✅ | ✅ |

## Atualização v3.1 — Usuários e Visitantes

Esta versão adiciona gerenciamento completo de usuários (admin) e
cadastro de visitantes, seguindo o fluxo seguro de migração:

### Fluxo de atualização (siga esta ordem)

```bash
# 1. Backup do banco ANTES de qualquer alteração
mysqldump -u root -p patrimonio > backup_antes_v31.sql

# 2. Aplicar a migração SQL
mysql -u root -p patrimonio < db/migracao_usuarios_visitantes.sql

# 3. Testar localmente
python gui/main.py
# ou
uvicorn api.app:app --reload

# 4. Se tudo OK, copiar os arquivos atualizados para o servidor
#    (core/, api/, web/, db/)

# 5. No servidor, reiniciar a API
sudo systemctl restart patrimonio-api
```

### Novidades

- **Tela de Usuários** (admin) — cadastrar, editar, redefinir senha, desativar
- **Tela de Visitantes** (admin) — cadastrar, editar, buscar, desativar
- **Alterar Minha Senha** — disponível para qualquer usuário autenticado, no menu "⋯ Mais"
- Regras de segurança: admin não pode remover o próprio nível admin nem desativar a própria conta
- Toda ação fica registrada na auditoria: criação/edição de usuário, troca de senha, criação/edição de visitante

### Endpoints novos da API

| Método | Rota | Quem pode |
|---|---|---|
| GET | `/usuarios/` | admin |
| POST | `/usuarios/` | admin |
| PUT | `/usuarios/{id}` | admin |
| PATCH | `/usuarios/{id}/senha` | admin |
| PATCH | `/usuarios/{id}/desativar` | admin |
| PATCH | `/usuarios/{id}/reativar` | admin |
| PATCH | `/usuarios/me/senha` | qualquer autenticado |
| GET/POST/PUT | `/visitantes/...` | admin |
| GET | `/relatorios/excel` | editor+ |

├── core/
│   ├── auth.py          # Login e controle de usuários
│   ├── auditoria.py     # Log de ações
│   ├── patrimonio.py    # CRUD + fotos
│   ├── movimentacao.py  # Movimentação e histórico
│   ├── manutencao.py    # Manutenção programada
│   ├── inventario.py    # Inventário por local
│   ├── dashboard.py     # Estatísticas
│   └── relatorios.py    # Exportação Excel
├── db/
│   ├── banco.py
│   ├── config.py
│   └── schema_atualizacao.sql
├── gui/
│   └── main.py
├── assets/
│   ├── fotos/           # Fotos dos patrimônios (gerado automaticamente)
│   └── relatorios/      # Relatórios Excel gerados (gerado automaticamente)
└── README.md
```
