""" File to handle all drone physics, capabilities etc."""

import pygame


class Drone:
    def __init__(self, environment):
        # Make environment accessible
        self.env = environment

        self.x0 = self.env.PLAYGROUND_WIDTH/2  # Initial Position in x [m]
        self.y0 = self.env.SCREEN_HEIGHT-100  # Initial Position in y [m]

        self.x = self.x0
        self.y = self.y0

        self.radius = 0.3  # [m]

        img_path = "img/drone.png"
        self.img = pygame.image.load(img_path)
        # Rescale to drone size
        radius_pxl = int(self.radius*self.env.m_to_pxl)
        self.img = pygame.transform.scale(self.img, (radius_pxl, radius_pxl))

    def draw_drone(self):
        img_rect = self.img.get_rect()
        img_rect.center = (self.x, self.y)

        self.env.screen.blit(self.img, img_rect)

