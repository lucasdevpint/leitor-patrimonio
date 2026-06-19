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

## Estrutura

```
patrimonio-v3/
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
