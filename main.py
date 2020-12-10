"""
Main Program File to start 2D Drone Simulation
"""

import pygame
from environment import Environment
from obstacles import Obstacles
from drone import Drone


if __name__ == "__main__":

    # Initialize Environment
    env = Environment()

    # Initialize Obstacles
    obstacles = Obstacles(env)

    # Initialize drone
    drone = Drone(env)

    # Main loop
    while env.running:
        # for loop through the event queue
        for event in pygame.event.get():
            env.check_quit_event(event)

        # Draw all obstacles
        obstacles.draw_all_obstacles()
        # Draw drone position
        drone.draw_drone()

        # Update the display
        pygame.display.flip()
