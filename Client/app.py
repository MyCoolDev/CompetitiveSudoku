from default import *

from States.WelcomeState import WelcomeState
from States.Home import Home
from States.InGame import InGame
from States.InLobby import InLobby
from States.LogRegisterState import LogRegister
from States.GameSpectator import GameSpectator
from client import ClientSocket


class App:
    def __init__(self):
        """
        The client application gui using pygame.
        """
        pygame.init()
        pygame.mixer.init()

        # socket
        self.client = ClientSocket(self)

        self.screen = pygame.display.set_mode((int(self.client.config["SCREEN_WIDTH"]), int(self.client.config["SCREEN_HEIGHT"])))

        # change the screen name
        pygame.display.set_caption("Competitive Sudoku")

        self.clock = pygame.time.Clock()
        self.events = None
        self.running = False
        self.dt = 0  # delta time

        self.current_state = WelcomeState(self.screen, self.client)

    def start_client(self):
        """
        Start the client gui.
        """
        self.running = True
        while self.running:
            self.events = pygame.event.get()
            self.handle_events(self.events)
            self.update()
            self.render()

        pygame.quit()

    def handle_events(self, events):
        """
        Handle the pygame events
        :param events:
        :return:
        """
        for event in events:
            # quit event for the close button on the top nav.
            if event.type == pygame.QUIT:
                self.running = False

    def update(self):
        """
        Update all the objects
        :return:
        """
        # update using the state
        self.current_state.update(self.dt, self.events)

        if isinstance(self.current_state, WelcomeState) and not self.current_state.intro_status:
            self.current_state = LogRegister(self.screen, self.client)

        if self.client.token is not None:
            if self.client.get_data("go_to_spectator"):
                self.client.set_data("go_to_spectator", False)
                self.current_state = GameSpectator(self.screen, self.client)
            if self.client.get_data("go_to_lobby"):
                self.client.set_data("go_to_lobby", False)
                self.current_state = InLobby(self.screen, self.client)
            elif self.client.get_data("go_to_home"):
                self.client.set_data("go_to_home", False)
                self.current_state = Home(self.screen, self.client)
            elif self.client.get_data("go_to_game"):
                self.client.set_data("go_to_game", False)
                self.current_state = InGame(self.screen, self.client)

    def render(self):
        """
        render everything to the screen.
        :return:
        """
        self.dt = self.clock.tick(60) / 1000
        self.screen.fill((46, 46, 46))
        self.current_state.render()
        pygame.display.flip()


if __name__ == '__main__':
    app = App()
    app.start_client()
