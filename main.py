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

    # Initialize Drone
    drone = Drone(env)

    # Main loop
    while env.running:

        # Update all environment variables first (dt)
        env.update()

        # for loop through the event queue
        for event in pygame.event.get():
            # Get Keys which are held down
            pressed = pygame.key.get_pressed()
            drone.check_user_input(pressed)
            # Check for quiting options
            env.check_quit_event(event)

        # Update Physics
        drone.update_physics()

        # Draw environment
        env.draw_environment()

        # Draw all obstacles
        obstacles.draw_all_obstacles()

        # Draw drone position and info
        drone.update_draw()

        # Update the display
        pygame.display.flip()

