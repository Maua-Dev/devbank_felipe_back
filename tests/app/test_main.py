from fastapi.exceptions import HTTPException
import pytest
import src.app.main as main_module
from src.app.main import get_all_items, get_item, create_item, delete_item, update_item
from src.app.repo.item_repository_mock import ItemRepositoryMock


class Test_Main:
    EXISTING_ITEM_ID = "b11af449-22c7-43db-b0e4-dbfbbe7fdbd7"
    EXISTING_ADMIN_ITEM_ID = "b41af449-22c7-43db-b0e4-dbfbbe7fdbd7"
    EXISTING_UPDATE_ITEM_ID = "b21af449-22c7-43db-b0e4-dbfbbe7fdbd7"
    NEW_ITEM_ID = "88f0920c-0de0-4e0a-bb46-abdb3705579d"
    NOT_FOUND_ITEM_ID = "00000000-0000-0000-0000-000000000000"
    INVALID_UUID_STRING = "1"

    def setup_method(self):
        # Reset do repositorio global usado em src.app.main a cada teste
        main_module.repo = ItemRepositoryMock()

    def test_get_all_items(self):
        repo = ItemRepositoryMock()
        response = get_all_items()
        assert all(
            [
                item_expect.to_dict() == item
                for item_expect, item in zip(repo.items, response.get("items"))
            ]
        )

    def test_get_item(self):
        repo = ItemRepositoryMock()
        response = get_item(item_id=self.EXISTING_ITEM_ID)
        expected_item = repo.get_item(self.EXISTING_ITEM_ID)
        assert response == {
            "item_id": self.EXISTING_ITEM_ID,
            "item": expected_item.to_dict(),
        }

    def test_get_item_id_is_none(self):
        with pytest.raises(HTTPException):
            get_item(item_id=None)

    def test_get_item_id_is_not_string(self):
        with pytest.raises(HTTPException):
            get_item(item_id=1)

    def test_get_item_id_is_not_uuid(self):
        with pytest.raises(ValueError):
            get_item(item_id=self.INVALID_UUID_STRING)

    def test_create_item(self):
        body = {
            "item_id": self.NEW_ITEM_ID,
            "name": "test",
            "price": 1.0,
            "item_type": "TOY",
            "admin_permission": False,
        }
        response = create_item(request=body)
        assert response == {
            "item_id": self.NEW_ITEM_ID,
            "item": {
                "item_id": self.NEW_ITEM_ID,
                "name": "test",
                "price": 1.0,
                "item_type": "TOY",
                "admin_permission": False,
            },
        }

    def test_create_item_conflict(self):
        body = {
            "item_id": self.EXISTING_ITEM_ID,
            "name": "test",
            "price": 1.0,
            "item_type": "TOY",
            "admin_permission": False,
        }
        with pytest.raises(HTTPException) as err:
            create_item(request=body)
        assert err.value.status_code == 409

    def test_create_item_missing_id(self):
        body = {
            "name": "test",
            "price": 1.0,
            "item_type": "TOY",
            "admin_permission": False,
        }
        with pytest.raises(HTTPException) as err:
            create_item(request=body)
        assert err.value.status_code == 400

    def test_create_item_id_is_not_string(self):
        body = {
            "item_id": 0,
            "name": "test",
            "price": 1.0,
            "item_type": "TOY",
            "admin_permission": False,
        }
        with pytest.raises(HTTPException) as err:
            create_item(request=body)
        assert err.value.status_code == 400

    def test_create_item_id_is_not_uuid(self):
        body = {
            "item_id": self.INVALID_UUID_STRING,
            "name": "test",
            "price": 1.0,
            "item_type": "TOY",
            "admin_permission": False,
        }
        with pytest.raises(ValueError):
            create_item(request=body)

    def test_create_item_missing_type(self):
        body = {
            "item_id": self.NEW_ITEM_ID,
            "name": "test",
            "price": 1.0,
            "admin_permission": False,
        }
        with pytest.raises(HTTPException) as err:
            create_item(request=body)
        assert err.value.status_code == 400

    def test_create_item_item_type_is_not_string(self):
        body = {
            "item_id": self.NEW_ITEM_ID,
            "name": "test",
            "price": 1.0,
            "item_type": 1,
            "admin_permission": False,
        }
        with pytest.raises(HTTPException) as err:
            create_item(request=body)
        assert err.value.status_code == 400

    def test_create_item_item_type_is_not_valid(self):
        body = {
            "item_id": self.NEW_ITEM_ID,
            "name": "test",
            "price": 1.0,
            "item_type": "test",
            "admin_permission": False,
        }
        with pytest.raises(HTTPException) as err:
            create_item(request=body)
        assert err.value.status_code == 400

    def test_delete_item(self):
        body = {"item_id": self.EXISTING_ITEM_ID}
        response = delete_item(request=body)
        assert response["item_id"] == self.EXISTING_ITEM_ID
        assert response["item"]["name"] == "Barbie"

    def test_delete_item_missing_id(self):
        with pytest.raises(HTTPException) as err:
            delete_item(request={})
        assert err.value.status_code == 400

    def test_delete_item_id_is_not_string(self):
        with pytest.raises(HTTPException) as err:
            delete_item(request={"item_id": 1})
        assert err.value.status_code == 400

    def test_delete_item_id_is_not_uuid(self):
        with pytest.raises(ValueError):
            delete_item(request={"item_id": self.INVALID_UUID_STRING})

    def test_delete_item_id_not_found(self):
        with pytest.raises(HTTPException) as err:
            delete_item(request={"item_id": self.NOT_FOUND_ITEM_ID})
        assert err.value.status_code == 404

    def test_delete_item_with_admin_flag_on_entity(self):
        body = {"item_id": self.EXISTING_ADMIN_ITEM_ID}
        response = delete_item(request=body)
        assert response["item_id"] == self.EXISTING_ADMIN_ITEM_ID
        assert response["item"]["name"] == "Super Mario Bros"

    def test_update_item(self):
        body = {
            "item_id": self.EXISTING_UPDATE_ITEM_ID,
            "name": "test",
            "price": 1.0,
            "item_type": "TOY",
            "admin_permission": False,
        }
        response = update_item(request=body)
        assert response == {
            "item_id": self.EXISTING_UPDATE_ITEM_ID,
            "item": {
                "item_id": self.EXISTING_UPDATE_ITEM_ID,
                "name": "test",
                "price": 1.0,
                "item_type": "TOY",
                "admin_permission": False,
            },
        }

    def test_update_item_missing_id(self):
        body = {
            "name": "test",
            "price": 1.0,
            "item_type": "TOY",
            "admin_permission": False,
        }
        with pytest.raises(HTTPException) as err:
            update_item(request=body)
        assert err.value.status_code == 400

    def test_update_item_id_is_not_string(self):
        body = {
            "item_id": 1,
            "name": "test",
            "price": 1.0,
            "item_type": "TOY",
            "admin_permission": False,
        }
        with pytest.raises(HTTPException) as err:
            update_item(request=body)
        assert err.value.status_code == 400

    def test_update_item_id_is_not_uuid(self):
        body = {
            "item_id": self.INVALID_UUID_STRING,
            "name": "test",
            "price": 1.0,
            "item_type": "TOY",
            "admin_permission": False,
        }
        with pytest.raises(ValueError):
            update_item(request=body)

    def test_update_item_not_found(self):
        body = {
            "item_id": self.NOT_FOUND_ITEM_ID,
            "name": "test",
            "price": 1.0,
            "item_type": "TOY",
            "admin_permission": False,
        }
        with pytest.raises(HTTPException) as err:
            update_item(request=body)
        assert err.value.status_code == 404

    def test_update_item_with_admin_flag_on_entity(self):
        body = {
            "item_id": self.EXISTING_ADMIN_ITEM_ID,
            "name": "test",
            "price": 1.0,
            "item_type": "TOY",
            "admin_permission": False,
        }
        response = update_item(request=body)
        assert response == {
            "item_id": self.EXISTING_ADMIN_ITEM_ID,
            "item": {
                "item_id": self.EXISTING_ADMIN_ITEM_ID,
                "name": "test",
                "price": 1.0,
                "item_type": "TOY",
                "admin_permission": False,
            },
        }

    def test_update_item_type_not_string(self):
        body = {
            "item_id": self.EXISTING_ITEM_ID,
            "name": "test",
            "price": 1.0,
            "item_type": 1,
            "admin_permission": False,
        }
        with pytest.raises(HTTPException) as err:
            update_item(request=body)
        assert err.value.status_code == 400

    def test_update_item_type_not_valid(self):
        body = {
            "item_id": self.EXISTING_ITEM_ID,
            "name": "test",
            "price": 1.0,
            "item_type": "test",
            "admin_permission": False,
        }
        with pytest.raises(HTTPException) as err:
            update_item(request=body)
        assert err.value.status_code == 400
            