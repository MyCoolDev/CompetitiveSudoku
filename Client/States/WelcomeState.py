from Client.default import *
from BaseState import BaseState
from Client.client import ClientSocket


class WelcomeState(BaseState):
    def __init__(self, screen: Surface, client: ClientSocket):
        """
        A state of the gui, a specific screen (one "page").
        """
        super().__init__(screen, client)

    def __init_vars(self, *args, **kwargs) -> None:
        pass
    