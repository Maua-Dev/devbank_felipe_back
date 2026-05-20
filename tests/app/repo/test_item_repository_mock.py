import pytest
from src.app.entities.item import Item
from src.app.enums.item_type_enum import ItemTypeEnum
from src.app.repo.item_repository_mock import ItemRepositoryMock

class Test_ItemRepositoryMock:
    FIRST_ITEM_ID = "b11af449-22c7-43db-b0e4-dbfbbe7fdbd7"
    NOT_FOUND_ITEM_ID = "00000000-0000-0000-0000-000000000000"
    CREATED_ITEM_ID = "88f0920c-0de0-4e0a-bb46-abdb3705579d"

    def test_get_all_items(self):
        repo = ItemRepositoryMock()
        items = repo.get_all_items()
        assert len(items) == len(repo.items)
        assert all([item_expect == item for item_expect, item in zip(repo.items, items)])
        
    def test_get_item(self):
        repo = ItemRepositoryMock()
        item = repo.get_item(item_id=self.FIRST_ITEM_ID)
        assert item is not None
        assert item.item_id == self.FIRST_ITEM_ID
    
    def test_get_item_not_found(self):
        repo = ItemRepositoryMock()
        item = repo.get_item(item_id=self.NOT_FOUND_ITEM_ID)
        assert item is None
        
    def test_create_item(self):
        repo = ItemRepositoryMock()
        len_before = len(repo.items)
        item = Item(
            item_id=self.CREATED_ITEM_ID,
            name="test",
            price=1.0,
            item_type=ItemTypeEnum.TOY,
            admin_permission=False,
        )
        repo.create_item(item=item)
        len_after = len(repo.items)
        assert len_after == len_before + 1
        assert repo.items[-1] == item
        assert repo.items[-1].item_id == self.CREATED_ITEM_ID
        
    def test_delete_item(self):
        repo = ItemRepositoryMock()
        item_expected_to_be_deleted = repo.get_item(self.FIRST_ITEM_ID)
        len_before = len(repo.items)
        
        item = repo.delete_item(item_id=self.FIRST_ITEM_ID)
        len_after = len(repo.items)
        assert len_after == len_before - 1
        assert item == item_expected_to_be_deleted
        assert repo.get_item(self.FIRST_ITEM_ID) is None
        
    def test_delete_item_not_found(self):
        repo = ItemRepositoryMock()
        item = repo.delete_item(item_id=self.NOT_FOUND_ITEM_ID)
        assert item is None
        
    def test_update_item(self):
        repo = ItemRepositoryMock()
        item_updated = repo.update_item(
            item_id=self.FIRST_ITEM_ID,
            name="test",
            price=1.0,
            item_type=ItemTypeEnum.TOY,
            admin_permission=False,
        )
        
        assert item_updated is not None
        assert item_updated.item_id == self.FIRST_ITEM_ID
        assert item_updated.name == "test"
        assert item_updated.price == 1.0
        assert item_updated.item_type == ItemTypeEnum.TOY
        assert item_updated.admin_permission is False
        
    def test_update_item_partial_1(self):
        repo = ItemRepositoryMock()
        name = "test"
        item_updated = repo.update_item(item_id=self.FIRST_ITEM_ID, name=name)
        
        assert item_updated.name == name
        assert repo.get_item(self.FIRST_ITEM_ID).name == name
        
    def test_update_item_partial_2(self):
        repo = ItemRepositoryMock()
        price = 1.0
        item_updated = repo.update_item(item_id=self.FIRST_ITEM_ID, price=price)
        
        assert item_updated.price == price
        assert repo.get_item(self.FIRST_ITEM_ID).price == price