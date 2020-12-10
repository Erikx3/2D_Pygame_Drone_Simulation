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
        # Define screen width and height
        self.SCREEN_WIDTH = 1200
        self.SCREEN_HEIGHT = 800
        # Define width of where Simulation takes place
        self.PLAYGROUND_WIDTH = self.SCREEN_WIDTH * 2 / 3
        # TODO: Add doc that one pixel corresponds to 1 cm and that everything is calculated in metres, only when we
        #  blit something we need to convert it back to pixels!!
        # Define conversion rate between pixel and metres
        self.m_to_pxl = 100

        # ---------- Further Init ----------
        # Initialize pygame
        pygame.init()
        # Create the screen object
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        # Set Caption
        pygame.display.set_caption('2D Drone Simulation by Erik')
        # Fill the screen with White
        self.screen.fill(self.WHITE)
        # Variable to keep the main loop running
        self.running = True
        # Create game menu on the right
        self.create_game_menu()

    def create_game_menu(self):
        # Add one more surface background for the buttons and the displays later
        panel_surf = pygame.Surface(
            (self.SCREEN_WIDTH - self.PLAYGROUND_WIDTH, self.SCREEN_HEIGHT))  # the size of your rect
        panel_surf.set_alpha(128)  # alpha level
        panel_surf.fill(self.GRAY)  # this fills the entire surface
        self.screen.blit(panel_surf, (self.PLAYGROUND_WIDTH, 0))  # (0,0) are the top-left coordinates
        # panel bar description
        self.display_text("Game Menu",
                          (self.PLAYGROUND_WIDTH + (self.SCREEN_WIDTH - self.PLAYGROUND_WIDTH) / 2, 50),
                          fontsize=30)

    def display_text(self, text: str, pos: tuple, fontsize: int = 12) -> None:
        """
        Function to create text with coordinates given in center!

        :param text: Text to display
        :param pos: center position of text as tuple coordinate
        :param fontsize: fontsize number
        """
        my_font = pygame.font.SysFont('Comic Sans MS', fontsize)
        text_surface = my_font.render(text, False, self.BLACK)
        text_rect = text_surface.get_rect()
        text_rect.center = pos
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
