# DoaCerto API de Gestao de Estoque de Doacoes

## Execucao (terminal integrado do VS Code)

Windows (PowerShell):
    python -m venv .venv
    .venv\Scripts\Activate.ps1
    pip install -r requirements.txt
    uvicorn main:app --reload

Linux / macOS:
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    uvicorn main:app --reload

Swagger: http://127.0.0.1:8000/docs
Se o PowerShell bloquear a ativacao: Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
