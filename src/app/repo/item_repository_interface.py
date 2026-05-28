from abc import ABC, abstractmethod
from typing import List, Optional, Any
from src.app.entities.item import Item
from src.app.entities.user import User

class IItemRepository(ABC):

    @abstractmethod
    def get_all_items(self) -> List[Item]:
        """Return all stored items."""
        pass

    @abstractmethod
    def get_item(self, item_id: str) -> Optional[Item]:
        """Retrieve a single item by its identifier."""
        pass

    @abstractmethod
    def create_item(self, item: Item) -> Item:
        """Persist a new item."""
        pass

    @abstractmethod
    def delete_item(self, item_id: str) -> Optional[Item]:
        """Delete an item by its identifier."""
        pass

    @abstractmethod
    def update_item(
        self, 
        item_id: str, 
        name: Optional[str] = None, 
        price: Optional[float] = None, 
        item_type: Optional[Any] = None, 
        admin_permission: Optional[bool] = None
    ) -> Optional[Item]:
        """Update mutable fields of an existing item."""
        pass

    @abstractmethod
    def get_user(self) -> User:
        """Busca os dados do usuario do DevBank."""
        pass

    @abstractmethod
    def deposit(self, amount: float) -> User:
        """Realiza a operacao de deposito."""
        pass

    @abstractmethod
    def withdraw(self, amount: float) -> User:
        """Realiza a operacao de saque."""
        pass