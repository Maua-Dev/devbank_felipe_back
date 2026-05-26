from .base_error import BaseError


class ParamNotValidated(BaseError):
    def __init__(self, param: str, message: str):
        super().__init__(f'Field {param} is wrong: {message}')

class EntityValidationError(BaseError):
    def __init__(self, message: str):
        super().__init__(f"Erro de validacao na entidade: {message}")