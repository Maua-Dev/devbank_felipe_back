from abc import ABC, abstractmethod
from typing import List, Optional

from ..enums.item_type_enum import ItemTypeEnum

from ..entities.item import Item


class IItemRepository(ABC):
    
    # a interface de repositório é como se fosse um esqueleto. diferentes corpos existem para o mesmo design de esqueleto, a mesma coisa é verdade para as interfaces.
    # diferentes repositórios podem ser construídos seguindo a mesma interface.
    # quando instanciamos o repositórios, passamos a interface e consequentemente somos obrigados a instanciar os métodos que recebem os Decorators abstractmethod
    # isso garante, por exemplo, que nosso reposirório de testes tenha obrigatóriamente os mesmo metódos do repositório real.

    @abstractmethod
    def get_all_items(self) -> List[Item]:
        
        # a baixo segue uma docstring, elas são importantes para documentar a função nesse caso, ou outros elementos dentro do python.
        # aqui passamos uma descrição do retorno da função + o tipo de retorno. no método seeguinte, especificamos os argumentos que 
        # devemos passar ao método. isso é literalmente o que aparece quando voce arrasta o mouse para cima de uma função de biblioteca
        # ao longo do código, ela se refere a docstring e ajuda muito a vida de quem posteriormente desenvolve ou que esta desenvolvendo com voce
        
        """
        Return all stored items.

        Returns:
            List[Item]: Collection of all items currently persisted.
        """
        pass

    @abstractmethod
    def get_item(self, item_id: str) -> Optional[Item]:
        """
        Retrieve a single item by its identifier.

        Args:
            item_id (str): UUID string stored in the entity attribute `item.item_id`.

        Returns:
            Optional[Item]: The matching item when found, otherwise `None`.
        """
        pass

    @abstractmethod
    def create_item(self, item: Item) -> Item:
        """
        Persist a new item.

        Args:
            item (Item): Fully validated item entity.

        Returns:
            Item: The persisted item.
        """
        pass

    @abstractmethod
    def delete_item(self, item_id: str) -> Optional[Item]:
        """
        Delete an item by its identifier.

        Args:
            item_id (str): UUID string of the target item.

        Returns:
            Optional[Item]: Deleted item when found, otherwise `None`.
        """
        pass

    @abstractmethod
    def update_item(
        self,
        item_id: str,
        name: str = None,
        price: float = None,
        item_type: ItemTypeEnum = None,
        admin_permission: bool = None,
    ) -> Optional[Item]:
        """
        Update mutable fields of an existing item.

        Args:
            item_id (str): UUID string of the item to update.
            name (str, optional): New name.
            price (float, optional): New price.
            item_type (ItemTypeEnum, optional): New item type.
            admin_permission (bool, optional): New admin permission flag.

        Returns:
            Optional[Item]: Updated item when found, otherwise `None`.
        """
        pass