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
    KEY_UP = K_QUOTE
    KEY_DOWN = K_SLASH
    KEY_LEFT = K_a
    KEY_RIGHT = K_z
    KEY_BATTLE = K_b
    KEY_ATTACK = K_SPACE
    KEY_END_TURN = K_ESCAPE

    def __init__(self):

        self.game = model.Game("SQUOIDS")
        self.view = view.MainFrame(self.game, 1250, 800)
        self.audio = audio.AudioManager()

        self.initialise()

    def initialise(self):

        self.game.initialise()
        self.view.initialise()
        self.audio.initialise()

        pygame.mixer.pre_init(44100, -16, 2, 2048)
        pygame.mixer.init()

    def run(self):

        os.environ["SDL_VIDEO_CENTERED"] = "1"

        FPSCLOCK = pygame.time.Clock()

        pygame.time.set_timer(USEREVENT + 1, 150)
        pygame.time.set_timer(USEREVENT + 2, 500)
        pygame.event.set_allowed([QUIT, KEYUP, USEREVENT])

        loop = True

        while loop is True:

            # Loop to process game events
            event = self.game.get_next_event()

            while event is not None:

                try:

                    self.game.process_event(event)
                    self.view.process_event(event)
                    self.audio.process_event(event)
                    print(str(event))

                except Exception as err:
                    print(str(err))

                if event.type == model.Event.QUIT:
                    loop = False

                event = self.game.get_next_event()

            # Loop to process pygame events
            for event in pygame.event.get():

                # Timer events
                if event.type == USEREVENT + 1:
                    self.game.tick()
                    self.view.tick()
                    try:
                        pass



                    except Exception as err:
                        print(str(err))

                elif event.type == QUIT:
                    loop = False


                # Timer for Computer AI moves
                elif event.type == USEREVENT + 2:
                    if self.game.state == model.Game.BATTLE:
                        self.game.battle.do_auto()

                # Key pressed events
                elif event.type == KEYUP:

                    if self.game.state == model.Game.PLAYING:

                        try:
                            if event.key == Controller.KEY_LEFT:
                                self.game.move_player(-1, 0)
                            elif event.key == Controller.KEY_RIGHT:
                                self.game.move_player(1, 0)
                            elif event.key == Controller.KEY_UP:
                                self.game.move_player(0, -1)
                            elif event.key == Controller.KEY_DOWN:
                                self.game.move_player(0, 1)
                            elif event.key == Controller.KEY_PAUSE:
                                self.game.pause()
                            elif event.key == Controller.KEY_GAME_OVER:
                                self.game.game_over()
                            elif event.key == Controller.KEY_BATTLE:
                                self.game.start_battle()
                            elif event.key == K_F11:
                                self.game.get_current_floor().do_auto()


                        except Exception as err:
                            print(str(err))

                    elif self.game.state == model.Game.BATTLE:
                        #try:

                        if self.game.battle.state == model.Battle.PLAYING:
                            if event.key == K_1:
                                self.game.battle.set_current_target(model.Team.TACTIC_RANDOM)
                            elif event.key == K_2:
                                self.game.battle.set_current_target(model.Team.TACTIC_NEAREST)
                            elif event.key == K_3:
                                self.game.battle.set_current_target(model.Team.TACTIC_FURTHEST)
                            elif event.key == K_4:
                                self.game.battle.set_current_target(model.Team.TACTIC_STRONGEST)
                            elif event.key == K_5:
                                self.game.battle.set_current_target(model.Team.TACTIC_WEAKEST)
                            elif event.key == Controller.KEY_LEFT:
                                self.game.battle.move_player(-1, 0)
                            elif event.key == Controller.KEY_RIGHT:
                                self.game.battle.move_player(1, 0)
                            elif event.key == Controller.KEY_UP:
                                self.game.battle.move_player(0, -1)
                            elif event.key == Controller.KEY_DOWN:
                                self.game.battle.move_player(0, 1)
                            elif event.key == Controller.KEY_ATTACK:
                                self.game.battle.do_attack()
                            elif event.key == Controller.KEY_END_TURN:
                                self.game.battle.next_player()
                            elif event.key == K_F1:
                                self.view.battle_view.toggle_show_names()
                            elif event.key == K_F11:
                                self.game.battle.do_auto(override=True)
                            elif event.key == K_F12:
                                self.game.battle.print()

                        elif self.game.battle.state == model.Battle.END:
                            if event.key == K_F10:
                                self.game.state = model.Game.PLAYING

                        # except Exception as err:
                        #     print(str(err))

                    elif self.game.state == model.Game.PAUSED:
                        if event.key == Controller.KEY_PAUSE:
                            self.game.pause(False)

                    elif self.game.state == model.Game.READY:
                        if event.key == Controller.KEY_START:
                            self.game.start()

                    elif self.game.state == model.Game.GAME_OVER:
                        if event.key == Controller.KEY_START:
                            self.game.initialise()

            self.view.draw()
            self.view.update()

            FPSCLOCK.tick(50)

        self.view.end()
        self.audio.end()
        self.game.end()

