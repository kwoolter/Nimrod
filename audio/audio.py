import model
import pygame
import os


class Sounds:

    OPEN_DOOR = "open door"
    LEVEL_MUSIC = "level music"
    GAME_READY = "game ready"
    GAME_OVER = "game over"
    INVENTORY = "inventory"
    SHOP = "shop"
    UNLOCK = "unlock"
    SWITCH = "switch"
    SHOP = "shop"
    OPEN_CHEST = "open chest"
    EXPLODE = "explode"
    HP_DOWN = "HP down"
    HP_UP = "HP up"
    FOUND_KEY = "found key"
    FOUND_BOSS_KEY = "found boss key"
    FOUND_TREASURE = "found treasure"
    FOUND_MAP = "found map"
    FOUND_RUNE = "found rune"
    EFFECT_END = "effect end"
    SWAP_TILE = "swap tile"
    CHANGE_SELECTION = "change selection"
    CHANGE_FLOOR = "change floor"
    CHANGE_LEVEL = "change level"
    ERROR = "error"

class AudioManager:

    DEFAULT_THEME = "default"
    PLAYING = model.Game.PLAYING

    RESOURCES_DIR = os.path.dirname(__file__) + "\\resources\\"
    RESOURCES_DIR_MUSIC = os.path.dirname(__file__) + "\\resources\\music\\"

    def __init__(self):

        self.sound_themes = None
        self.music_themes = None
        self.sounds_cache = None
        self.current_music = None
        self.music_on = True
        self.sound_on = True

    def process_event(self, new_event: model.Event):
        print("AudioManager event process:{0}".format(new_event))
        sound = self.get_theme_sound(new_event.name, sound_theme=new_event.type)
        sound.play()

    def initialise(self):

        self.sound_themes = {}
        self.sounds_cache = {}
        self.music_themes = {}

        self.load_sound_themes()
        self.load_music_themes()

    def get_theme_sound(self, sound_name: str, sound_theme: str = DEFAULT_THEME, play=True):

        sound = None

        if self.sound_on is False:
            return None

        if sound_theme not in self.sound_themes.keys():
            sound_theme = AudioManager.DEFAULT_THEME
            if sound_theme not in self.sound_themes.keys():
                raise Exception("Can't find sound theme {0}.")

        theme = self.sound_themes[sound_theme]

        if sound_name not in theme.keys():
            theme = self.sound_themes[AudioManager.DEFAULT_THEME]

        if sound_name not in theme.keys():
            raise Exception("Can't find sound '{0}' in theme '{1}'".format(sound_name, sound_theme))

        if sound_name in self.sounds_cache.keys():
            sound = self.sounds_cache[sound_name]

        else:
            sound_file_name = theme[sound_name]
            if sound_file_name is not None:
                sound = pygame.mixer.Sound(AudioManager.RESOURCES_DIR + sound_file_name)
                self.sounds_cache[sound_name] = sound
            else:
                self.sounds_cache[sound_name] = None

        if play is True and sound is not None:
            sound.play()

        return sound

    def load_sound_themes(self):

        new_theme_name = AudioManager.DEFAULT_THEME
        new_theme = {
            model.Event.TICK: "LTTP_Menu_Cursor.wav",
            model.Game.PLAYING: "LTTP_Rupee1.wav",
            model.Game.PAUSED: "LTTP_Menu_Select.wav",
            model.Game.GAME_OVER: "LTTP_Link_Hurt.wav",
        }

        self.sound_themes[new_theme_name] = new_theme

    def load_music_themes(self):
        new_theme_name = AudioManager.DEFAULT_THEME
        new_theme = {
            Sounds.LEVEL_MUSIC: "Rains Will Fall.mp3",
            Sounds.GAME_OVER: "game_over.mp3",
            Sounds.GAME_READY: "Heroic_Age.mp3",
            Sounds.INVENTORY: "M02_Firelink Shrine.ogg",
            Sounds.INVENTORY: "01-souls-of-fire.mp3",
            Sounds.SHOP: "Heroic Age.mp3",
        }

        self.music_themes[new_theme_name] = new_theme

        new_theme_name = "winter"
        new_theme = {
            Sounds.LEVEL_MUSIC: "M02_Firelink Shrine.ogg",
            Sounds.SHOP: "07 Exploring The Ruins.mp3",
        }

        self.music_themes[new_theme_name] = new_theme

        new_theme_name = "desert"
        new_theme = {
            Sounds.LEVEL_MUSIC: "Old Road.mp3",
            Sounds.LEVEL_MUSIC: "Eastern Thought.mp3",
        }

        self.music_themes[new_theme_name] = new_theme

        new_theme_name = "chaos"
        new_theme = {
            Sounds.LEVEL_MUSIC: "Old Road.mp3",
        }

        self.music_themes[new_theme_name] = new_theme

        new_theme_name = "end"
        new_theme = {
            Sounds.LEVEL_MUSIC: "Heroic Age.mp3",
        }

        self.music_themes[new_theme_name] = new_theme

    def play_theme_music(self, music_name: str, music_theme: str = DEFAULT_THEME, repeat: int = 1):

        print("Play that funky music...{0} from {1} theme".format(music_name, music_theme))

        if self.music_on is False:
            return

        if music_theme not in self.music_themes.keys():
            music_theme = AudioManager.DEFAULT_THEME

        theme = self.music_themes[music_theme]

        if music_name not in theme.keys():
            raise Exception("Can't find sound {0} in theme {1}".format(music_name, music_theme))

        music_file_name = theme[music_name]

        try:
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.stop()
            print("playing '{0}' as the {1} music for theme {2}".format(music_file_name, music_name, music_theme))
            pygame.mixer.music.load(AudioManager.RESOURCES_DIR_MUSIC + music_file_name)
            pygame.mixer.music.play(-1)
        except Exception as err:
            print(str(err))

    def stop_music(self):

        # pygame.mixer.music.stop()
        pygame.mixer.music.fadeout(700)

    def end(self):
        pygame.mixer.quit()
