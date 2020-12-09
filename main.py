"""
Main Program File to start 2D Drone Simulation
"""

import pygame
from environment import Environment
from obstacles import Obstacles


if __name__ == "__main__":

    # Initialize Environment
    env = Environment()

    # Initialize Obstacles
    obstacles = Obstacles(env)

    # Main loop
    while env.running:
        # for loop through the event queue
        for event in pygame.event.get():
            # Check for KEYDOWN event
            if event.type == pygame.KEYDOWN:
                # If the Esc key is pressed, then exit the main loop
                if event.key == pygame.K_ESCAPE:
                    env.running = False
            # Check for QUIT event.
            elif event.type == pygame.QUIT:
                env.running = False
        obstacles.draw_all_obstacles()

        # Update the display
        pygame.display.flip()
