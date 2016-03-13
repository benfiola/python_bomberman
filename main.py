import sys

import pygame

from configuration import configuration
import controller

# now, init pygame and set the screen size
pygame.init()
screen = pygame.display.set_mode(configuration.get_screen_size())
clock = pygame.time.Clock()

# we start at the title screen
controller = controller.TitleScreenController()
controller.handle_forward_controller_transition()
try:
    while not controller.should_exit:
        # this limits the framerate to 60fps.
        clock.tick(60)
        events = pygame.event.get()
        controller.process_events(events)

        # if, due to event processing, we find ourselves looking to switch to a new controller
        # this means we're switching to a new menu or 'screen'
        if controller.next_controller is not None:
            # to make things a bit more readable.
            controller.view.save()
            previous_controller = controller.previous_controller
            curr_controller = controller
            next_controller = controller.next_controller

            # set the app's controller to our next controller
            # we want to set the current controller's 'next' back to None.
            # otherwise, when/if we navigate back to it, we will immediately
            # get thrown back into this if statement.
            controller = next_controller
            curr_controller.next_controller = None

            # if previous_controler == next_controller, then we're navigating back to a previous menu.
            if previous_controller == next_controller:
              controller.handle_backward_controller_transition()
            else:
              controller.handle_forward_controller_transition()

except:
    import traceback
    traceback.print_exc()

sys.exit(0)