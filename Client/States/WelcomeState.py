from Client.default import *
from Client.States.BaseState import BaseState
from Client.client import ClientSocket
import math

from Client.Components.Text import Text


class WelcomeState(BaseState):
    def __init__(self, screen: Surface, client: ClientSocket):
        """
        A state of the gui, a specific screen (one "page").
        """
        super().__init__(screen, client)
        self.light_circles = None
        self.__init_vars()
        self.timer = 0

    def __init_vars(self, *args, **kwargs) -> None:

        # animation timer
        self.timer = 0

        # Animations

        # (I) Sin function light flow
        self.radius = 100
        self.light_circles = []
        self.light_circle_radius = 5
        self.animation_durations = 4
        self.animation_circle_duration = 2

        # (II) Studio logo fade animation
        self.intro_production_fade_in_duration = 2
        self.intro_production_duration = 1
        self.intro_production_fade_out_duration = 2
        self.intro_production_fade_sum_duration = self.intro_production_fade_in_duration + self.intro_production_duration + self.intro_production_fade_out_duration
        self.intro_fade_timer = 0
        self.intro_production_content = "RY Studio."
        self.intro_production_text = Text(self.intro_production_content, "Bold", 70,
                                          pygame.Vector2(self.screen.get_width() / 2, self.screen.get_height() / 2),
                                          (255, 255, 255))

        self.intro_status = True

    def update(self, dt: float, events: list, *args, **kwargs):
        """
        Update the state.
        :param dt: delta time
        :param events: events
        :param args: args
        :param kwargs: kwargs
        """
        self.timer += dt

        if self.intro_fade_timer < self.intro_production_fade_sum_duration:
            self.intro_fade_timer += dt

        if self.timer < self.intro_production_fade_in_duration:
            alpha = int((255 / 3) * self.intro_fade_timer)
            self.intro_production_text.alpha = alpha
            self.intro_production_text.update_alpha()
        elif 0 < self.timer - self.intro_production_fade_in_duration < self.intro_production_duration:
            self.intro_fade_timer = 0
        elif 0 < self.timer - self.intro_production_fade_in_duration - self.intro_production_duration < self.intro_production_fade_out_duration:
            self.intro_fade_timer += dt
            alpha = int((255 / 3) * (3 - self.intro_fade_timer))
            self.intro_production_text.alpha = alpha
            self.intro_production_text.update_alpha()
        elif 0 < self.timer - self.intro_production_fade_sum_duration < self.animation_durations:
            # (I) Sin function light flow
            self.light_circles = [(self.radius * math.cos(
                math.radians(self.timer / self.animation_circle_duration * 360 + 20 * i)) + self.screen.get_width() / 2,
                                   self.radius * math.sin(math.radians(
                                       self.timer / self.animation_circle_duration * 360 + (20 + (self.timer - self.intro_production_fade_sum_duration) * 15) * i)) + self.screen.get_height() / 2)
                                  for i in range(5)]
        else:
            self.intro_status = False

    def render(self, *args, **kwargs):
        # (I) Sin function light flow
        for light_circle in self.light_circles:
            pygame.draw.circle(self.screen, (255, 255, 255), (int(light_circle[0]), int(light_circle[1])), self.light_circle_radius)

        if self.timer < self.intro_production_fade_sum_duration:
            self.intro_production_text.render(self.screen)
