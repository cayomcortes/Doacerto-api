"""
models.py
Modelos ORM (camada de persistencia) mapeados para tabelas do SQLite.
"""
import enum
from datetime import date
from typing import Optional

from sqlalchemy import CheckConstraint, Date, Enum, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class CategoriaEnum(str, enum.Enum):
    """Categorias permitidas para os itens doados."""
    ALIMENTO = "alimento"
    HIGIENE = "higiene"
    VESTUARIO = "vestuario"
    LIMPEZA = "limpeza"
    OUTROS = "outros"


class ItemDoacao(Base):
    __tablename__ = "itens_doacao"

    # Restricoes em nivel de tabela (RN02 e RN05).
    __table_args__ = (
        CheckConstraint("quantidade >= 0", name="ck_quantidade_nao_negativa"),
        CheckConstraint("estoque_minimo >= 0", name="ck_estoque_minimo_nao_negativo"),
        UniqueConstraint("nome", "categoria", "data_validade", name="uq_item_lote"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    categoria: Mapped[CategoriaEnum] = mapped_column(
        Enum(
            CategoriaEnum,
            native_enum=False,
            length=20,
            values_callable=lambda enum_cls: [m.value for m in enum_cls],
        ),
        nullable=False,
    )
    descricao: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    unidade: Mapped[str] = mapped_column(String(20), nullable=False)
    quantidade: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    estoque_minimo: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    data_validade: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    data_entrada: Mapped[date] = mapped_column(Date, nullable=False, default=date.today)

    # Propriedades calculadas (nao persistidas), expostas na API.
    @property
    def estoque_baixo(self) -> bool:
        """RN08: sinaliza saldo igual ou inferior ao minimo definido."""
        return self.quantidade <= self.estoque_minimo

    @property
    def vencido(self) -> bool:
        """Indica se a validade do item ja expirou."""
        return self.data_validade is not None and self.data_validade < date.today()
