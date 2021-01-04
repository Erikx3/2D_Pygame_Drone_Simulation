""" Class to handle all environment and setting related stuff"""

import pygame


class Environment:
    def __init__(self):
        # --------- Environment Settings ---------
        # Define conversion rate between pixel and metres
        self.m_to_pxl = 100
        # Define screen width and height (possible to change, but not recommended, since menu bar not dynamically
        # scaled yet)
        self.SCREEN_WIDTH = 1200
        self.SCREEN_HEIGHT = 800

        # ---------- Rest of init (DO NOT CHANGE) ----------
        # Initialize pygame
        pygame.init()
        # Define colors
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.BLUE = (0, 0, 255)
        self.GREEN = (0, 255, 0)
        self.RED = (255, 0, 0)
        self.GRAY = (150, 150, 150)
        self.YELLOW_t = (255, 255, 0, 100)
        # Define width of where Simulation takes place
        self.PLAYGROUND_WIDTH = self.SCREEN_WIDTH * 2 / 3
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
        # Boolean Variables to keep track of main loop modes
        self.running = True
        self.paused = False
        self.pause_text = 'Pause'
        # Create help variables
        self.MENU_MID_COORD = self.PLAYGROUND_WIDTH + (self.SCREEN_WIDTH - self.PLAYGROUND_WIDTH) / 2
        # Create buttons for menu and boolean variables
        self.editor_button = Button(environment=self, color=self.RED, x=self.MENU_MID_COORD + 80,
                                    y=150, width=100, height=67, text='Editor')
        self.editor = False
        self.fly_button = Button(self, self.GREEN, self.MENU_MID_COORD - 80, 150, 100, 67, 'Fly')
        self.flying = True
        self.editor_reset_button = Button(self, self.GRAY, self.MENU_MID_COORD + 80, 220, 75, 50, 'Reset', fontsize=22)
        self.editor_reset = False

    def update(self):
        # TODO: Check if "Fixing time Step" is necessary
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
        # Draw buttons!
        self.editor_button.draw()
        self.fly_button.draw()
        self.editor_reset_button.draw()

    def draw_environment(self):
        self.screen.fill(self.WHITE)
        self.create_game_menu()
        self.draw_pause()

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

    def check_user_input(self, event):
        """
        Function to check and evaluate all input events for the environment

        :param event: pygame input event
        """
        # Buttons related logic
        mouse_pos = pygame.mouse.get_pos()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.editor_button.is_over(mouse_pos):
                self.editor_button.color = self.GREEN
                self.fly_button.color = self.RED
                self.flying = False
                self.editor = True
            if self.fly_button.is_over(mouse_pos):
                self.fly_button.color = self.GREEN
                self.editor_button.color = self.RED
                self.flying = True
                self.editor = False
            if self.editor_reset_button.is_over(mouse_pos):
                self.editor_reset = True
        if event.type == pygame.KEYDOWN:
            # Check if user wants to pause the game
            if event.key == pygame.K_p:
                self.pause("Pause")
            if event.key == pygame.K_c:
                self.paused = False

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

    def draw_pause(self):
        if self.paused:
            self.display_text(self.pause_text, (self.PLAYGROUND_WIDTH / 2, self.SCREEN_HEIGHT / 2), 80)
            self.display_text("Press C to continue", (self.PLAYGROUND_WIDTH / 2, self.SCREEN_HEIGHT / 2 + 100), 40)

    def pause(self, text):
        self.paused = True
        self.pause_text = text

    def is_over_playground(self, pos):
        """
        Function to check, if input coordinates are within playground area

        :param pos: original pygame coordinates
        """

        if 0 < pos[0] < self.PLAYGROUND_WIDTH:
            if 0 < pos[1] < self.SCREEN_HEIGHT:
                return True
        return False


class Button:
    def __init__(self, environment, color, x, y, width, height, text='', fontsize=30):
        self.env = environment
        self.color = color
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.fontsize = fontsize

    def draw(self, outline=True):
        """
        Call to draw Button with text given during creation

        :param outline: Whether button should have black outline
        """
        if outline:
            pygame.draw.rect(self.env.screen, self.env.BLACK, (self.x - self.width/2 - 2, self.y - self.height/2 - 2, self.width + 4, self.height + 4), 0)

        pygame.draw.rect(self.env.screen, self.color, (self.x - self.width/2, self.y - self.height/2, self.width, self.height), 0)

        if self.text != '':
            font = pygame.font.SysFont('Comic Sans MS', self.fontsize)
            text_surface = font.render(self.text, True, self.env.BLACK)
            text_rect = text_surface.get_rect()
            text_rect.center = (self.x, self.y)
            self.env.screen.blit(text_surface, text_rect)

    def is_over(self, pos):
        """
        Function to check, whether mouse position is over button position

        :param pos: mouse position
        :return:
        """
        if self.x - self.width/2 < pos[0] < self.x + self.width/2:
            if self.y - self.height/2 < pos[1] < self.y + self.height/2:
                return True
        return False
