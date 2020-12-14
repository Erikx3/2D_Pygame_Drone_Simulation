""" File to handle all drone physics, capabilities etc."""

import pygame
import numpy as np


class Drone:
    def __init__(self, environment):
        # Make environment accessible
        self.env = environment

        # --------- Settings ---------
        # TODO: Think about adding these to Game Menu
        self.radius = 0.15  # [m]
        self.drone_mass = 1  # [kg]

        self.x0 = (self.env.PLAYGROUND_WIDTH / 2) / self.env.m_to_pxl  # Initial Position in x [m]
        self.y0 = 100 / self.env.m_to_pxl  # Initial Position in y [m]
        self.psi0 = 0

        # --------- Rest of init (DO NOT CHANGE) ---------
        # Load drone image
        img_path = "img/drone.png"
        self.orig_img = pygame.image.load(img_path)
        # Rescale to drone size
        self.radius_pxl = int(self.radius*self.env.m_to_pxl)
        self.orig_img = pygame.transform.scale(self.orig_img, (int(self.radius_pxl*2), int(self.radius_pxl*2)))

        # Set navigation frame values
        self.pos = np.array([self.x0, self.y0])  # x and y
        self.psi = self.psi0  # Yaw angle [rad] (always equal to body frame, since we do not have pitch, roll)
        self.speed_nav = np.array([0, 0])
        # Set state, forces and dynamic values (all in body frame!!)
        self.r = 0  # Yaw Rate [rad/s]
        self.r_dot = 0  # Yaw Acc [rad/s^2]
        self.speed = np.array([0, 0])  # x_dot, y_dot
        self.acc = np.array([0, 0])  # x_dot_dot, y_dot_dot
        self.F = np.array([0, 0])  # F_x and F_y (total forces)
        self.F_drag = np.array([0, 0])  # F_drag_x, F_drag_y
        self.F_user = np.array([0, 0])  # User force input (since 2D)

        self.body_to_nav = np.array([[0, 0],
                                    [0, 0]])

    def equation_of_motion(self):
        self.body_to_nav = np.array([[np.cos(self.psi), -np.sin(self.psi)],
                                    [np.sin(self.psi), np.cos(self.psi)]])
        # simple semi-implicit-euler used here
        self.speed = self.speed + self.acc * self.env.dt
        self.speed_nav = np.dot(self.body_to_nav, self.speed)
        self.pos = self.pos + self.speed_nav * self.env.dt
        self.psi = (self.psi + self.r + 2 * np.pi) % (2 * np.pi) # Values are always between 0 and 2 pi
        self.r = self.r + self.r_dot * self.env.dt

    def calculate_forces(self):
        self.acc = np.array([0.1, 0.1])
        self.r_dot = 0.01

    def update_physics(self):
        self.calculate_forces()
        self.equation_of_motion()

    def draw_drone(self):
        img = pygame.transform.rotozoom(self.orig_img, self.psi*180/np.pi, 1)
        img_rect = img.get_rect()
        img_rect.center = self.env.mysys_to_pygame(self.pos)
        # Add circle for better boundary visibility
        pygame.draw.circle(self.env.screen, self.env.YELLOW_t, img_rect.center, self.radius_pxl)
        self.env.screen.blit(img, img_rect)
        # TODO: Remember to draw drone only w.r.t to original picture
