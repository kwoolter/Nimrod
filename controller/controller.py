import model
import view
import audio
import pygame
from pygame.locals import *
import os

class Controller:
    def __init__(self):

        self.model = model.Model("Nimrod")
        self.view = view.MainFrame(self.model)
        self.audio = audio.AudioManager()

        self.view.initialise()


    def run(self):

        print("Here we go....")
        self.model.print()

        os.environ["SDL_VIDEO_CENTERED"] = "1"

        FPSCLOCK = pygame.time.Clock()

        pygame.time.set_timer(USEREVENT + 1, 250)
        pygame.event.set_allowed([QUIT, KEYDOWN, KEYUP, USEREVENT])

        loop = True

        while loop is True:

            self.model.tick()

            event = self.model.get_next_event()

            while event is not None:

                self.view.process_event(event)
                self.audio.process_event(event)

                if event.type == model.Event.QUIT:
                    loop = False

                event = self.model.get_next_event()

            for event in pygame.event.get():

                if event.type == USEREVENT + 1:
                    try:

                        self.model.tick()
                        self.view.tick()

                    except Exception as err:
                        print(str(err))

                elif event.type == QUIT:
                    loop = False

            self.view.tick()
            self.view.draw()
            self.view.update()

            FPSCLOCK.tick(75)


        self.view.end()
        self.audio.end()
