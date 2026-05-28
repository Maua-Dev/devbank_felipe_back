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
    stage: STAGE

    def _configure_local(self):
        from dotenv import load_dotenv
        load_dotenv()
        os.environ["STAGE"] = os.environ.get("STAGE") or STAGE.TEST.value

    def load_envs(self):
        if "STAGE" not in os.environ or os.environ["STAGE"] == STAGE.DOTENV.value:
            self._configure_local()

        stage_value = os.environ.get("STAGE") or STAGE.TEST.value
        # CORREÇÃO DE OURO: Força o "dev" da AWS a virar "DEV" maiúsculo para não quebrar o Enum!
        self.stage = STAGE[stage_value.upper()]

    @staticmethod
    def get_item_repo() -> IItemRepository:
        if Environments.get_envs().stage in [STAGE.TEST, STAGE.DEV, STAGE.PROD]:
            from .repo.item_repository_mock import ItemRepositoryMock
            return ItemRepositoryMock()
        else:
            raise EnvironmentNotFound("STAGE")

    @staticmethod
    def get_envs() -> "Environments":
        envs = Environments()
        envs.load_envs()
        return envs

    def __repr__(self):
        return str(self.__dict__)