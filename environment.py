""" Class to handle all environment and setting related stuff"""

import pygame


class Environment:
    def __init__(self):
        # --------- Environment Settings ---------
        # Define colors
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.BLUE = (0, 0, 255)
        self.GREEN = (0, 255, 0)
        self.RED = (255, 0, 0)
        self.GRAY = (150, 150, 150)
        self.YELLOW_t = (255, 255, 0, 100)
        # Define screen width and height
        self.SCREEN_WIDTH = 1200
        self.SCREEN_HEIGHT = 800
        # Define width of where Simulation takes place
        self.PLAYGROUND_WIDTH = self.SCREEN_WIDTH * 2 / 3
        # Define conversion rate between pixel and metres
        self.m_to_pxl = 100

        # ---------- Rest of init (DO NOT CHANGE) ----------
        # Initialize pygame
        pygame.init()
        # Create clock
        self.clock = pygame.time.Clock()
        self.dt = 0
        self.total_time = 0
        # Create the screen object
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        # Set Caption
        pygame.display.set_caption('2D Drone Simulation by Erik')
        # Fill the screen with White
        self.screen.fill(self.WHITE)
        # Variable to keep the main loop running
        self.running = True
        self.paused = False
        # Create help variables
        self.MENU_MID_COORD = self.PLAYGROUND_WIDTH + (self.SCREEN_WIDTH - self.PLAYGROUND_WIDTH) / 2

    def update(self):
        # TODO: Check of "Fixing time Step" is necessary
        self.dt = self.clock.tick_busy_loop(60) / 1000  # [s]
        self.total_time += self.dt  # [s]

    def mysys_to_pygame(self, coord_array):
        """
        Convert coordinates into pygame coordinates (origin lower-left => top left, meters => pixel)

        :param coord_array: numpy array with coordinates
        """
        coord_array = coord_array * self.m_to_pxl  # Unit conversion
        # Change coord orig
        if coord_array.ndim > 1:
            coord_array[:, 1] = self.SCREEN_HEIGHT - coord_array[:, 1]
        else:
            coord_array[1] = self.SCREEN_HEIGHT - coord_array[1]
        return coord_array

    def pygame_to_mysys(self, coord_array):
        """
        Convert coordinates into my system coordinates (origin top-left => bottom-left, pixel => meters)

        :param coord_array: numpy array with coordinates
        """
        # Change coord orig
        if coord_array.ndim > 1:
            coord_array[:, 1] = self.SCREEN_HEIGHT - coord_array[:, 1]
        else:
            coord_array[1] = self.SCREEN_HEIGHT - coord_array[1]
        coord_array = coord_array/self.m_to_pxl  # Unit conversion
        return coord_array

    def create_game_menu(self):
        # Add one more surface background for the buttons and the displays later
        panel_surf = pygame.Surface(
            (self.SCREEN_WIDTH - self.PLAYGROUND_WIDTH, self.SCREEN_HEIGHT))  # the size of your rect
        panel_surf.set_alpha(128)  # alpha level
        panel_surf.fill(self.GRAY)  # this fills the entire surface
        self.screen.blit(panel_surf, (self.PLAYGROUND_WIDTH, 0))  # (0,0) are the top-left coordinates
        # panel bar description
        self.display_text("Game Menu",
                          (self.MENU_MID_COORD, 50),
                          fontsize=30)

    def draw_environment(self):
        self.screen.fill(self.WHITE)
        self.create_game_menu()

    def display_text(self, text: str, pos, fontsize: int = 12, align: str = 'center') -> None:
        """
        Function to create text with coordinates given in center!

        :param align: left or center alignment
        :param text: Text to display
        :param pos: center position of text
        :param fontsize: fontsize number
        """
        my_font = pygame.font.SysFont('Comic Sans MS', fontsize)
        text_surface = my_font.render(text, False, self.BLACK)
        text_rect = text_surface.get_rect()
        if align == 'center':
            text_rect.center = pos
        else:
            text_rect.midleft = pos
        self.screen.blit(text_surface, text_rect)

    def check_quit_event(self, event):
        """
        Function to make sure games stops when user wants to

        :param event: pygame input event
        """
        # Check for KEYDOWN event
        if event.type == pygame.KEYDOWN:
            # If the Esc key is pressed, then exit the main loop
            if event.key == pygame.K_ESCAPE:
                self.running = False
        # Check for QUIT event.
        elif event.type == pygame.QUIT:
            self.running = False
            self.paused = False

    def pause(self, text):
        self.paused = True

        while self.paused:
            for event in pygame.event.get():
                self.check_quit_event(event)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_c:
                        self.paused = False

            self.display_text(text, (self.PLAYGROUND_WIDTH / 2, self.SCREEN_HEIGHT / 2), 80)
            self.display_text("Press C to continue", (self.PLAYGROUND_WIDTH / 2, self.SCREEN_HEIGHT / 2 + 100), 40)
            # Update the display
            pygame.display.flip()
