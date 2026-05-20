from typing import Tuple
import uuid
from pydantic import BaseModel, ConfigDict, Field
from ..errors.entity_errors import ParamNotValidated
from ..enums.item_type_enum import ItemTypeEnum


class Item:
    
    # atributos da entidade
    
    item_id: str
    name: str
    price: float
    item_type: ItemTypeEnum
    admin_permission: bool
    
    def __init__(
        
        # argumentos da função 
        
        self, 
        item_id: str = None,
        name: str = None, 
        price: float = None, 
        item_type: ItemTypeEnum = None,
        admin_permission: bool = False # o default colocamos dessa forma
    ):
        
        # método construtor da entidade. Pense nisso como uma função que executa toda vez que voce instancia a classe.
        # Ex: meu_item = Item( *argumentos que voce pediu na chamada* ) -> executa a logica dentro de __init__ e pede pelos argumentos
        # passados na função (item_id, name, price, item_type, admin_permission). DETALHE: esses argumentos pedidos NÃO são os atributos da entidade.
        # voce poderia modelar a função init para pedir apenas por name, price, item_type e admin_permission, por exemplo, e gerar um id aleatório dentro
        # do proprio init.
        
        ##
        
        # a seguir temos o fluxo validação dos parâmetros da entidade. o python por natureza não é uma linguagem estritamente tipada.
        # isso significa que mesmo voce definindo nos argumentos da função E nos atributos da entidade, voce poderia livremente atribuir um int ao item_id
        # sem o python te barrar.
        # os métodos de validação servem para restringir nossa entidade às devidas regras de negócio. o validation_item_id, por exemplo, valida se o item_id
        # esta dentro das regras esperadas e determinadas pela nossa aplicação. seguindo no mesmo exemplo, ele precisa ser uma string, no formato UUID e não nulo.
        # segure ctrl + click esquerdo na função validate_item_id ou vá para a linha 86 - a lógica de validação do item_id está la.
        
        validation_item_id = self.validate_item_id(item_id)
        if validation_item_id[0] is False:
            
            # esse bloco raise levanta um erro (para um escopo acima de execução, por exemplo no arquivo (código) que está chamando a entidade)
            # posteriormente esse erro pode ser capturado (except) no proprio escopo ou em um acima para direcionar o código
            
            raise ParamNotValidated("item_id", validation_item_id[1])
        
        # após passar da validação (e não levantar nenhum erro), atribuimos um atributo da entidade ao valor passado como argumento no init
        # nosso item agora possuí um atributo item_id, que podemos acessar por item.item_id
        # antes dessa atribuição (a baixo) o valor item_id é apenas um argumento recebido pela função init e não "persiste" no nosso item. isso significa que
        # depois que a função init terminar de executar seu cógio, caso não tivessemos a linha 58, a entidade não teria um item_id definido
        
        self.item_id = item_id
        
        validation_name = self.validate_name(name)
        if validation_name[0] is False:
            raise ParamNotValidated("name", validation_name[1])
        self.name = name
        
        validation_price = self.validate_price(price)
        if validation_price[0] is False:
            raise ParamNotValidated("price", validation_price[1])
        self.price = price

        validation_item_type = self.validate_item_type(item_type)
        if validation_item_type[0] is False:
            raise ParamNotValidated("item_type", validation_item_type[1])
        self.item_type = item_type
        
        validation_admin_permission = self.validate_admin_permission(admin_permission)
        if validation_admin_permission[0] is False:
            raise ParamNotValidated("admin_permission", validation_admin_permission[1])
        self.admin_permission = admin_permission
        
    # definição dos métodos de validação
    # os @ antes das funções ou qualquer bloco de código se chamam Decorators.
    # esse em específico, @staticmethod, nos permite chamar esses métodos "de fora" da entidade. Exemplo: não criamos um item ainda, porém podemos rodar um
    # (nome da classe)Item.validate_item_id("123321") - note que a chamada Item não é atribuída a uma entidade, mas sim à classe Item.
        
    @staticmethod
    def validate_item_id(item_id: str) -> Tuple[bool, str]:
        if item_id is None:
            return (False, "Item id is required")
        if type(item_id) != str:
            return (False, "Item id must be a string")
        if not uuid.UUID(item_id):
            return (False, "Item id must be a valid uuid string")
        return (True, "")
    
    @staticmethod
    def validate_name(name: str) -> Tuple[bool, str]:
        if name is None:
            return (False, "Name is required")
        if type(name) != str:
            return (False, "Name must be a string")
        if len(name) < 3:
            return (False, "Name must be at least 3 characters long")
        return (True, "")
        
    @staticmethod
    def validate_price(price: float) -> Tuple[bool, str]:
        if price is None:
            return (False, "Price is required")
        if type(price) != float:
            return (False, "Price must be a float")
        if price < 0:
            return (False, "Price must be a positive number")
        return (True, "")
    
    @staticmethod
    def validate_item_type(item_type: ItemTypeEnum) -> Tuple[bool, str]:
        if item_type is None:
            return (False, "Item type is required")
        if type(item_type) != ItemTypeEnum:
            return (False, "Item type must be a ItemTypeEnum")
        return (True, "")
    
    @staticmethod
    def validate_admin_permission(admin_permission: bool) -> Tuple[bool, str]:
        if admin_permission is None:
            return (False, "Admin permission is required")
        if type(admin_permission) != bool:
            return (False, "Admin permission must be a boolean")
        return (True, "")
    
        
    def to_dict(self):
        return {
            "item_id": self.item_id,
            "name": self.name,
            "price": self.price,
            "item_type": self.item_type.value,
            "admin_permission": self.admin_permission
        }
    
    def __eq__(self,other):
        return (
            self.name == other.name and 
            self.price == other.price and 
            self.item_type == other.item_type and 
            self.admin_permission == other.admin_permission
        )
    
    def __repr__(self):
        return f"""
            Item(name={self.name}, 
            price={self.price}, 
            item_type={self.item_type}, 
            admin_permission={self.admin_permission})
        """
        
# esse é o caminho do desafio, não é necessário para completar o trainee fazer o objeto por meio do pydantic
        
class PydanticItem(BaseModel):
    
    item_id: uuid.UUID = Field(
        description="ID único do item, em formato UUID",
        default_factory=uuid.uuid4
    )
    name: str = Field(
        description="Nome do item, precisa ter no minimo 3 caracteres e no maximo 100",
        pattern=r'^[A-Za-z\s]+$', # apenas espaços e letras
        min_length=3,
        max_length=100,
    )
    price: float = Field(
        description="Preço do Item, precisa ser maior que 0",
        gt=0 # gt significa greater than
    )
    item_type: ItemTypeEnum = Field(
        description="Tipo do Item, determinado por um Enum",
    )
    admin_permission: bool = Field(
        description="Bool indicando permissão de administador",
        default=False
    )
    
    model_config = ConfigDict(
        use_enum_values=False,
        extra="forbid",
        populate_by_name=True
    )