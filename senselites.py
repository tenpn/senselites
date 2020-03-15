"""runs a sensory garden"""
from random import randrange, choice, shuffle, random
import time
from mote import Mote

def color_constant(color):
    """holds this colour"""
    while True:
        yield color

def color_random():
    """avoids repetition"""
    prev_pattern = -1
    values = [127, 200, 255]
    patterns = [[1,1,0], [1,0,1], [0,1,1], [0,0,1], [0,1,0], [1,0,0]]
    while True:
        # don't want colours too similar, and don't want black:
        pattern_index = randrange(len(patterns))
        if pattern_index == prev_pattern:
            continue
        pattern = patterns[pattern_index]
        c = [pattern[0]*choice(values), pattern[1]*choice(values), pattern[2]*choice(values)]
        yield c
        prev_pattern = pattern_index

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

    rand_cols = color_random()
    
    patterns = [pattern_floodfill, pattern_scatter, pattern_race]
    colors = [color_random, lambda: color_constant(next(rand_cols))]
    
    while True:
        pattern = choice(patterns)
        color = choice(colors)()

        for update in pattern():
            c = next(color)
            mote.set_pixel(update[0], update[1], c[0], c[1], c[2])
            mote.show()
            time.sleep(0.05)
        if random() < 0.33:
            continue
        for update in pattern_reverse(pattern()):
            c = next(color)
            mote.set_pixel(update[0], update[1], 0, 0, 0)
            mote.show()
            time.sleep(0.05)

run()
