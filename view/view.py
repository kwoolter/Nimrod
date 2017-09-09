import pygame
import model
import os

from pygame.locals import *

import model


class Colours:
    # set up the colours
    BLACK = (0, 0, 0)
    BROWN = (128, 64, 0)
    WHITE = (255, 255, 255)
    RED = (237, 28, 36)
    GREEN = (34, 177, 76)
    BLUE = (63, 72, 204)
    DARK_GREY = (40, 40, 40)
    GREY = (128, 128, 128)
    GOLD = (255, 201, 14)
    YELLOW = (255, 255, 0)
    TRANSPARENT = (255, 1, 1)

class View():

    def __init__(self, width : int = 0, height : int = 0):

        self.tick_count = 0
        self.height = height
        self.width = width
        self.surface = None

    def initialise(self):
        pass

    def tick(self):
        self.tick_count += 1

    def process_event(self, new_event : model.Event):
        pass

class MainFrame(View):

    RESOURCES_DIR = os.path.dirname(__file__) + "\\resources\\"

    def __init__(self, model : model.Model, width : int = 500, height : int = 500):
        super(MainFrame, self).__init__(width, height)

        self.model = model

    def initialise(self):

        super(MainFrame, self).initialise()

        self.surface = pygame.display.set_mode((self.width, self.height), DOUBLEBUF)

        os.environ["SDL_VIDEO_CENTERED"] = "1"
        pygame.init()
        pygame.display.set_caption(self.model.name)
        filename = MainFrame.RESOURCES_DIR + "icon.png"

        try:
            image = pygame.image.load(filename)
            image = pygame.transform.scale(image, (32, 32))
            pygame.display.set_icon(image)
        except Exception as err:
            print(str(err))


    def draw(self):

        self.surface.fill(Colours.DARK_GREY)

    def process_event(self, new_event : model.Event):
        print("MainFrame event process:{0}".format(new_event))

    def update(self):
        pygame.display.update()

    def end(self):
        pygame.quit()



