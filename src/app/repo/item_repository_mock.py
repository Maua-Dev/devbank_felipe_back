from typing import List, Optional, Any
from src.app.entities.item import Item
from src.app.enums.item_type_enum import ItemTypeEnum
from src.app.entities.user import User
from src.app.errors.entity_errors import EntityValidationError
from .item_repository_interface import IItemRepository

class ItemRepositoryMock(IItemRepository):
    items: List[Item]
    user: User

    def __init__(self):
        # IDs atualizados para formato UUID válido exigido pela entidade Item da Mauá
        self.items = [
            Item(item_id="93bc17de-276d-49f9-bc8c-2f6385d0d811", name="maça", price=2.5, item_type=ItemTypeEnum.FOOD, admin_permission=False),
            Item(item_id="aa31eb8e-67a0-4107-b286-9a008c2f1fbb", name="caneta", price=1.0, item_type=ItemTypeEnum.TOY, admin_permission=False),
            Item(item_id="e5c6e8f4-63be-4a27-a006-2c9748b991a0", name="livro", price=50.0, item_type=ItemTypeEnum.GAMES, admin_permission=True),
        ]
        
        # Inicializa o usuário do DevBank exigido pelo Playground
        self.user = User(
            name="Vitor Soller",
            agency="0000",
            account="00000-0",
            current_balance=1000.0
        )

    def get_user(self) -> User:
        """Retorna o estado atualizado do usuario."""
        return self.user

    def deposit(self, amount: float) -> User:
        """Soma o valor recebido ao saldo atual."""
        if amount <= 0:
            raise EntityValidationError("O valor do deposito deve ser maior que zero")
        self.user.current_balance += amount
        return self.user

    def withdraw(self, amount: float) -> User:
        """Subtrai o valor do saldo se houver fundos suficientes."""
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