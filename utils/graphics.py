import pygame


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


def draw_text(surface, msg, x, y, size=32, fg_colour=Colours.WHITE, bg_colour=Colours.BLACK, alpha: int = 255,
              centre: bool = True):
    font = pygame.font.Font(None, size)
    if bg_colour is not None:
        text = font.render(msg, 1, fg_colour, bg_colour)
    else:
        text = font.render(msg, 1, fg_colour)
    textpos = text.get_rect()

    if centre is True:
        textpos.centerx = x
    else:
        textpos.x = x

    textpos.centery = y
    surface.blit(text, textpos)
    surface.set_alpha(alpha)


# draw some text into an area of a surface
# automatically wraps words
# returns any text that didn't get blitted
def drawText(surface, text, color, rect, font, aa=False, bkg=None):
    rect = pygame.Rect(rect)
    y = rect.top
    lineSpacing = 2

    # get the height of the font
    fontHeight = font.size("Tg")[1]

    while text:
        i = 1

        # determine if the row of text will be outside our area
        if y + fontHeight > rect.bottom:
            break

        # determine maximum width of line
        while font.size(text[:i])[0] < rect.width and i < len(text):
            i += 1

        # if we've wrapped the text, then adjust the wrap to the last word
        if i < len(text):
            i = text.rfind(" ", 0, i) + 1

        # render the line and blit it to the surface
        if bkg:
            image = font.render(text[:i], 1, color, bkg)
            image.set_colorkey(bkg)
        else:
            image = font.render(text[:i], aa, color)

        textpos = image.get_rect()
        textpos.centerx = rect.centerx
        textpos.y = y

        surface.blit(image, (textpos))
        y += fontHeight + lineSpacing

        # remove the text we just blitted
        text = text[i:]

    return text

class spritesheet(object):
    def __init__(self, filename):
        try:
            self.sheet = pygame.image.load(filename)
        except pygame.Exception as err:
            print('Unable to load spritesheet image:', filename)
            raise err

    # Load a specific image from a specific rectangle
    def image_at(self, rectangle, colorkey = None):
        "Loads image from x,y,x+offset,y+offset"
        rect = pygame.Rect(rectangle)
        image = pygame.Surface(rect.size, depth=24)
        key = (0, 255, 0)
        image.fill(key)
        image.set_colorkey(key)
        image.blit(self.sheet, (0, 0), rect)

        return image

    # Load a whole bunch of images and return them as a list
    def images_at(self, rects, colorkey = None):
        "Loads multiple images, supply a list of coordinates"
        return [self.image_at(rect, colorkey) for rect in rects]

    # Load a whole strip of images
    def load_strip(self, rect, image_count, colorkey = None):
        "Loads a strip of images and returns them as a list"
        tups = [(rect[0]+rect[2]*x, rect[1], rect[2], rect[3])
                for x in range(image_count)]
        return self.images_at(tups, colorkey)
