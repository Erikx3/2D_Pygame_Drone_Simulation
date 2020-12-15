""" File to handle all drone physics, capabilities etc."""

import pygame
import numpy as np
from tools.circle_line_intersection import circle_line_intersection


class Drone(pygame.sprite.Sprite):
    def __init__(self, environment):
        # Make environment accessible
        self.env = environment

        # --------- Settings ---------
        # TODO: Think about adding these to Game Menu
        self.radius = 0.15  # [m]
        self.drone_mass = 1  # [kg]
        self.damp_t = 0.5  # translational damping [kg/s]
        self.damp_r = 0.05  # rotational damping [kg*m^2/s]
        self.F_user_max = 1
        self.M_user_max = 0.25

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

        # Set state, forces and dynamic values in BODY FRAME!!
        self.r = 0  # Yaw Rate [rad/s]
        self.r_dot = 0  # Yaw Acc [rad/s^2]
        self.speed = np.array([0, 0])  # u, v [m/s]
        self.acc = np.array([0, 0])  # u_dot, v_dot [m/s^2]
        self.F = np.array([0, 0])  # F_xb and F_yb (total forces)
        self.F_drag = np.array([0, 0])  # F_drag_xb, F_drag_yb
        self.F_user = np.array([0.0, 0.0])  # User force input
        self.M = 0  # total moment [Nm]
        self.M_drag = 0
        self.M_user = 0.0
        self.body_to_nav = np.array([[0, 0],
                                    [0, 0]])  # Init transformation matrix
        self.J = 0.5*self.drone_mass*self.radius**2  # Inertia formula for thin circular disk

        # Add drone circle for collision detection later
        self.drone_circle = pygame.draw.circle(self.env.screen, self.env.YELLOW_t,
                                               self.env.mysys_to_pygame(self.pos), self.radius_pxl)

    # TODO: Add vector with optional buttons for displaying
    def equation_of_motion(self):
        self.body_to_nav = np.array([[np.cos(self.psi), -np.sin(self.psi)],
                                    [np.sin(self.psi), np.cos(self.psi)]])
        # simple semi-implicit-euler used here
        self.speed_nav = self.speed_nav + np.dot(self.body_to_nav, self.acc) * self.env.dt
        self.speed = np.dot(np.linalg.inv(self.body_to_nav), self.speed_nav)
        self.pos = self.pos + self.speed_nav * self.env.dt
        self.r = self.r + self.r_dot * self.env.dt
        self.psi = (self.psi + self.r * self.env.dt + 2 * np.pi) % (2 * np.pi)  # Values are always between 0 and 2 pi

    def calculate_forces(self):
        # Calculate Drag Forces
        self.F_drag = self.speed * self.damp_t * -1
        self.M_drag = self.r * self.damp_r * -1
        # Calculate total forces
        self.F = self.F_user + self.F_drag
        self.M = self.M_user + self.M_drag
        # Calculate accelerations
        # TODO: check rotation changes body's vel(acc)?? np.dot(np.array([[0, self.r], [-self.r, 0]]), self.speed)
        self.acc = self.F / self.drone_mass
        self.r_dot = self.M / self.J

    def update_physics(self):
        self.calculate_forces()
        self.equation_of_motion()

    def update_draw(self):
        self.draw_drone()
        self.draw_vectors()
        self.draw_info()

    def draw_info(self):
        speed_t_str = "Translational Speed: " + str(np.round(self.speed_nav, 2))
        speed_rot_str = "Rotational Speed: " + str(np.round(self.r, 2))
        # Need to transform for user, since positive angle in my x-y coord would mean left around is positive
        heading_str = "Heading: " + str(abs(np.round(self.psi * 180 / np.pi - 360, 1)))
        self.env.display_text(speed_t_str, (self.env.MENU_MID_COORD, self.env.SCREEN_HEIGHT - 20), 18)
        self.env.display_text(speed_rot_str, (self.env.MENU_MID_COORD, self.env.SCREEN_HEIGHT - 60), 18)
        self.env.display_text(heading_str, (self.env.MENU_MID_COORD, self.env.SCREEN_HEIGHT - 120), 18)

    def draw_drone(self):
        img = pygame.transform.rotozoom(self.orig_img, self.psi*180/np.pi, 1)
        img_rect = img.get_rect()
        img_rect.center = self.env.mysys_to_pygame(self.pos)
        # Add circle for better boundary visibility
        self.drone_circle = pygame.draw.circle(self.env.screen, self.env.YELLOW_t, img_rect.center, self.radius_pxl)
        # Add line for better heading visibility
        outer_circle_coord = self.env.mysys_to_pygame(self.pos
                                                      + self.radius * 0.8
                                                      * np.array([-np.sin(self.psi), np.cos(self.psi)]))
        pygame.draw.line(self.env.screen, self.env.BLACK, img_rect.center, outer_circle_coord, width=2)
        self.env.screen.blit(img, img_rect)

    def draw_vectors(self):
        # Draw force vectors
        max_user_F_length = 3*self.radius
        endpoint = self.env.mysys_to_pygame(self.pos + np.dot(self.body_to_nav, self.F)
                                            / self.F_user_max * max_user_F_length)
        pygame.draw.line(self.env.screen, self.env.RED, self.env.mysys_to_pygame(self.pos), endpoint)

    def check_user_input(self, pressed):
        self.F_user = np.array([0, 0])
        self.M_user = 0
        if pressed[pygame.K_LEFT]:
            self.F_user[0] += -self.F_user_max
        if pressed[pygame.K_RIGHT]:
            self.F_user[0] += self.F_user_max
        if pressed[pygame.K_UP] or pressed[pygame.K_w]:
            self.F_user[1] += self.F_user_max
        if pressed[pygame.K_DOWN] or pressed[pygame.K_s]:
            self.F_user[1] += -self.F_user_max
        if pressed[pygame.K_a]:
            self.M_user += self.M_user_max
        if pressed[pygame.K_d]:
            self.M_user += -self.M_user_max

    def check_collision(self, all_line_obstacles):
        """

        :param all_line_obstacles: list of np.ndarrays (dim=2) containing coordinates of lines
        """
        for coords in all_line_obstacles:
            for i in range(len(coords)-1):
                intersections = circle_line_intersection(self.pos, self.radius, coords[i], coords[i+1], False)
                if len(intersections) >= 1:
                    self.env.pause("YOU CRASHED")
                    self.reset_drone()

    def reset_drone(self):
        # Set navigation frame values
        self.pos = np.array([self.x0, self.y0])  # x and y
        self.psi = self.psi0  # Yaw angle [rad] (always equal to body frame, since we do not have pitch, roll)
        self.speed_nav = np.array([0, 0])

        # Set state, forces and dynamic values in BODY FRAME!!
        self.r = 0  # Yaw Rate [rad/s]
        self.r_dot = 0  # Yaw Acc [rad/s^2]
        self.speed = np.array([0, 0])  # u, v [m/s]
        self.acc = np.array([0, 0])  # u_dot, v_dot [m/s^2]
        self.F = np.array([0, 0])  # F_xb and F_yb (total forces)
        self.F_drag = np.array([0, 0])  # F_drag_xb, F_drag_yb
        self.F_user = np.array([0.0, 0.0])  # User force input
        self.M = 0  # total moment [Nm]
        self.M_drag = 0
        self.M_user = 0.0

