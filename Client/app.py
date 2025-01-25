import pygame

from States.LogRegisterState import LogRegister
from States.Home import Home
from States.InLobby import InLobby

from client import ClientSocket


class App:
    def __init__(self):
        """
        The client application gui using pygame.
        """
        pygame.init()
        pygame.mixer.init()

        self.screen = pygame.display.set_mode((1920, 1080))
        self.clock = pygame.time.Clock()
        self.events = None
        self.running = False
        self.dt = 0  # delta time

        # socket
        self.client = ClientSocket(self)

        self.current_state = LogRegister(self.screen, self.client)

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

        if self.client.token is not None:
            if self.client.get_data("lobby_info") is None and type(self.current_state) is not Home:
                self.current_state = Home(self.screen, self.client)

            elif self.client.get_data("lobby_info") is not None and type(self.current_state) is not InLobby:
                self.current_state = InLobby(self.screen, self.client)

    def render(self):
        """
        render everything to the screen.
        :return:
        """
        self.screen.fill((46, 46, 46))
        self.current_state.render()
        pygame.display.flip()
        self.dt = self.clock.tick(60) / 1000


if __name__ == '__main__':
    app = App()
    app.start_client()
