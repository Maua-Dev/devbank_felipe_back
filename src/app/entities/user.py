import re
from pydantic import BaseModel, Field, field_validator

class User(BaseModel):
    name: str = Field(
        description="Nome do usuario do banco", 
        min_length=3, 
        max_length=100
    )
    agency: str = Field(
        description="Agencia com exatamente 4 digitos"
    )
    account: str = Field(
        description="Conta corrente no esquema XXXXX-X"
    )
    current_balance: float = Field(
        description="Saldo atual da conta do usuario",
        default=0.0
    )

    # Validação customizada para garantir que a agência possui apenas 4 dígitos numéricos
    @field_validator('agency')
    @classmethod
    def validate_agency(cls, v: str) -> str:
        if not re.match(r'^\d{4}$', v):
            raise ValueError("A agencia deve conter exatamente 4 digitos numericos")
        return v

    # Validação customizada para o padrão estrito XXXXX-X
    @field_validator('account')
    @classmethod
    def validate_account(cls, v: str) -> str:
        if not re.match(r'^\d{5}-\d{1}$', v):
            raise ValueError("A conta deve seguir rigorosamente o padrao XXXXX-X")
        return v

    def to_dict(self):
        """
        Método mapeando os atributos tanto em snake_case quanto em CamelCase
        para garantir compatibilidade exata com o Front-end do Playground.
        """
        return {
            "name": self.name,
            "agency": self.agency,
            "account": self.account,
            "current_balance": self.current_balance,
            # Variações para o Front-end conseguir ler com sucesso:
            "currentBalance": self.current_balance,
            "saldo": self.current_balance
        }