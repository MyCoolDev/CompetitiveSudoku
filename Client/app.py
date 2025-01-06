import pygame

from States.LogRegisterState import LogRegister
from States.Home import Home

from client import ClientSocket


class App:
    def __init__(self):
        """
        The client application gui using pygame.
        """
        pygame.init()

        self.screen = pygame.display.set_mode((1200, 800))
        self.clock = pygame.time.Clock()
        self.events = None
        self.running = False
        self.dt = 0  # delta time

        # sockets
        self.client = ClientSocket()

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
        for event in events:
            # quit event for the close button on the top nav.
            if event.type == pygame.QUIT:
                self.running = False

    def update(self):
        self.current_state.update(self.dt, self.events)

        if self.client.token is not None:
            self.current_state = Home(self.screen, self.client)

    def render(self):
        self.screen.fill((30, 30, 30))
        self.current_state.render()
        pygame.display.flip()
        self.dt = self.clock.tick(60) / 1000


if __name__ == '__main__':
    app = App()
    app.start_client()
