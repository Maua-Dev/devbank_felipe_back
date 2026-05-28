from enum import Enum
import os

from .errors.environment_errors import EnvironmentNotFound
from .repo.item_repository_interface import IItemRepository


class STAGE(Enum):
    DOTENV = "DOTENV"
    DEV = "DEV"
    PROD = "PROD"
    TEST = "TEST"


class Environments:
    """
    Defines the environment variables for the application. You should not instantiate this class directly. Please use Environments.get_envs() method instead.

    Usage:

    """
    stage: STAGE

    def _configure_local(self):
        from dotenv import load_dotenv
        load_dotenv()
        os.environ["STAGE"] = os.environ.get("STAGE") or STAGE.TEST.value

    def load_envs(self):
        if "STAGE" not in os.environ or os.environ["STAGE"] == STAGE.DOTENV.value:
            self._configure_local()

        # CORREÇÃO 1: Garante que o valor buscado seja uma string válida para não quebrar o Enum
        stage_value = os.environ.get("STAGE") or STAGE.TEST.value
        self.stage = STAGE[stage_value]

    @staticmethod
    def get_item_repo() -> IItemRepository:
        # Adicionamos o STAGE.DEV e PROD para a AWS não quebrar!
        if Environments.get_envs().stage in [STAGE.TEST, STAGE.DEV, STAGE.PROD]:
            from .repo.item_repository_mock import ItemRepositoryMock
            return ItemRepositoryMock()
        else:
            raise EnvironmentNotFound("STAGE")
        

    @staticmethod
    def get_envs() -> "Environments":
        """
        Returns the Environments object. This method should be used to get the Environments object instead of instantiating it directly.
        :return: Environments (stage={self.stage})

        """
        envs = Environments()
        envs.load_envs()
        return envs

    def __repr__(self):
        return str(self.__dict__)