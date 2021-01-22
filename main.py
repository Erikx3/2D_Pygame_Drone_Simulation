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
            # Get Keys which are held down (easier for drone control)
            pressed = pygame.key.get_pressed()
            drone.check_user_input(pressed)
            # Check environment related events
            env.check_quit_event(event)
            env.check_user_input(event)
            # Check user input for editor mode
            obstacles.check_user_input(event)

        # Draw environment
        env.draw_environment()

        # Draw all obstacles
        obstacles.draw_all_obstacles()

        # Only Update Drone, if game is in flying mode
        if env.flying and not env.paused:
            # Check for collision
            drone.check_collision(obstacles.all_obstacles)
            # Update Physics
            drone.update_physics()

        # Draw drone position and info
        drone.update_draw()

        # Update the display
        pygame.display.flip()
