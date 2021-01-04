""" File to handle all drone physics, capabilities etc."""

import pygame
import numpy as np
from tools.circle_line_intersection import circle_line_intersection
from tools.line_intersect import line_intersection, distance
import random


class Drone:
    def __init__(self, environment):
        # Make environment accessible
        self.env = environment

        # --------- Settings ---------
        # TODO: Think about adding these to Game Menu
        self.radius = 0.15  # [m]
        self.drone_mass = 1  # [kg]
        self.damp_t = 0.75  # translational damping [kg/s]
        self.damp_r = 0.05  # rotational damping [kg*m^2/s]
        self.F_user_max = 1
        self.M_user_max = 0.25

        self.x0 = (self.env.PLAYGROUND_WIDTH / 2) / self.env.m_to_pxl  # Initial Position in x [m]
        self.y0 = 100 / self.env.m_to_pxl  # Initial Position in y [m]
        self.psi0 = np.pi * 0/180

        self.n_laser = 5  # Number of laser range measurements used
        self.laser_max_range = 3  # Maximum range of lasers

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

        # Add colorized drone circle for collision detection later
        self.drone_circle = pygame.draw.circle(self.env.screen, self.env.YELLOW_t,
                                               self.env.mysys_to_pygame(self.pos), self.radius_pxl)

        # Create measurement unit list
        # Add IMU and Laser to drone
        self.IMU = IMU(drone=self, log_rate=1.0, N_meas=500, noise_perc=0.05)
        self.Laser = Laser(drone=self, log_rate=1.0, N_meas=500, n_laser=self.n_laser,
                           max_range=self.laser_max_range, noise_perc=0.05)
        self.measurement_units = [self.IMU, self.Laser]
        self.simulated_laser_range = np.zeros(self.n_laser)
        self.simulated_laser_intercep_visual = np.zeros(self.n_laser*2).reshape(self.n_laser, 2)

    def update_physics(self):
        self.calculate_forces()
        self.equation_of_motion()
        # Update all measurement unit
        [unit.update(dt=self.env.dt) for unit in self.measurement_units]

    def update_draw(self):
        if self.env.laser_flag:
            self.draw_laser()
        self.draw_drone()
        self.draw_vectors()
        self.draw_info()

    def equation_of_motion(self):
        self.body_to_nav = np.array([[np.cos(self.psi), -np.sin(self.psi)],
                                    [np.sin(self.psi), np.cos(self.psi)]])
        # simple semi-implicit-euler used here
        self.speed_nav = self.speed_nav + np.dot(self.body_to_nav, self.acc) * self.env.dt
        self.speed = np.dot(np.linalg.inv(self.body_to_nav), self.speed_nav)  # More stable to reverse it again here
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
        self.acc = self.F / self.drone_mass
        self.r_dot = self.M / self.J

    def draw_info(self):
        speed_t_str = "Translational Speed: " + str(np.round(self.speed_nav, 2))
        speed_rot_str = "Rotational Speed: " + str(np.round(self.r, 2))
        # Need to transform for user, since positive angle in my x-y coord would mean left around is positive
        heading_str = "Heading: " + str(abs(np.round(self.psi * 180 / np.pi - 360, 1)))
        self.env.display_text(speed_t_str, (self.env.MENU_MID_COORD, self.env.SCREEN_HEIGHT - 10), 16)
        self.env.display_text(speed_rot_str, (self.env.MENU_MID_COORD, self.env.SCREEN_HEIGHT - 30), 16)
        self.env.display_text(heading_str, (self.env.MENU_MID_COORD, self.env.SCREEN_HEIGHT - 50), 16)

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
        max_user_F_length = 3 * self.radius
        endpoint = self.env.mysys_to_pygame(self.pos + np.dot(self.body_to_nav, self.F)
                                            / self.F_user_max * max_user_F_length)
        pygame.draw.line(self.env.screen, self.env.BLUE, self.env.mysys_to_pygame(self.pos), endpoint)

    def draw_laser(self):
        for point in self.simulated_laser_intercep_visual:
            p_t = self.env.mysys_to_pygame(point)
            pygame.draw.line(self.env.screen, self.env.RED, self.env.mysys_to_pygame(self.pos), p_t)
            pygame.draw.circle(self.env.screen, self.env.RED, p_t, 2)

    def apply_forces(self, F, M):
        """
        This function should be used as an interface for other programs later to apply forces on drone

        :param F: Translational Force as 2-dim array [N]
        :param M: Rotational Force as 1 dim [Nm]
        """

        self.F_user = np.array(F)
        self.M_user = M

    def check_user_input(self, pressed):
        M_temp = 0
        F_temp = [0, 0]
        if pressed[pygame.K_LEFT]:
            F_temp[0] += -self.F_user_max
        if pressed[pygame.K_RIGHT]:
            F_temp[0] += self.F_user_max
        if pressed[pygame.K_UP] or pressed[pygame.K_w]:
            F_temp[1] += self.F_user_max
        if pressed[pygame.K_DOWN] or pressed[pygame.K_s]:
            F_temp[1] += -self.F_user_max
        if pressed[pygame.K_a]:
            M_temp += self.M_user_max
        if pressed[pygame.K_d]:
            M_temp += -self.M_user_max
        self.apply_forces(F_temp, M_temp)

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

        # TODO Help function placed here for now to access obstacles, think about good way of refactoring
        self.simulate_laser_meas(self.n_laser, self.laser_max_range, all_line_obstacles)

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

        # Reset Measurement units
        [unit.reset() for unit in self.measurement_units]

    def simulate_laser_meas(self, no_laser, max_range, all_line_obs):
        """
        Help function to generate true laser range measurements
        (update self.simulated_laser_range and points for visualization)

        :param max_range: maximum range of laser measurement
        :param all_line_obs: list of np.ndarrays (dim=2) containing coordinates of lines
        :param no_laser: number of lasers
        """
        angle_step = 2*np.pi/no_laser
        current_angle = 0.0
        all_laser_dis = []  # Init to gather all laser meas
        all_laser_p_visual = []  # Init to gather all points for visualization
        temp_closest_dis = max_range  # Init
        for i_laser in range(no_laser):
            T_laser_b_to_nav = np.array([-np.sin(self.psi + current_angle), np.cos(self.psi + current_angle)])
            # Second point in navigation frame for current laser iteration
            max_laser_point = self.pos + T_laser_b_to_nav * max_range
            for coords in all_line_obs:
                for i_coord in range(len(coords) - 1):
                    intersec = line_intersection([coords[i_coord], coords[i_coord+1]], [self.pos, max_laser_point])
                    # Check if intersection available
                    if intersec:
                        temp_closest_dis = distance(self.pos, intersec)
                        max_laser_point = intersec  # When used like this, we always check to closes point found before
            # TODO: Check, what a laser would return, when out of laser range
            if temp_closest_dis == max_range:
                temp_closest_dis = np.nan
            all_laser_dis.append(temp_closest_dis)
            all_laser_p_visual.append(max_laser_point)
            current_angle += angle_step
            temp_closest_dis = max_range

        self.simulated_laser_intercep_visual = np.array(all_laser_p_visual)
        self.simulated_laser_range = np.array(all_laser_dis)

    def get_sim_laser_meas(self):
        """
        
        :return: [lasermeas_1, lasermeas_2, ..., lasermeas_n]
        """
        
        return self.simulated_laser_range


class MeasurementUnit:
    def __init__(self, drone, log_rate, N_meas):
        """
        This class should be used for each measurement unit as a parent class

        :param drone: drone it belongs to
        :param log_rate: log rate the measurement will be updated with
        :param N_meas: Number of measurements saved in the time sliding data array
        """
        self.drone = drone  # Drone Instance
        self.log_rate = log_rate  # Logging rate in [s]
        self.accumulator = 0.0  # Accumulator to check, if log time is reached
        self.timestamp = 0.0
        self.measurements = None  # Initiate measurement with next function
        self.N_meas = N_meas
        self.initialize_meas(self.N_meas)

    def update(self, dt):
        self.accumulator += dt
        if self.accumulator >= self.log_rate:
            new_meas = self.create_meas()
            self.add_meas(new_meas)
            self.accumulator -= self.log_rate
        self.timestamp += dt

    def reset(self):
        self.accumulator = 0.0  # Accumulator to check, if log time is reached
        self.timestamp = 0.0
        self.initialize_meas(self.N_meas)

    def get_current_meas(self):
        return self.measurements[0]

    def get_all_meas(self):
        return self.measurements

    def add_noise(self, data_list, perc):
        """
        Function to add random noise to a parameter by percentage
        :param data_list: data to put noise on
        :param perc: percentage of noise between 0 .. 1
        :return: np.array data with noise on it
        """

        noise_perc = random.uniform(-perc, perc)  # Generate random noise
        inp_data = np.array(data_list)  # make sure it is as array
        data_with_noise = inp_data + noise_perc * inp_data
        return data_with_noise

    def add_meas(self, new_m):
        """
        Add new measurement to sliding data array

        :param new_m: list or array with new measurements
        """
        self.measurements = np.vstack([new_m, self.measurements[0:-1]])

    def create_meas(self):
        """
        This function is supposed to be overwritten and create one list of measurements.
        This data should be generated artificially based on the real data of the drone for now.
        It must have the following format, add a suitable doc:
        :return [timestamp[s], data_1, data_2, ..., data_n]
        """
        new_meas = []
        return new_meas

    def initialize_meas(self, N_meas):
        """
        This function is supposed to be overwritten and create an initial array with row N_meas and number of columns n
        according to the following format:
        [timestamp, data_1, data_2, ..., data_n]
        """
        pass


class IMU(MeasurementUnit):
    def __init__(self, drone, log_rate, N_meas, noise_perc):
        """
        See parent class, added noise variable

        :param noise_perc: Percentage of noise in measurement (w.r.t to absolute value)
        """
        super().__init__(drone, log_rate, N_meas)
        self.noise_perc = noise_perc  # Add percentage noise to previous call, could choose other forms aswell

    def create_meas(self):
        """

        :return: list with [timestamp[s], AccX[m/s^2], AccY[m/s^2], OmegaZ[rad/s^2]]
        """
        acc_x = self.drone.acc[0]
        acc_y = self.drone.acc[1]
        omega_z = self.drone.r_dot
        noise_data = self.add_noise([acc_x, acc_y, omega_z], self.noise_perc)
        new_meas = np.hstack([self.timestamp, noise_data])
        return new_meas

    def initialize_meas(self, N_meas):
        self.measurements = np.zeros((N_meas, 4))
        self.measurements[0] = [self.timestamp, 0, 0, 0]  # AccX[m/s^2], AccY[m/s^2], OmegaZ[rad/s^2]


class Laser(MeasurementUnit):
    def __init__(self, drone, log_rate, N_meas, n_laser, max_range, noise_perc):
        """
        See parent class, added noise variable and number of lasers

        :param noise_perc: Percentage of noise in measurement (w.r.t to absolute value)
        """
        self.n_laser = n_laser  # Number of laser coming from the drone
        self.max_range = max_range
        super().__init__(drone, log_rate, N_meas)
        self.noise_perc = noise_perc  # Add percentage noise for each laser measurement and choose number of laser

    def create_meas(self):
        """

        :return: list with [timestamp[s], laserrange_1[m], laserrange_2[m], ... , laserrange_n[m]]
        """

        new_laser_meas = self.drone.get_sim_laser_meas()
        noise_data = self.add_noise(new_laser_meas, self.noise_perc)
        new_meas = np.hstack([self.timestamp, noise_data])
        return new_meas

    def initialize_meas(self, N_meas):
        self.measurements = np.zeros((N_meas, self.n_laser+1))
