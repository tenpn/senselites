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

def lerp_cols(a, lhs, rhs):
    """blends between lhs and rhs"""
    return [int((rhs[0]-lhs[0])*a + lhs[0]), int((rhs[1]-lhs[1])*a + lhs[1]), int((rhs[2]-lhs[2])*a + lhs[2])]
    
class ColorChannelFade:
    """fades between colours on one channel"""
    start_col = [0,0,0]
    end_col = [1,1,1]
    def __init__(self, start_col, end_col):
        self.start_col = start_col
        self.end_col = end_col

    def get(self, coord):
        alpha = coord[1]/15
        return lerp_cols(alpha, self.start_col, self.end_col)
    
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
    
    patterns = [pattern_floodfill, pattern_scatter, pattern_race]
    black = lambda: ColorConstant([0,0,0])
    colors = [black,
              black,
              black,
              ColorRandom,
              lambda: ColorConstant(rand_cols.get(None)),
              lambda: ColorChannelFade(rand_cols.get(None), rand_cols.get(None))]
    last_col_template = None
    last_pattern_template = None
    
    while True:
        pattern_template = choice(patterns)
        if pattern_template == last_pattern_template:
            continue
        pattern = pattern_template() if random() < 0.5 else pattern_reverse(pattern_template())

        color_template = choice(colors)
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
