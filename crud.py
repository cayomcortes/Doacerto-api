"""
crud.py
Camada de servico: operacoes de persistencia e regras de negocio.
As excecoes de dominio aqui definidas sao convertidas em respostas HTTP em main.py.
"""
from datetime import date, timedelta
from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

import models
import schemas


# ---------------------------------------------------------------------------
# Excecoes de dominio
# ---------------------------------------------------------------------------
class ItemNaoEncontradoError(Exception):
    """Item inexistente (HTTP 404)."""


class RegraDeNegocioError(Exception):
    """Violacao de regra de negocio (HTTP 409)."""


# ---------------------------------------------------------------------------
# Funcoes auxiliares
# ---------------------------------------------------------------------------
def _existe_duplicidade(
    db: Session,
    nome: str,
    categoria: models.CategoriaEnum,
    data_validade: Optional[date],
    ignorar_id: Optional[int] = None,
) -> bool:
    """
    RN05: verifica duplicidade por nome (case-insensitive), categoria e validade.
    A checagem em codigo e necessaria porque, no SQLite, valores NULL nao
    colidem em restricoes UNIQUE.
    """
    consulta = db.query(models.ItemDoacao).filter(
        func.lower(models.ItemDoacao.nome) == nome.lower(),
        models.ItemDoacao.categoria == categoria,
        models.ItemDoacao.data_validade == data_validade,  # None vira IS NULL
    )
    if ignorar_id is not None:
        consulta = consulta.filter(models.ItemDoacao.id != ignorar_id)
    return db.query(consulta.exists()).scalar()


# ---------------------------------------------------------------------------
# Operacoes CRUD
# ---------------------------------------------------------------------------
def criar_item(db: Session, dados: schemas.ItemCreate) -> models.ItemDoacao:
    if _existe_duplicidade(db, dados.nome, dados.categoria, dados.data_validade):
        raise RegraDeNegocioError(
            "Ja existe um item com o mesmo nome, categoria e validade. "
            "Registre uma entrada no item existente."
        )
    item = models.ItemDoacao(**dados.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def listar_itens(
    db: Session,
    categoria: Optional[models.CategoriaEnum] = None,
    apenas_estoque_baixo: bool = False,
    skip: int = 0,
    limit: int = 100,
) -> list[models.ItemDoacao]:
    consulta = db.query(models.ItemDoacao)
    if categoria is not None:
        consulta = consulta.filter(models.ItemDoacao.categoria == categoria)
    if apenas_estoque_baixo:  # RN08
        consulta = consulta.filter(
            models.ItemDoacao.quantidade <= models.ItemDoacao.estoque_minimo
        )
    return consulta.order_by(models.ItemDoacao.nome).offset(skip).limit(limit).all()


def obter_item(db: Session, item_id: int) -> models.ItemDoacao:
    item = db.get(models.ItemDoacao, item_id)
    if item is None:
        raise ItemNaoEncontradoError(f"Item {item_id} nao encontrado.")
    return item


def atualizar_item(
    db: Session, item_id: int, dados: schemas.ItemUpdate
) -> models.ItemDoacao:
    item = obter_item(db, item_id)
    if _existe_duplicidade(
        db, dados.nome, dados.categoria, dados.data_validade, ignorar_id=item_id
    ):
        raise RegraDeNegocioError(
            "A atualizacao geraria duplicidade de nome, categoria e validade."
        )
    for campo, valor in dados.model_dump().items():
        setattr(item, campo, valor)
    db.commit()
    db.refresh(item)
    return item


def excluir_item(db: Session, item_id: int) -> None:
    item = obter_item(db, item_id)
    if item.quantidade != 0:  # RN09
        raise RegraDeNegocioError(
            "Somente itens com saldo zero podem ser excluidos. "
            "Registre a saida do saldo remanescente antes."
        )
    db.delete(item)
    db.commit()


# ---------------------------------------------------------------------------
# Movimentacoes de estoque
# ---------------------------------------------------------------------------
def registrar_entrada(db: Session, item_id: int, quantidade: int) -> models.ItemDoacao:
    item = obter_item(db, item_id)
    if item.vencido:  # RN07
        raise RegraDeNegocioError("Nao e possivel registrar entrada em item vencido.")
    item.quantidade += quantidade
    db.commit()
    db.refresh(item)
    return item


def registrar_saida(db: Session, item_id: int, quantidade: int) -> models.ItemDoacao:
    item = obter_item(db, item_id)
    if quantidade > item.quantidade:  # RN06
        raise RegraDeNegocioError(
            f"Saldo insuficiente: disponivel {item.quantidade}, solicitado {quantidade}."
        )
    item.quantidade -= quantidade
    db.commit()
    db.refresh(item)
    return item


# ---------------------------------------------------------------------------
# Alertas
# ---------------------------------------------------------------------------
def listar_a_vencer(db: Session, dias: int = 7) -> list[models.ItemDoacao]:
    """RN10: itens com saldo que vencem em ate `dias` dias (inclui ja vencidos)."""
    limite = date.today() + timedelta(days=dias)
    return (
        db.query(models.ItemDoacao)
        .filter(
            models.ItemDoacao.data_validade.is_not(None),
            models.ItemDoacao.data_validade <= limite,
            models.ItemDoacao.quantidade > 0,
        )
        .order_by(models.ItemDoacao.data_validade)
        .all()
    )
