"""runs a sensory garden"""
from random import randrange, choice, shuffle, random
import time
from math import sqrt
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

class ColorChannelConstant:
    """one colour per channel"""
    constant_cols = []
    def __init__(self, rand_cols):
        for i in range(4):
            self.constant_cols.append(rand_cols.get(None))

    def get(self, coord):
        return self.constant_cols[coord[0]-1]

class ColorChequerboard:
    """alternating"""
    cols = []
    def __init__(self, rand_cols):
        self.cols = [rand_cols.get(None), rand_cols.get(None)]

    def get(self, coord):
        index = (coord[0]+coord[1])%2
        return self.cols[index]

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

def remap(v, in_range, out_range):
    """rescales a value from one range to another"""
    in_v_norm = (in_range[1]-v)/(in_range[1]-in_range[0])
    clamped_norm = min(1, max(0, in_v_norm))
    return out_range[0] + clamped_norm*(out_range[1] - out_range[0])
    
def lerp_i(a, lhs, rhs):
    """integer lerp"""
    return int((rhs-lhs)*a + lhs)
    
def lerp_cols(a, lhs, rhs):
    """blends between lhs and rhs"""
    return [lerp_i(a, lhs[0], rhs[0]), lerp_i(a, lhs[1], rhs[1]), lerp_i(a, lhs[2], rhs[2])]

class ColorFade:
    """handles fades"""
    start_col = [0,0,0]
    end_col = [1,1,1]
    def __init__(self, start_col, end_col):
        self.start_col = start_col
        self.end_col = end_col

    def get(self, coord):
        return lerp_cols(self.get_alpha(coord), self.start_col, self.end_col)
    
    def __repr__(self):
        return self.__class__.__name__ + " " + str(self.start_col) + " > " + str(self.end_col)
        
class ColorChannelFade(ColorFade):
    """fades between colours on one channel"""
    def get_alpha(self, coord):
        return coord[1]/15.0
    
class ColorGlobalFade(ColorFade):
    """fades across all pixels, chained end-to-end"""
    def get_alpha(self, coord):
        return ((coord[0]-1)*16+coord[1])/63.0
    
class ColorPixelFade(ColorFade):
    """fades between pixels on the same row"""
    def get_alpha(self, coord):
        return (coord[0]-1)/3.0

class ColorHorizCenterFade(ColorFade):
    """1 in the middle, 0 at the edges"""
    def get_alpha(self, coord):
        return abs(8-coord[1])/8.0
    
class ColorRadialFade(ColorFade):
    """circular"""
    def get_alpha(self, coord):
        norm_to_center = [abs(1.5-(coord[0]-1))/1.5, abs(7.5-coord[1])/7.5]
        dist_to_center = sqrt(norm_to_center[0]*norm_to_center[0] + norm_to_center[1]*norm_to_center[1])
        alpha = remap(dist_to_center, [0.1, 1.2], [0, 1])
        return alpha
    
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
        lambda: ColorChannelConstant(rand_cols),
        lambda: ColorChannelFade(rand_cols.get(None), rand_cols.get(None)),
        lambda: ColorGlobalFade(rand_cols.get(None), rand_cols.get(None)),
        lambda: ColorPixelFade(rand_cols.get(None), rand_cols.get(None)),
        lambda: ColorHorizCenterFade(rand_cols.get(None), rand_cols.get(None)),
        lambda: ColorRadialFade(rand_cols.get(None), rand_cols.get(None)),
        lambda: ColorChequerboard(rand_cols),
    ]
    last_col_template = None
    last_pattern_template = None
    
    while True:
        pattern_template = choice(patterns)
        if pattern_template == last_pattern_template:
            continue
        pattern = pattern_template() if random() < 0.5 else pattern_reverse(pattern_template())

        color_template = black if random() < 0.4 and last_col_template != None else choice(colors)
        if color_template == last_col_template:
            continue
        color = color_template()

        for update in pattern:
            c = color.get(update)
            mote.set_pixel(update[0], update[1], c[0], c[1], c[2])
            mote.show()
            time.sleep(0.05)

        last_col_template = color_template
        last_pattern_template = pattern_template
run()
