from pydantic import ValidationError
import pytest
import uuid
from src.app.entities.item import Item, PydanticItem
from src.app.enums.item_type_enum import ItemTypeEnum
from src.app.errors.entity_errors import ParamNotValidated


class Test_Item:
    
    FIXED_ID = "88f0920c-0de0-4e0a-bb46-abdb3705579d"
    
    def test_item(self):
        item = Item(
            item_id="88f0920c-0de0-4e0a-bb46-abdb3705579d", 
            name="test", 
            price=1.0, 
            item_type=ItemTypeEnum.FOOD, 
            admin_permission=True
        )
        assert item.name == "test"
        assert item.price == 1.0
        assert item.item_type == ItemTypeEnum.FOOD
        assert item.admin_permission == True
        
    def test_item_id_required(self):
        with pytest.raises(ParamNotValidated):
            Item(
                item_id=None, 
                name="test", 
                price=1.0, 
                item_type=ItemTypeEnum.FOOD
            )
            
    def test_item_default_admin_permission(self):
        item = Item(
            item_id="88f0920c-0de0-4e0a-bb46-abdb3705579d", 
            name="test", 
            price=1.0, 
            item_type=ItemTypeEnum.FOOD, 
        )
        assert item.admin_permission == False
            
    def test_item_name_is_not_string(self):
        with pytest.raises(ParamNotValidated):
            Item(
                item_id="88f0920c-0de0-4e0a-bb46-abdb3705579d", 
                name=1.0, 
                price=1.0, 
                item_type=ItemTypeEnum.FOOD, 
                admin_permission=True
            )
            
    def test_item_name_is_too_short(self):
        with pytest.raises(ParamNotValidated):
            Item(
                item_id="88f0920c-0de0-4e0a-bb46-abdb3705579d", 
                name="te", 
                price=1.0, 
                item_type=ItemTypeEnum.FOOD, 
                admin_permission=True
            )
            
    def test_item_price_is_none(self):
        with pytest.raises(ParamNotValidated):
            Item(
                item_id="88f0920c-0de0-4e0a-bb46-abdb3705579d", 
                name="test", 
                price=None, 
                item_type=ItemTypeEnum.FOOD, 
                admin_permission=True
            )
            
    def test_item_price_is_not_float(self):
        with pytest.raises(ParamNotValidated):
            Item(
                item_id="88f0920c-0de0-4e0a-bb46-abdb3705579d", 
                name="test", 
                price="1.0", 
                item_type=ItemTypeEnum.FOOD, 
                admin_permission=True
            )
    def test_item_price_is_negative(self):
        with pytest.raises(ParamNotValidated):
            Item(
                item_id="88f0920c-0de0-4e0a-bb46-abdb3705579d", 
                name="test", 
                price=-1.0, 
                item_type=ItemTypeEnum.FOOD, 
                admin_permission=True
            )
            
    def test_item_type_is_none(self):
        with pytest.raises(ParamNotValidated):
            Item(
                item_id="88f0920c-0de0-4e0a-bb46-abdb3705579d", 
                name="test", 
                price=1.0, 
                item_type=None, 
                admin_permission=True
            )
            
    def test_item_type_is_not_enum(self):
        with pytest.raises(ParamNotValidated):
            Item(
                item_id="88f0920c-0de0-4e0a-bb46-abdb3705579d", 
                name="test", 
                price=1.0, 
                item_type="FOOD", 
                admin_permission=True
            )
            
    def test_item_admin_permission_is_none(self):
        with pytest.raises(ParamNotValidated):
            Item(
                item_id="88f0920c-0de0-4e0a-bb46-abdb3705579d", 
                name="test", 
                price=1.0, 
                item_type=ItemTypeEnum.FOOD, 
                admin_permission=None
            )
        
    def test_item_admin_permission_is_not_bool(self):
        with pytest.raises(ParamNotValidated):
            Item(
                item_id="88f0920c-0de0-4e0a-bb46-abdb3705579d", 
                name="test", 
                price=1.0, 
                item_type=ItemTypeEnum.FOOD, 
                admin_permission="True"
            )
            
class Test_Pydantic_Item:
    
    def test_pydantic_item(self):
        
        # voces podem gerar esse fixed id do site https://www.uuidgenerator.net, de preferencia selecionem uuid4
        
        fixed_id = "c5e36f85-92aa-469c-959f-6f4c8fec6643"
        
        p_item = PydanticItem(
            # como temos o default factory definido para o campo item_id, nao precisamos passar o parametro aqui, ele é gerado
            # automaticamente.
            
            # por estarmos em um ambiente de teste, precisamos definir esse uuid para 'pegar' ele pelo código. do contrário, 
            # é imprático fazer comparações por conta do valor aleatório gerado
            
            # o item_id é responsável por tornar as entidades únicas, pois estamos usando uuid, uma string aleatória seguindo
            # um padrão sempre único (quando gerado).
            
            item_id="c5e36f85-92aa-469c-959f-6f4c8fec6643",
            
            # o campo item não será único pois não definimos uma regra para tal.
            
            name="Item",
            
            # aqui podemos passar um inteiro pois o pydantic converte automaticamente para float. isso se torna necessário
            # quando temos um frontend que não consegue mandar por request números inteiros como quebrados, ex: 100.0
            
            price=100,
            item_type=ItemTypeEnum.TOY,
            
            # admin permission sempre será setado para False caso não passemos o valor aqui
            
            # admin_permission=True
            
        )
        
        # o pydantic vai armazenar o item_id gerado automaticamente em um objeto uuid.UUID. preicsamos converter
        # um deles para o tipo do outro, pode ser os dois em string ou ambos em uuid.UUID.
        
        assert p_item.item_id == uuid.UUID(fixed_id)
        #...
        assert p_item.admin_permission == False
        
    def test_pydantic_item_negative_price(self):
        
        # o pydantic usa um erro padrão para quando um parâmetro é posto fora do padrão definido pelas regras: ValidationError
        
        with pytest.raises(ValidationError) as test_info:
            
            p_item = PydanticItem(     
                name="Item",
                price=-1,
                item_type=ItemTypeEnum.TOY   
            )
            
        # podemos extrair dados do erro por meio do test_info
        # existe uma documentação sobre as strings de erros levantadas, isso é útil para capturar exatamente o erro ou realizar
        # testes em medidas específicas
            
        print(test_info)
        
        # por fora do nest, em with pytest.raises(ValidationError) as test_info, capturamos que isso já é um erro de validação
        # agora, dentro do nest, podemos pegar o erro especificamente por meio da informação disponível dentro de test_info
        # nesse teste, estamos validando a função gt=0 que colocamos nas regras do parâmetro price.
        
        # aqui pegamos a lista de erros da informação disponível em test_info, que nada mais é do que uma entidade do próprio
        # pydantic para explicitar esses erros (igual estamos fazendo com a entidade Item, porém com proposito diferente)
        
        erros = test_info.value.errors()
        
        print(erros)
        
        # garante que só deu UM erro na validação, o erro em price
        assert len(erros) == 1
        
        # garante que o erro foi realmente no campo price
        assert erros[0]['loc'] == ('price',)
        
        # garante que o tipo do erro é exatamente a quebra da regra 'gt'
        assert erros[0]['type'] == 'greater_than'
        
        # essa sequência é crucial para correta indentificação dos erros pessoal