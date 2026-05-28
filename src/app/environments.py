from enum import Enum
import os
from typing import Any

from .errors.environment_errors import EnvironmentNotFound


class STAGE(Enum):
    DOTENV = "DOTENV"
    DEV = "DEV"
    PROD = "PROD"
    TEST = "TEST"


class Environments:
    """
    Defines the environment variables for the application. You should not instantiate this class directly. Please use Environments.get_envs() method instead.
    """
    stage: STAGE

    def _configure_local(self):
        from dotenv import load_dotenv
        load_dotenv()
        os.environ["STAGE"] = os.environ.get("STAGE") or STAGE.TEST.value

    def load_envs(self):
        if "STAGE" not in os.environ or os.environ["STAGE"] == STAGE.DOTENV.value:
            self._configure_local()

        stage_value = os.environ.get("STAGE") or STAGE.TEST.value
        self.stage = STAGE[stage_value.upper()]

    @staticmethod
    def get_item_repo() -> Any:
        # Mantém a nossa correção para aceitar a AWS, mas volta a retornar a CLASSE pura (padrão Mauá)
        if Environments.get_envs().stage in [STAGE.TEST, STAGE.DEV, STAGE.PROD]:
            from .repo.item_repository_mock import ItemRepositoryMock
            return ItemRepositoryMock
        else:
            raise EnvironmentNotFound("STAGE")
        

    @staticmethod
    def get_envs() -> "Environments":
        """
        Returns the Environments object. This method should be used to get the Environments object instead of instantiating it directly.
        """
        envs = Environments()
        envs.load_envs()
        return envs

    def __repr__(self):
        return str(self.__dict__)