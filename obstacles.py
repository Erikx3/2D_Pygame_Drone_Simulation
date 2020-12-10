""" File to handle all kind of obstacles in the game"""

import pygame
import numpy as np


class Obstacles:
    def __init__(self, environment):
        self.env = environment
        self.base_wall = np.array(
            [[0, 0],
             [self.env.PLAYGROUND_WIDTH/self.env.m_to_pxl, 0],
             [self.env.PLAYGROUND_WIDTH/self.env.m_to_pxl, self.env.SCREEN_HEIGHT/self.env.m_to_pxl],
             [0, self.env.SCREEN_HEIGHT/self.env.m_to_pxl],
             [0, 0]]  # in [m]
        )
        self.all_obstacles = [self.base_wall]

    def draw_all_obstacles(self):
        for i, obstacle in enumerate(self.all_obstacles):
            # Change line width for first outer boundaries
            if i == 0:
                line_width = 4
            else:
                line_width = 1
            obstacle = obstacle * self.env.m_to_pxl  # Convert from metre to pxl
            pygame.draw.lines(surface=self.env.screen,
                              color=self.env.BLACK,
                              closed=False,
                              points=obstacle,
                              width=line_width)
