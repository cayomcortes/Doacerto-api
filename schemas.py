"""
schemas.py
Contratos de entrada e saida da API, validados com Pydantic v2.
"""
from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from models import CategoriaEnum


class ItemBase(BaseModel):
    """Campos descritivos comuns a cadastro, atualizacao e resposta."""
    nome: str = Field(..., min_length=1, max_length=120, examples=["Arroz tipo 1"])
    categoria: CategoriaEnum = Field(..., examples=["alimento"])
    descricao: Optional[str] = Field(None, max_length=255)
    unidade: str = Field(..., min_length=1, max_length=20, examples=["kg"])
    estoque_minimo: int = Field(0, ge=0, examples=[10])  # RN02
    data_validade: Optional[date] = Field(None, examples=["2027-12-31"])

    @field_validator("nome", "unidade")
    @classmethod
    def normalizar_texto(cls, valor: str) -> str:
        """RN01: remove espacos excedentes e rejeita texto vazio."""
        valor = " ".join(valor.split())
        if not valor:
            raise ValueError("O campo nao pode ser vazio.")
        return valor

    @model_validator(mode="after")
    def exigir_validade_para_alimento(self):
        """RN03: alimentos exigem data de validade."""
        if self.categoria == CategoriaEnum.ALIMENTO and self.data_validade is None:
            raise ValueError("Itens da categoria 'alimento' exigem data_validade.")
        return self


class ItemCreate(ItemBase):
    """Corpo da requisicao de cadastro."""
    quantidade: int = Field(0, ge=0, examples=[50])  # RN02

    @field_validator("data_validade")
    @classmethod
    def validade_nao_pode_estar_no_passado(cls, valor: Optional[date]) -> Optional[date]:
        """RN04: nao se cadastra item ja vencido."""
        if valor is not None and valor < date.today():
            raise ValueError("A data de validade nao pode ser anterior a data atual.")
        return valor


class ItemUpdate(ItemBase):
    """
    Corpo da requisicao de atualizacao (PUT).
    A quantidade NAO e alterada aqui: deve ser movimentada por entrada/saida,
    garantindo rastreabilidade do estoque.
    """


class Movimentacao(BaseModel):
    """Corpo das requisicoes de entrada e saida de estoque."""
    quantidade: int = Field(..., gt=0, examples=[5])


class ItemResponse(ItemBase):
    """Representacao do item retornada pela API."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    quantidade: int
    data_entrada: date
    estoque_baixo: bool
    vencido: bool
