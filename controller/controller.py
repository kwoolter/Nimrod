import os

import pygame
from pygame.locals import *

import audio
import model
import view


class Controller:
    PLAYING = "Playing"

    KEY_PAUSE = K_ESCAPE
    KEY_START = K_SPACE
    KEY_GAME_OVER = K_BACKSPACE

    def __init__(self):

        self.game = model.Game("Nimrod")
        self.view = view.MainFrame(self.game,700,700)
        self.audio = audio.AudioManager()

        self.initialise()

    def initialise(self):


        self.game.initialise()
        self.view.initialise()

        new_player = model.Player("Player1")
        self.game.add_player(new_player)

        pygame.mixer.pre_init(44100, -16, 2, 2048)
        pygame.mixer.init()


    def run(self):

        os.environ["SDL_VIDEO_CENTERED"] = "1"

        FPSCLOCK = pygame.time.Clock()

        pygame.time.set_timer(USEREVENT + 1, 250)
        pygame.event.set_allowed([QUIT, KEYDOWN, KEYUP, USEREVENT])

        loop = True

        while loop is True:

            self.game.tick()

            # Loop to process game events
            event = self.game.get_next_event()

            while event is not None:

                self.view.process_event(event)
                self.audio.process_event(event)

                if event.type == model.Event.QUIT:
                    loop = False

                event = self.game.get_next_event()

            # Loop to process pygame events
            for event in pygame.event.get():

                # Timer events
                if event.type == USEREVENT + 1:
                    try:

                        self.game.tick()
                        self.view.tick()

                    except Exception as err:
                        print(str(err))

                elif event.type == QUIT:
                    loop = False

                # Key pressed events
                elif event.type == KEYUP:

                    if self.game.state == model.Game.PLAYING:
                        if event.key == Controller.KEY_PAUSE:
                            self.game.pause()
                        elif event.key == Controller.KEY_GAME_OVER:
                            self.game.game_over()

                    elif self.game.state == model.Game.PAUSED:
                        if event.key == Controller.KEY_PAUSE:
                            self.game.pause(False)

                    elif self.game.state == model.Game.READY:
                        if event.key == Controller.KEY_START:
                            self.game.start()

                    elif self.game.state == model.Game.GAME_OVER:
                        if event.key == Controller.KEY_START:
                            self.game.initialise()

            self.view.tick()
            self.view.draw()
            self.view.update()

            FPSCLOCK.tick(75)

        self.game.end()
        self.view.end()
        self.audio.end()
