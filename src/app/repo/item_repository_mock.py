from typing import List, Optional, Any

# CORREÇÃO: Usando imports relativos (..) em vez de src.app
from ..entities.item import Item
from ..enums.item_type_enum import ItemTypeEnum
from ..entities.user import User
from ..errors.entity_errors import EntityValidationError
from .item_repository_interface import IItemRepository

class ItemRepositoryMock(IItemRepository):
    items: List[Item]
    user: User

    def __init__(self):
        # IDs e Nomes intocáveis exigidos pela pipeline da DevMauá
        self.items = [
            Item(item_id="b11af449-22c7-43db-b0e4-dbfbbe7fdbd7", name="Barbie", price=2.5, item_type=ItemTypeEnum.TOY, admin_permission=False),
            Item(item_id="b21af449-22c7-43db-b0e4-dbfbbe7fdbd7", name="caneta", price=1.0, item_type=ItemTypeEnum.TOY, admin_permission=False),
            Item(item_id="b41af449-22c7-43db-b0e4-dbfbbe7fdbd7", name="Super Mario Bros", price=50.0, item_type=ItemTypeEnum.GAMES, admin_permission=True),
        ]
        
        # Inicializa o usuário do DevBank
        self.user = User(
            name="Vitor Soller",
            agency="0000",
            account="00000-0",
            current_balance=1000.0
        )

    def get_user(self) -> User:
        return self.user

    def deposit(self, amount: float) -> User:
        if amount <= 0:
            raise EntityValidationError("O valor do deposito deve ser maior que zero")
        self.user.current_balance += amount
        return self.user

    def withdraw(self, amount: float) -> User:
        if amount <= 0:
            raise EntityValidationError("O valor do saque deve ser maior que zero")
        if amount > self.user.current_balance:
            raise EntityValidationError("Saldo insuficiente para realizar o saque")
        self.user.current_balance -= amount
        return self.user

    def get_all_items(self) -> List[Item]:
        return self.items

    def get_item(self, item_id: str) -> Optional[Item]:
        for item in self.items:
            if item.item_id == item_id:
                return item
        return None

    def create_item(self, item: Item) -> Item:
        self.items.append(item)
        return item

    def delete_item(self, item_id: str) -> Optional[Item]:
        for index, item in enumerate(self.items):
            if item.item_id == item_id:
                return self.items.pop(index)
        return None

    def update_item(
        self, 
        item_id: str, 
        name: Optional[str] = None, 
        price: Optional[float] = None, 
        item_type: Optional[Any] = None, 
        admin_permission: Optional[bool] = None
    ) -> Optional[Item]:
        for item in self.items:
            if item.item_id == item_id:
                if name is not None:
                    item.name = name
                if price is not None:
                    item.price = price
                if item_type is not None:
                    item.item_type = item_type
                if admin_permission is not None:
                    item.admin_permission = admin_permission
                return item
        return None