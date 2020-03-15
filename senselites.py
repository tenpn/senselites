"""runs a sensory garden"""
from random import randrange, choice, shuffle, random
import time
from mote import Mote

class ColorConstant:
    """holds this colour"""
    constant_col = [0,0,0]
    def __init__(self, constant_col):
        self.constant_col = constant_col

    def get(self, coord):
        return self.constant_col

    def __repr__(self):
        return "Constant " + str(self.constant_col)

class ColorRandom:
    """avoids repetition"""
    prev_pattern = -1
    values = [127, 200, 255]
    patterns = [[1,1,0], [1,0,1], [0,1,1], [0,0,1], [0,1,0], [1,0,0]]

    def get(self, coord):
        # don't want colours too similar, and don't want black:
        pattern_index = randrange(len(self.patterns))
        if pattern_index == self.prev_pattern:
            return self.get(coord)
        self.prev_pattern = pattern_index
        pattern = self.patterns[pattern_index]
        c = [pattern[0]*choice(self.values), pattern[1]*choice(self.values), pattern[2]*choice(self.values)]
        return c

def lerp_i(a, lhs, rhs):
    return int((rhs-lhs)*a + lhs)
    
def lerp_cols(a, lhs, rhs):
    """blends between lhs and rhs"""
    return [lerp_i(a, lhs[0], rhs[0]), lerp_i(a, lhs[1], rhs[1]), lerp_i(a, lhs[2], rhs[2])]

class ColorChannelFade:
    """fades between colours on one channel"""
    start_col = [0,0,0]
    end_col = [1,1,1]
    def __init__(self, start_col, end_col):
        self.start_col = start_col
        self.end_col = end_col

    def get(self, coord):
        alpha = coord[1]/15.0
        return lerp_cols(alpha, self.start_col, self.end_col)
    
    def __repr__(self):
        return "Channel Fade " + str(self.start_col) + " > " + str(self.end_col)
    
class ColorGlobalFade:
    """fades across all pixels, chained end-to-end"""
    start_col = [0,0,0]
    end_col = [1,1,1]
    def __init__(self, start_col, end_col):
        self.start_col = start_col
        self.end_col = end_col

    def get(self, coord):
        alpha = ((coord[0]-1)*16+coord[1])/63.0
        return lerp_cols(alpha, self.start_col, self.end_col)

    def __repr__(self):
        return "Global Fade " + str(self.start_col) + " > " + str(self.end_col)
    
class ColorPixelFade:
    """fades between pixels on the same row"""
    start_col = [0,0,0]
    end_col = [1,1,1]
    def __init__(self, start_col, end_col):
        self.start_col = start_col
        self.end_col = end_col

    def get(self, coord):
        alpha = (coord[0]-1)/3.0
        return lerp_cols(alpha, self.start_col, self.end_col)
    
    def __repr__(self):
        return "Pixel Fade " + str(self.start_col) + " > " + str(self.end_col)
    
def pattern_race():
    fills = [0,0,0,0]
    completed = 0;
    while completed < 4:
        # pick an incomplete channel
        c = randrange(len(fills))
        if fills[c] == 16:
            continue
        # add to fills, set the pixel
        yield (c+1, fills[c])
        fills[c] += 1
        if fills[c] >= 16:
            completed += 1
        
        
def pattern_scatter():
    pixels = [(c,p) for c in range(1,5) for p in range(16)]
    shuffle(pixels)
    for p in pixels:
        yield (p[0], p[1])
        
def pattern_floodfill():
    """fills each channel in order"""
    for channel in range(1,5):
        for pixel in range(16):
            yield (channel, pixel)

def pattern_horizflood():
    """fills by pixel and then by channel"""
    for pixel in range(16):
        for channel in range(1,5):
            yield (channel, pixel)

def pattern_horizsnakeflood():
    """zipping back and forth"""
    for pixel in range(16):
        snakedir = range(1,5) if (pixel%2)==0 else range(4,0,-1)
        for channel in snakedir:
            yield (channel, pixel)
            
def pattern_snakeflood():
    """fills each channel in order"""
    for channel in range(1,5):
        snakedir = range(16) if (channel%2)==0 else range(15,-1,-1)
        for pixel in snakedir:
            yield (channel, pixel)
            
def pattern_reverse(other_pattern):
    """sets each pixel black in reverse order of other_pattern"""
    other_reversed = reversed(list(other_pattern))
    for update in other_reversed:
        yield (update[0], update[1])

def run():
    """let's goooo"""
    mote = Mote()

    mote.configure_channel(1, 16, False)
    mote.configure_channel(2, 16, False)
    mote.configure_channel(3, 16, False)
    mote.configure_channel(4, 16, False)

    rand_cols = ColorRandom()
    
    patterns = [
        pattern_floodfill,
        pattern_scatter,
        pattern_race,
        pattern_horizflood,
        pattern_horizsnakeflood,
        pattern_snakeflood,
    ]
    black = lambda: ColorConstant([0,0,0])
    colors = [
        ColorRandom,
        lambda: ColorConstant(rand_cols.get(None)),
        lambda: ColorChannelFade(rand_cols.get(None), rand_cols.get(None)),
        lambda: ColorGlobalFade(rand_cols.get(None), rand_cols.get(None)),
        lambda: ColorPixelFade(rand_cols.get(None), rand_cols.get(None)),
    ]
    last_col_template = None
    last_pattern_template = None
    
    while True:
        pattern_template = choice(patterns)
        if pattern_template == last_pattern_template:
            continue
        pattern = pattern_template() if random() < 0.5 else pattern_reverse(pattern_template())

        color_template = black if random() < 0.4 else choice(colors)
        if color_template == last_col_template:
            continue
        color = color_template()

        print(color)

        for update in pattern:
            c = color.get(update)
            mote.set_pixel(update[0], update[1], c[0], c[1], c[2])
            mote.show()
            time.sleep(0.05)

        last_col_template = color_template
        last_pattern_template = pattern_template
run()
