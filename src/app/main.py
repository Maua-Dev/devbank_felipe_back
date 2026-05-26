# type: ignore

from fastapi import FastAPI, HTTPException
from pydantic import ValidationError
from mangum import Mangum

from .environments import Environments
from .errors.entity_errors import ParamNotValidated, EntityValidationError
from .enums.item_type_enum import ItemTypeEnum
from .entities.item import Item

# === INJEÇÃO DE IMPORTS DO DEVBANK ===
from .repo.user_repository_mock import UserRepositoryMock

app = FastAPI()

repo = Environments.get_item_repo()()

# === INICIALIZAÇÃO DO REPOSITÓRIO DE USUÁRIO ===
user_repo = UserRepositoryMock()

# ==========================================================
# ROTAS DO DEVBANK (BACKEND SOLO FELIPE)
# ==========================================================

@app.get("/")
def get_user_data():
    """
    Rota raiz exigida pela Dev Maua para trazer as informacoes 
    iniciais do usuario do DevBank integrado com o Playground.
    """
    try:
        user = user_repo.get_user()
        # .model_dump() converte o objeto Pydantic em dicionario Python nativo
        return user.model_dump()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/deposit")
def deposit(request: dict):
    """
    Rota de Deposito: Recebe {"amount": valor} e soma ao saldo.
    """
    amount = request.get("amount")
    if amount is None:
        raise HTTPException(status_code=400, detail="O parametro amount eh obrigatorio")
    
    try:
        user_updated = user_repo.deposit(float(amount))
        return user_updated.model_dump()
    except EntityValidationError as err:
        raise HTTPException(status_code=400, detail=err.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/withdraw")
def withdraw(request: dict):
    """
    Rota de Saque: Recebe {"amount": valor} e subtrai do saldo.
    """
    amount = request.get("amount")
    if amount is None:
        raise HTTPException(status_code=400, detail="O parametro amount eh obrigatorio")
    
    try:
        user_updated = user_repo.withdraw(float(amount))
        return user_updated.model_dump()
    except EntityValidationError as err:
        raise HTTPException(status_code=400, detail=err.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==========================================================
# ROTAS PADRÃO DO TEMPLATE (MANTIDAS INTACTAS)
# ==========================================================

@app.get("/items/get_all_items")
def get_all_items():
    items = repo.get_all_items()
    return {
        "items": [item.to_dict() for item in items]
    }

@app.get("/items/{item_id}")
def get_item(item_id: str):
    validation_item_id = Item.validate_item_id(item_id=item_id)
    if not validation_item_id[0]:
        raise HTTPException(status_code=400, detail=validation_item_id[1])
    
    item = repo.get_item(item_id)
    
    if item is None:
        raise HTTPException(status_code=404, detail="Item Not found")
    
    return {
        "item_id": item_id,
        "item": item.to_dict()    
    }

@app.post("/items/create_item", status_code=201)
def create_item(request: dict):
    item_id = request.get("item_id")
    
    validation_item_id = Item.validate_item_id(item_id=item_id)
    if not validation_item_id[0]:
        raise HTTPException(status_code=400, detail=validation_item_id[1])
    
    item = repo.get_item(item_id)
    if item is not None:
        raise HTTPException(status_code=409, detail="Item already exists")
    
    name = request.get("name")
    price = request.get("price")
    item_type = request.get("item_type")
    if item_type is None:
        raise HTTPException(status_code=400, detail="Item type is required")
    if type(item_type) != str:
        raise HTTPException(status_code=400, detail="Item type must be a string")
    if item_type not in [possible_type.value for possible_type in ItemTypeEnum]:
        raise HTTPException(status_code=400, detail=item_type + " is not a valid one")
    
    admin_permission = request.get("admin_permission")
    
    try:
        item = Item(
            item_id=item_id,
            name=name,
            price=price,
            item_type=ItemTypeEnum[item_type], 
            admin_permission=admin_permission,
        )
    except ParamNotValidated as err:
        raise HTTPException(status_code=400, detail=err.message)
    
    item_response = repo.create_item(item)
    return {
        "item_id": item_id,
        "item": item_response.to_dict()    
    }
    
@app.delete("/items/delete_item")
def delete_item(request: dict):
    item_id = request.get("item_id")
    
    validation_item_id = Item.validate_item_id(item_id=item_id)
    if not validation_item_id[0]:
        raise HTTPException(status_code=400, detail=validation_item_id[1])
    
    item = repo.get_item(item_id)
    
    if item is None:
        raise HTTPException(status_code=404, detail="Item Not found")

    item_deleted = repo.delete_item(item_id)
    
    return {
        "item_id": item_id,
        "item": item_deleted.to_dict()    
    }
    
@app.put("/items/update_item")
def update_item(request: dict):
    item_id = request.get("item_id")
    
    validation_item_id = Item.validate_item_id(item_id=item_id)
    if not validation_item_id[0]:
        raise HTTPException(status_code=400, detail=validation_item_id[1])
    
    item = repo.get_item(item_id)
    
    if item is None:
        raise HTTPException(status_code=404, detail="Item Not found")

    name = request.get("name")
    price = request.get("price")
    admin_permission = request.get("admin_permission")

    item_type_value = request.get("item_type")
    if item_type_value != None:
        if type(item_type_value) != str:
            raise HTTPException(status_code=400, detail="Item type must be a string")
        if item_type_value not in [possible_type.value for possible_type in ItemTypeEnum]:
            raise HTTPException(status_code=400, detail="Item type is not a valid one")
        item_type = ItemTypeEnum[item_type_value]
    else:
        item_type = None
        
    item_updated = repo.update_item(item_id, name, price, item_type, admin_permission)
    
    return {
        "item_id": item_id,
        "item": item_updated.to_dict()    
    }

handler = Mangum(app, lifespan="off")