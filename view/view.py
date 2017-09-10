import logging
import os

import pygame
from pygame.locals import *

import model
from utils import Colours
from utils import draw_text
from utils import drawText
import utils





class ImageManager:
    DEFAULT_SKIN = "default"
    RESOURCES_DIR = os.path.dirname(__file__) + "\\resources\\"

    image_cache = {}
    skins = {}
    initialised = False

    def __init__(self):
        pass

    def initialise(self):
        if ImageManager.initialised is False:
            self.load_skins()

    def get_image(self, image_file_name: str, width: int = 32, height: int = 32):

        if image_file_name not in ImageManager.image_cache.keys():

            filename = ImageManager.RESOURCES_DIR + image_file_name
            try:
                logging.info("Loading image {0}...".format(filename))
                original_image = pygame.image.load(filename).convert_alpha()
                image = pygame.transform.scale(original_image, (width, height))
                ImageManager.image_cache[image_file_name] = image
                logging.info("Image {0} loaded and cached.".format(filename))
                print("loading img")
            except Exception as err:
                print(str(err))

        return self.image_cache[image_file_name]

    def load_skins(self):

        new_skin_name = ImageManager.DEFAULT_SKIN
        new_skin = (new_skin_name, {

            model.Objects.PLAYER: "player.png",

        })

        ImageManager.skins[new_skin_name] = new_skin

        new_skin_name = "forest"
        new_skin = (new_skin_name, {

            model.Objects.PLAYER: "player.png",
        })

        ImageManager.skins[new_skin_name] = new_skin

    def get_skin_image(self, tile_name: str, skin_name: str = DEFAULT_SKIN, tick=0, width: int = 32, height: int = 32):

        if skin_name not in ImageManager.skins.keys():
            raise Exception("Can't find specified skin {0}".format(skin_name))

        name, tile_map = ImageManager.skins[skin_name]

        if tile_name not in tile_map.keys():
            name, tile_map = ImageManager.skins[ImageManager.DEFAULT_SKIN]
            if tile_name not in tile_map.keys():
                raise Exception("Can't find tile name '{0}' in skin '{1}'!".format(tile_name, skin_name))

        tile_file_names = tile_map[tile_name]

        image = None

        if tile_file_names is None:
            image = None
        elif isinstance(tile_file_names, tuple):
            if tick == 0:
                tile_file_name = tile_file_names[0]
            else:
                tile_file_name = tile_file_names[tick % len(tile_file_names)]

            image = self.get_image(image_file_name=tile_file_name, width=width, height=height)

        else:
            image = self.get_image(tile_file_names, width=width, height=height)

        return image


class View():
    image_manager = ImageManager()

    def __init__(self, width: int = 0, height: int = 0):
        self.tick_count = 0
        self.height = height
        self.width = width
        self.surface = None

        View.image_manager.initialise()

    def initialise(self):
        pass

    def tick(self):
        self.tick_count += 1

    def process_event(self, new_event: model.Event):
        pass

    def draw(self):
        pass

class MainFrame(View):

    RESOURCES_DIR = os.path.dirname(__file__) + "\\resources\\"

    TITLE_HEIGHT = 80
    STATUS_HEIGHT = 50

    def __init__(self, model: model.Game, width: int = 500, height: int = 500):

        super(MainFrame, self).__init__(width, height)

        self.model = model

        self.title_bar = TitleBar(width, MainFrame.TITLE_HEIGHT)
        self.status_bar = StatusBar(width, MainFrame.STATUS_HEIGHT)

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

        self.title_bar.initialise(self.model)
        self.status_bar.initialise(self.model)

    def draw(self):

        self.surface.fill(Colours.DARK_GREY)


        self.title_bar.draw()
        self.status_bar.draw()

        pane_rect = self.surface.get_rect()

        self.title_bar.draw()
        self.status_bar.draw()

        x = 0
        y = 0

        self.surface.blit(self.title_bar.surface, (x, y))

        y += MainFrame.TITLE_HEIGHT

        x = 0
        y = pane_rect.bottom - MainFrame.STATUS_HEIGHT

        self.surface.blit(self.status_bar.surface, (x, y))

    def process_event(self, new_event: model.Event):
        print("MainFrame event process:{0}".format(new_event))

    def update(self):
        pygame.display.update()

    def end(self):
        pygame.quit()



class TitleBar(View):

    FILL_COLOUR = Colours.BLACK
    TEXT_FG_COLOUR = Colours.GOLD
    TEXT_BG_COLOUR = None

    def __init__(self, width: int, height: int):

        super(TitleBar, self).__init__()

        self.surface = pygame.Surface((width, height))
        self.title = None
        self.title_image = None
        self.game = None

    def initialise(self, game: model.Game):

        super(TitleBar, self).initialise()

        self.game = game
        self.title = game.name

        try:
            filename = MainFrame.RESOURCES_DIR + "title.png"
            image = pygame.image.load(filename)
            self.title_image = pygame.transform.scale(image, (self.surface.get_width(), self.surface.get_height()))
        except Exception as err:
            print(str(err))


    def draw(self):

        super(TitleBar, self).draw()

        self.surface.fill(TitleBar.FILL_COLOUR)

        if self.title_image is not None:
            self.surface.blit(self.title_image, (0, 0))

        if self.game.state == model.Game.PLAYING:
            msg = "Playing"
        elif self.title is not None:
            msg = self.title


        pane_rect = self.surface.get_rect()
        draw_text(self.surface,
                  msg=msg,
                  x=pane_rect.centerx,
                  y=int(pane_rect.height / 2),
                  fg_colour=TitleBar.TEXT_FG_COLOUR,
                  bg_colour=TitleBar.TEXT_BG_COLOUR,
                  size=int(pane_rect.height/2))

class StatusBar(View):
    FG_COLOUR = Colours.WHITE
    BG_COLOUR = Colours.BLACK
    ICON_WIDTH = 40
    PADDING = 40
    STATUS_TEXT_FONT_SIZE = 18
    MESSAGE_TICK_DURATION = 8

    def __init__(self, width: int, height: int):

        super(StatusBar, self).__init__()

        self.surface = pygame.Surface((width, height))
        self.text_box = pygame.Surface((width/2, height-4))
        self.status_messages = []
        self.game = None

    def initialise(self, game: model.Game):

        super(StatusBar, self).initialise()

        self.game = game
        self.title = game.name
        self.current_message_number = 0


    def tick(self):

        super(StatusBar, self).tick()

        self.status_messages = list(self.game.status_messages.keys())

        if self.tick_count % StatusBar.MESSAGE_TICK_DURATION == 0:

            self.current_message_number += 1
            if self.current_message_number >= len(self.status_messages):
                self.current_message_number = 0

    def draw(self):


        self.surface.fill(StatusBar.BG_COLOUR)

        if len(self.status_messages) == 0 or self.current_message_number >= len(self.status_messages):
            msg = "{0}".format(self.game.state)
        else:
            msg = self.status_messages[self.current_message_number]

        pane_rect = self.surface.get_rect()

        text_rect = pygame.Rect(0,0,pane_rect.width/2-4,pane_rect.height-4)

        self.text_box.fill(StatusBar.BG_COLOUR)

        drawText(surface=self.text_box,
                 text=msg,
                 color=StatusBar.FG_COLOUR,
                 rect = text_rect,
                 font=pygame.font.SysFont(pygame.font.get_default_font(), StatusBar.STATUS_TEXT_FONT_SIZE),
                 bkg=StatusBar.BG_COLOUR)

        self.surface.blit(self.text_box, (pane_rect.width/4,4))

        if self.game.state == model.Game.PLAYING:

            pass

        elif self.game.state == model.Game.PAUSED:
            msg = "F8:Save   F9:Load   Esc:Resume"
            draw_text(self.surface,
                      msg=msg,
                      x=10,
                      y=int(pane_rect.height / 2),
                      fg_colour=StatusBar.FG_COLOUR,
                      bg_colour=StatusBar.BG_COLOUR,
                      size=StatusBar.STATUS_TEXT_FONT_SIZE,
                      centre=False)

        elif self.game.state == model.Game.READY:
            msg = "SPACE:Start"
            draw_text(self.surface,
                      msg=msg,
                      x=10,
                      y=int(pane_rect.height / 2),
                      fg_colour=StatusBar.FG_COLOUR,
                      bg_colour=StatusBar.BG_COLOUR,
                      size=StatusBar.STATUS_TEXT_FONT_SIZE,
                      centre=False)



class HighScoreTableView(View):

    TITLE_HEIGHT = 26
    TITLE_TEXT_SIZE = 30
    SCORE_HEIGHT = 23
    SCORE_TEXT_SIZE = 22
    FG_COLOUR = Colours.WHITE
    BG_COLOUR = Colours.BLACK

    def __init__(self, width: int, height: int = 500):

        super(HighScoreTableView, self).__init__()

        self.hst = None
        self.surface = pygame.Surface((width, height))

    def initialise(self, hst: utils.HighScoreTable):

        super(HighScoreTableView, self).initialise()

        self.hst = hst

    def draw(self):

        if self.hst is None:
            raise ("No High Score Table to view!")

        self.surface.fill(HighScoreTableView.BG_COLOUR)

        pane_rect = self.surface.get_rect()

        y = HighScoreTableView.TITLE_HEIGHT
        x = pane_rect.centerx

        draw_text(self.surface, msg="High Score Table", x=x, y=y,
                  size=HighScoreTableView.TITLE_TEXT_SIZE,
                  fg_colour=Colours.GOLD)

        if len(self.hst.table) == 0:

            y += HighScoreTableView.SCORE_HEIGHT

            draw_text(self.surface, msg="No high scores recorded",
                      x=x, y=y,
                      size=HighScoreTableView.SCORE_TEXT_SIZE,
                      fg_colour=HighScoreTableView.FG_COLOUR,
                      bg_colour=HighScoreTableView.BG_COLOUR)
        else:
            rank = 1
            for entry in self.hst.table:
                y += HighScoreTableView.SCORE_HEIGHT

                name, score = entry
                draw_text(self.surface, msg="{0}. {1} - {2}".format(rank, name, score), x=x, y=y,
                          size=HighScoreTableView.SCORE_TEXT_SIZE,
                          fg_colour=HighScoreTableView.FG_COLOUR,
                          bg_colour=HighScoreTableView.BG_COLOUR)
                rank += 1



def draw_icon(surface, x, y, icon_name, count: int = None, tick: int = 0):
    image = View.image_manager.get_skin_image(tile_name=icon_name, skin_name="default", tick=tick)
    iconpos = image.get_rect()
    iconpos.left = x
    iconpos.top = y
    surface.blit(image, iconpos)

    if count is not None:
        small_font = pygame.font.Font(None, 20)
        icon_count = small_font.render("{0:^3}".format(count), 1, Colours.BLACK, Colours.WHITE)
        count_pos = icon_count.get_rect()
        count_pos.bottom = iconpos.bottom
        count_pos.right = iconpos.right
        surface.blit(icon_count, count_pos)
