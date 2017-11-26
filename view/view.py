import logging
import os

import pygame
from pygame.locals import *

import model
import utils
from utils import Colours
from utils import drawText
from utils import draw_text


class ImageManager:
    DEFAULT_SKIN = "default"
    RESOURCES_DIR = os.path.dirname(__file__) + "\\resources\\"
    TRANSPARENT=(1,2,3)

    image_cache = {}
    skins = {}
    sprite_sheets = {}
    initialised = False

    def __init__(self):
        pass

    def initialise(self):
        if ImageManager.initialised is False:
            self.load_skins()
            self.load_sprite_sheets()

    def get_image(self, image_file_name: str, width: int = 32, height: int = 32):

        if image_file_name not in ImageManager.image_cache.keys():

            if image_file_name in self.sprite_sheets.keys():
                file_name, rect = self.sprite_sheets[image_file_name]
                filename = ImageManager.RESOURCES_DIR + file_name
            else:
                filename = ImageManager.RESOURCES_DIR + image_file_name
                rect = (0,0,width,height)

            try:
                logging.info("Loading image {0} from {1} at {2}...".format(image_file_name, filename, rect))

                image_sheet = utils.spritesheet(filename)
                original_image = image_sheet.image_at(rect)

                image = pygame.transform.scale(original_image, (width, height))

                ImageManager.image_cache[image_file_name] = image
                logging.info("Image {0} loaded and cached.".format(filename))

            except Exception as err:
                print(str(err))

        return self.image_cache[image_file_name]

    def load_skins(self):

        new_skin_name = ImageManager.DEFAULT_SKIN
        new_skin = (new_skin_name, {

            model.Objects.PLAYER: ("player.png", "player1.png", "player.png", "player2.png"),
            model.Objects.HEART: "heart.png",
            model.Objects.BLOCK: "Block32x32.png",
            model.Objects.BLOCK_ORNATE: "Block32x32Ornate.png",
            model.Objects.BLOCK_HEXAGON: "Hexagon.png",
            model.Objects.BLOCK_TOP: "BlockFront.png",
            model.Objects.BLOCK_BOTTOM: "BlockBack.png",
            model.Objects.BLOCK_RIGHT: "BlockRight.png",
            model.Objects.BLOCK_LEFT: "BlockLeft.png",
            model.Objects.BLOCK_LEFT_SLOPE: "BlockSlopeSW.png",
            model.Objects.BLOCK_RIGHT_SLOPE: "BlockSlopeSE.png",
            model.Objects.BLOCK_LEFT_BACK_SLOPE: "BlockSlopeNW.png",
            model.Objects.BLOCK_RIGHT_BACK_SLOPE: "BlockSlopeNE.png",
            model.Objects.BLOCK_ARCH_NE: "BlockArchNE.png",
            model.Objects.BLOCK_ARCH_NW: "BlockArchNW.png",
            model.Objects.BLOCK_ARCH_SE: "BlockArchSE.png",
            model.Objects.BLOCK_ARCH_SW: "BlockArchSW.png",
            model.Objects.BLUE: "Block32x32Blue2.png",
            model.Objects.PYRAMID1: "Block32x32Pyramid4.png",
            model.Objects.PYRAMID2: "Block32x32Pyramid2.png",
            model.Objects.SPHERE: "Sphere2.png",
            model.Objects.SPHERE_GREEN: "SphereGreen.png",
            model.Objects.SPHERE_BLUE: "SphereBlue.png",
            model.Objects.SQUOID: "Squoid2.png",
            model.Objects.SQUOID2: "SquoidBasic.png",
            model.Objects.KEY: ("key0.png","key1.png","key2.png","key1.png"),
            model.Objects.CYLINDER: "Cylinder.png",
            model.Objects.LAVA: ("lava_0.png","lava_1.png","lava_2.png", "lava_1.png"),

        })

        ImageManager.skins[new_skin_name] = new_skin

        new_skin_name = "forest"
        new_skin = (new_skin_name, {

            model.Objects.PLAYER: ("player.png", "player1.png", "player.png", "player2.png"),
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

    def load_sprite_sheets(self):

        sheet_file_name = "blocks_sheet_brown.png"

        self.sprite_sheets["Block32x32Pyramid2.png"] = (sheet_file_name, (128,0, 32, 32))
        self.sprite_sheets["Block32x32Pyramid4.png"] = (sheet_file_name, (160,0, 32, 32))
        self.sprite_sheets["Cylinder.png"] = (sheet_file_name, (0, 0, 32, 32))
        self.sprite_sheets["Sphere2.png"] = (sheet_file_name, (96,0, 32, 32))
        self.sprite_sheets["Hexagon.png"] = (sheet_file_name, (64,0, 32, 32))
        self.sprite_sheets["Block32x32Ornate.png"] = (sheet_file_name, (32,0, 32, 32))

        self.sprite_sheets["Block32x32.png"] = (sheet_file_name, (0,32, 32, 32))
        self.sprite_sheets["BlockFront.png"] = (sheet_file_name, (32, 32, 32, 32))
        self.sprite_sheets["BlockRight.png"] = (sheet_file_name, (64, 32, 32, 32))
        self.sprite_sheets["BlockBack.png"] = (sheet_file_name, (96, 32, 32, 32))
        self.sprite_sheets["BlockLeft.png"] = (sheet_file_name, (128, 32, 32, 32))
        self.sprite_sheets["BlockArchNE.png"] = (sheet_file_name, (192, 0, 32, 32))
        self.sprite_sheets["BlockArchSE.png"] = (sheet_file_name, (224, 0, 32, 32))
        self.sprite_sheets["BlockArchSW.png"] = (sheet_file_name, (256, 0, 32, 32))
        self.sprite_sheets["BlockArchNW.png"] = (sheet_file_name, (288, 0, 32, 32))

        self.sprite_sheets["BlockSlopeSW.png"] = (sheet_file_name, (160, 32, 32, 32))
        self.sprite_sheets["BlockSlopeNW.png"] = (sheet_file_name, (192, 32, 32, 32))
        self.sprite_sheets["BlockSlopeNE.png"] = (sheet_file_name, (224, 32, 32, 32))
        self.sprite_sheets["BlockSlopeSE.png"] = (sheet_file_name, (256, 32, 32, 32))


        sheet_file_name = "blocks_sheet_blue.png"

        self.sprite_sheets["SphereBlue.png"] = (sheet_file_name, (96,0, 32, 32))
        #self.sprite_sheets["Block32x32Blue2.png"] = (sheet_file_name, (0,32, 32, 32))

        sheet_file_name = "blocks_sheet_green.png"
        self.sprite_sheets["SphereGreen.png"] = (sheet_file_name, (96,0, 32, 32))

        sheet_file_name = "Keys.png"
        self.sprite_sheets["key0.png"] = (sheet_file_name, (0, 0, 32, 32))
        self.sprite_sheets["key1.png"] = (sheet_file_name, (32, 0, 32, 32))
        self.sprite_sheets["key2.png"] = (sheet_file_name, (64, 0, 32, 32))



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

        self.game = model

        self.title_bar = TitleBar(width, MainFrame.TITLE_HEIGHT)
        self.status_bar = StatusBar(width, MainFrame.STATUS_HEIGHT)

        play_area_height = height - MainFrame.TITLE_HEIGHT - MainFrame.STATUS_HEIGHT

        self.game_view = GameView(width, play_area_height)
        self.game_ready = GameReadyView(width, play_area_height)
        self.game_over = GameOverView(width, play_area_height)

    def initialise(self):

        super(MainFrame, self).initialise()

        self.surface = pygame.display.set_mode((self.width, self.height), DOUBLEBUF)

        os.environ["SDL_VIDEO_CENTERED"] = "1"
        pygame.init()
        pygame.display.set_caption(self.game.name)
        filename = MainFrame.RESOURCES_DIR + "icon.png"

        try:
            image = pygame.image.load(filename)
            image = pygame.transform.scale(image, (32, 32))
            pygame.display.set_icon(image)
        except Exception as err:
            print(str(err))

        self.title_bar.initialise(self.game)
        self.status_bar.initialise(self.game)
        self.game_ready.initialise(self.game)
        self.game_view.initialise(self.game)
        self.game_over.initialise(self.game)

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

        if self.game.state == model.Game.READY:
            self.game_ready.draw()
            self.surface.blit(self.game_ready.surface, (x, y))
        elif self.game.state in (model.Game.PLAYING, model.Game.PAUSED):
            self.game_view.draw()
            self.surface.blit(self.game_view.surface, (x, y))
        elif self.game.state == model.Game.GAME_OVER:
            self.game_over.draw()
            self.surface.blit(self.game_over.surface, (x, y))

        x = 0
        y = pane_rect.bottom - MainFrame.STATUS_HEIGHT

        self.surface.blit(self.status_bar.surface, (x, y))

    def process_event(self, new_event: model.Event):
        print("MainFrame event process:{0}".format(new_event))

    def tick(self):

        if self.game.state == model.Game.READY:
            self.game_ready.tick()
        elif self.game.state == model.Game.PLAYING:
            self.game_view.tick()
        elif self.game.state == model.Game.GAME_OVER:
            self.game_over.tick()

    def update(self):
        pygame.display.update()

    def end(self):
        pygame.quit()


class TitleBar(View):
    FILL_COLOUR = Colours.BLACK
    TEXT_FG_COLOUR = Colours.WHITE
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
            filename = MainFrame.RESOURCES_DIR + "jellyfish_banner.jpg"
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
                  size=int(pane_rect.height * 0.75))


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
        self.text_box = pygame.Surface((width / 2, height - 4))
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

        text_rect = pygame.Rect(0, 0, pane_rect.width / 2 - 4, pane_rect.height - 4)

        self.text_box.fill(StatusBar.BG_COLOUR)

        drawText(surface=self.text_box,
                 text=msg,
                 color=StatusBar.FG_COLOUR,
                 rect=text_rect,
                 font=pygame.font.SysFont(pygame.font.get_default_font(), StatusBar.STATUS_TEXT_FONT_SIZE),
                 bkg=StatusBar.BG_COLOUR)

        self.surface.blit(self.text_box, (pane_rect.width / 4, 4))

        if self.game.state == model.Game.PLAYING:

            y = 8
            x = int(pane_rect.width * 3 / 4)

            draw_icon(self.surface, x=x, y=y, icon_name=model.Objects.HEART, count=self.game.player.HP, tick=self.tick_count)

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
        elif self.game.state == model.Game.GAME_OVER:
            msg = "SPACE:Continue"
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


class GameReadyView(View):
    FG_COLOUR = Colours.GOLD
    BG_COLOUR = Colours.DARK_GREY

    def __init__(self, width: int, height: int = 500):
        super(GameReadyView, self).__init__()

        self.game = None
        self.hst = HighScoreTableView(width=width, height=300)

        self.surface = pygame.Surface((width, height))

    def initialise(self, game: model.Game):
        self.game = game
        self.hst.initialise(self.game.hst)

    def draw(self):
        if self.game is None:
            raise ("No Game to view!")

        self.surface.fill(GameReadyView.BG_COLOUR)

        pane_rect = self.surface.get_rect()

        x = pane_rect.centerx
        y = 20

        msg = "R E A D Y !"

        draw_text(self.surface,
                  msg=msg,
                  x=x,
                  y=y,
                  size=40,
                  fg_colour=GameReadyView.FG_COLOUR,
                  bg_colour=GameReadyView.BG_COLOUR)

        image = View.image_manager.get_skin_image(model.Objects.SQUOID, tick=self.tick_count)

        image_width = 200
        image_height = 200

        x = pane_rect.centerx - int(image_width / 2)
        y += 40
        image = pygame.transform.scale(image, (image_width, image_height))
        self.surface.blit(image, (x, y))

        x = 0
        y = pane_rect.bottom - self.hst.surface.get_height()
        self.hst.draw()
        self.surface.blit(self.hst.surface, (x, y))


class GameOverView(View):
    FG_COLOUR = Colours.WHITE
    BG_COLOUR = Colours.DARK_GREY
    SCORE_TEXT_SIZE = 22

    def __init__(self, width: int, height: int = 500):

        super(GameOverView, self).__init__()

        self.game = None
        self.hst = HighScoreTableView(width=width, height=300)

        self.surface = pygame.Surface((width, height))

    def initialise(self, game: model.Game):

        self.game = game
        self.hst.initialise(self.game.hst)

    def draw(self):

        self.surface.fill(GameOverView.BG_COLOUR)

        if self.game is None:
            raise ("No Game to view!")

        pane_rect = self.surface.get_rect()

        y = 20
        x = pane_rect.centerx

        text = "G A M E    O V E R"
        fg_colour = GameOverView.FG_COLOUR

        draw_text(self.surface,
                  msg=text,
                  x=x,
                  y=y,
                  size=30,
                  fg_colour=fg_colour,
                  bg_colour=GameOverView.BG_COLOUR)

        y += 30

        draw_text(self.surface,
                  msg="Final Scores",
                  x=x,
                  y=y,
                  size=GameOverView.SCORE_TEXT_SIZE,
                  fg_colour=GameOverView.FG_COLOUR,
                  bg_colour=GameOverView.BG_COLOUR)

        y += GameOverView.SCORE_TEXT_SIZE

        rank = 1
        scores = self.game.get_scores()
        for score in scores:
            player, score = score

            if self.game.is_high_score(score):
                fg_colour = Colours.GOLD
                text = "{0}. {1} : {2} ** High Score **".format(rank, player, score)
            else:
                fg_colour = GameOverView.FG_COLOUR
                text = "{0}. {1} : {2}".format(rank, player, score)

            draw_text(self.surface,
                      x=x,
                      y=y,
                      msg=text,
                      fg_colour=fg_colour,
                      bg_colour=GameOverView.BG_COLOUR,
                      size=GameOverView.SCORE_TEXT_SIZE
                      )
            y += GameOverView.SCORE_TEXT_SIZE
            rank += 1

        x = 0
        y = pane_rect.bottom - self.hst.surface.get_height()

        self.hst.draw()
        self.surface.blit(self.hst.surface, (x, y))


class GameView(View):
    BG_COLOUR = Colours.BLACK
    FG_COLOUR = Colours.WHITE
    TILE_WIDTH = 32
    TILE_HEIGHT = 32
    TRANSPARENT = Colours.TRANSPARENT

    def __init__(self, width: int, height: int):
        super(GameView, self).__init__()

        self.surface = pygame.Surface((width, height))

        self.game = None

    def initialise(self, game: model.Game):
        super(GameView, self).initialise()

        self.game = game

    def tick(self):
        super(GameView, self).tick()

    def draw_layer(self, surface, layer_id):

        self.floor=self.game.current_floor

        if self.floor is None:
            raise ("No Floor to view!")

        skin_name = self.floor.skin_name

        #print("drawing layer for floor {0}".format(layer_id))

        for x in range(0, self.floor.rect.width):
            for y in range(0, self.floor.rect.height):
                view_object = self.floor.get_floor_tile(x,y,layer_id)
                if view_object is not None:
                    image = View.image_manager.get_skin_image(view_object.name,
                                                              tick=self.tick_count,
                                                              width=view_object.rect.width,
                                                              height=view_object.rect.height,
                                                              skin_name=skin_name)
                    if image is not None:

                        if layer_id > 1:
                            image.set_alpha(255-(layer_id*10))
                        else:
                            image.set_alpha(255)

                        surface.blit(image, self.model_to_view(view_object.rect.x, view_object.rect.y, layer_id))


        return surface

    def draw(self):
        self.surface.fill(GameView.BG_COLOUR)

        if self.game is None:
            raise ("No Game to view!")

        current_floor = self.game.current_floor

        for layer_id in current_floor.layers.keys():
            self.draw_layer(self.surface, layer_id)


    def end(self):
        super(GameView, self).end()

    def model_to_view(self,x,y, layer_id):
        origin_x = self.surface.get_rect().width/2
        origin_y = 128
        view_x = int(origin_x + (GameView.TILE_WIDTH * x/2) - (GameView.TILE_WIDTH * y/2))
        view_y = int(origin_y + (GameView.TILE_HEIGHT * x/4) + (GameView.TILE_HEIGHT * y/4) - (layer_id * GameView.TILE_HEIGHT/2))
        return view_x, view_y


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
