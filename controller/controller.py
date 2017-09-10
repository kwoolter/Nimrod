import model
import view
import audio
import pygame
from pygame.locals import *
import os

class Controller:


    KEY_PAUSE = K_ESCAPE
    KEY_START = K_SPACE

    def __init__(self):

        self.game = model.Game("Nimrod")
        self.view = view.MainFrame(self.game)
        self.audio = audio.AudioManager()




    def run(self):

        self.game.initialise()
        self.view.initialise()

        os.environ["SDL_VIDEO_CENTERED"] = "1"

        FPSCLOCK = pygame.time.Clock()

        pygame.time.set_timer(USEREVENT + 1, 250)
        pygame.event.set_allowed([QUIT, KEYDOWN, KEYUP, USEREVENT])

        loop = True

        while loop is True:

            self.game.tick()

            event = self.game.get_next_event()

            while event is not None:

                self.view.process_event(event)
                self.audio.process_event(event)

                if event.type == model.Event.QUIT:
                    loop = False

                event = self.game.get_next_event()

            for event in pygame.event.get():

                if event.type == USEREVENT + 1:
                    try:

                        self.game.tick()
                        self.view.tick()

                    except Exception as err:
                        print(str(err))

                elif event.type == QUIT:
                    loop = False

                elif event.type == KEYUP:

                    # If we are in playing mode...
                    if event.key == Controller.KEY_START:

                        try:
                            if self.game.state == model.Game.READY:
                                self.game.start()
                            elif self.game.state == model.Game.PLAYING:
                                self.game.pause()
                            elif self.game.state == model.Game.PAUSED:
                                self.game.pause(False)

                        except Exception as err:
                            print(str(err))

            self.view.tick()
            self.view.draw()
            self.view.update()

            FPSCLOCK.tick(75)


        self.view.end()
        self.audio.end()
