# 🩸 Sistema de Doação de Sangue (Fullstack)

Projeto desenvolvido para a disciplina *Projeto de Extensão em Software Fullstack*.

## 1. O problema

Hemocentros e bancos de sangue enfrentam dois problemas recorrentes fora do
ambiente acadêmico:

1. **Falta de agendamento organizado** — doadores aparecem sem hora marcada,
   gerando filas e desperdício de tempo tanto do doador quanto da equipe.
2. **Falta de visibilidade do estoque** — a equipe não tem, em tempo real,
   uma visão clara de quais tipos sanguíneos estão em falta, o que dificulta
   campanhas direcionadas (ex.: "precisamos de O- urgente").

Este sistema resolve os dois problemas ao mesmo tempo: permite que doadores
se cadastrem e agendem doações online, e dá à equipe do hemocentro um painel
para gerenciar agendamentos e o estoque de sangue por tipo sanguíneo,
inclusive com alerta automático de estoque baixo.

## 2. Arquitetura (Front + Back + Banco de Dados)

```
blood-donation-system/
├── backend/              # API em Python (FastAPI)
│   ├── main.py           # Rotas da API
│   ├── models.py         # Modelos do banco (SQLAlchemy)
│   ├── schemas.py        # Validação de dados (Pydantic)
│   ├── auth.py           # Autenticação com JWT + hash de senha
│   └── requirements.txt
├── frontend/             # Interface web (HTML + CSS + JS puro)
│   ├── index.html        # Login / Cadastro
│   ├── dashboard.html    # Painel do doador
│   ├── admin.html        # Painel administrativo do hemocentro
│   ├── css/style.css
│   └── js/
├── .vscode/              # Extensões e configurações recomendadas
└── README.md
```

- **Front-end**: HTML, CSS e JavaScript puro, consumindo a API via `fetch`.
- **Back-end**: Python com FastAPI, autenticação JWT e senhas com hash
  (bcrypt via passlib).
- **Banco de dados**: SQLite (arquivo `blood_donation.db`, criado
  automaticamente), gerenciado com SQLAlchemy.

## 3. Funcionalidades

**Doador:**
- Cadastro e login (com senha criptografada e token JWT).
- Visualização do próprio perfil e tipo sanguíneo.
- Agendamento de doações (data, horário, local).
- Histórico dos próprios agendamentos.
- Visualização do estoque atual do hemocentro.

**Administrador (equipe do hemocentro):**
- Login com o mesmo sistema de autenticação (papel `admin`).
- Listagem de todos os agendamentos, com filtro por status.
- Marcar agendamento como **concluído** (isso atualiza automaticamente a
  data da última doação do doador **e** soma 1 unidade ao estoque do tipo
  sanguíneo correspondente) ou **cancelado**.
- Gestão do estoque por tipo sanguíneo, com destaque visual para tipos
  abaixo do limite mínimo configurado.

Conta de administrador criada automaticamente na primeira execução:
- **E-mail:** `admin@hemocentro.com`
- **Senha:** `admin123`



## 4. Como rodar o back-end

Pré-requisitos: Python 3.11 ou 3.12(testado no 3.11).

```bash
cd backend
python -m venv .venv

# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate

pip install -r requirements.txt
uvicorn main:app --reload
```

A API sobe em `http://localhost:8000`. A documentação interativa (Swagger)
fica disponível automaticamente em `http://localhost:8000/docs`.

## 5. Como rodar o front-end

O front-end é HTML/CSS/JS puro, sem necessidade de build. Duas formas simples
de rodar:

**Opção A — extensão Live Server (recomendada, veja seção 6):**
Abra a pasta `frontend/` no VS Code, clique com o botão direito em
`index.html` e escolha **"Open with Live Server"**.

**Opção B — servidor embutido do Python:**
```bash
cd frontend
python -m http.server 5500
```
Depois acesse `http://localhost:5500` no navegador.

> Importante: o backend precisa estar rodando (`uvicorn main:app --reload`)
> para o front-end funcionar, pois ele consome a API em
> `http://localhost:8000`.

## 6. Extensões do VS Code

Ao abrir esta pasta no VS Code, ele vai sugerir automaticamente a instalação
das extensões listadas em `.vscode/extensions.json`:

| Extensão | Para que serve |
|---|---|
| Python (ms-python.python) | Suporte à linguagem Python |
| Pylance | Autocompletar e checagem de tipos no back-end |
| Black Formatter | Formatação automática do código Python |
| REST Client | Testar os endpoints da API direto do VS Code |
| SQLite Viewer | Visualizar o conteúdo do arquivo Doacerto-api/ |
| Live Server | Rodar o front-end com recarregamento automático |
| Prettier | Formatação automática de HTML/CSS/JS |
| ESLint | Checagem de qualidade do JavaScript |
| GitLens | Visualizar histórico de commits |
| Code Spell Checker | Evita erros de digitação no código e nos textos |

Para instalar tudo de uma vez: abra a paleta de comandos
(`Ctrl+Shift+P` / `Cmd+Shift+P`), digite **"Extensions: Show Recommended
Extensions"** e clique em instalar todas.
