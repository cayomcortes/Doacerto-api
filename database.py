"""
database.py
Infraestrutura de acesso a dados: engine, fabrica de sessoes e base declarativa.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# Banco SQLite armazenado no arquivo doacoes.db na raiz do projeto.
SQLALCHEMY_DATABASE_URL = "sqlite:///./doacoes.db"

# check_same_thread=False e necessario no SQLite, pois o FastAPI pode
# atender requisicoes em threads distintas da que criou a conexao.
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Classe base para todos os modelos ORM."""


def get_db():
    """
    Dependencia do FastAPI: fornece uma sessao por requisicao
    e garante seu fechamento ao final do ciclo.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
