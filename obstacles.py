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

        # Temporary list of coordinates during editor mode
        self.temp_coord_list = []

    def draw_all_obstacles(self):
        for i, obstacle in enumerate(self.all_obstacles):
            # Change line width for first outer boundaries
            if i == 0:
                line_width = 4
            else:
                line_width = 2
            for point in obstacle:
                pygame.draw.circle(self.env.screen, self.env.BLACK, self.env.mysys_to_pygame(point), 2)
            obstacle = self.env.mysys_to_pygame(obstacle)  # Convert from metre to pxl and coord origin
            pygame.draw.lines(surface=self.env.screen,
                              color=self.env.BLACK,
                              closed=False,
                              points=obstacle,
                              width=line_width)
        # Draw temporary coord list, which are in the making during editing
        if len(self.temp_coord_list) >= 2:
            pygame.draw.lines(surface=self.env.screen,
                              color=self.env.BLUE,
                              closed=False,
                              points=self.temp_coord_list,
                              width=2)
        # Care: Points are still in pygame system, since temporary list
        for point in self.temp_coord_list:
            pygame.draw.circle(self.env.screen, self.env.BLUE, point, 2)

    def check_user_input(self, event):
        # Pygame internal variables for left and right mouse click
        LEFT = 1
        RIGHT = 3
        mouse_pos = pygame.mouse.get_pos()
        if self.env.editor:
            # Add coordinate temporary to list
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == LEFT and self.env.is_over_playground(mouse_pos):
                self.temp_coord_list.append(list(mouse_pos))
            # Add all points to coordinates when user uses right click or hits return in editor mode
            if (event.type == pygame.MOUSEBUTTONDOWN and event.button == RIGHT and self.env.is_over_playground(mouse_pos)) or \
                    (event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN):
                if len(self.temp_coord_list) >= 2:
                    # Append temporary list of coordinates to all obstacles in my coordinate system
                    self.all_obstacles.append(self.env.pygame_to_mysys(np.array(self.temp_coord_list)))
                # Reset temp coord list
                self.temp_coord_list = []
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.temp_coord_list = []
        else:
            self.temp_coord_list = []
        if self.env.editor_reset:
            self.env.editor_reset = False
            self.reset_obstacles()

    def reset_obstacles(self):
        self.all_obstacles = [self.base_wall]
