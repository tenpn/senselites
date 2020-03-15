"""runs a sensory garden"""
from random import randrange, choice
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
        print(c)
        yield c
        prev_pattern = pattern_index
        
def pattern_floodfill(colour):
    """fills each channel in order"""
    for channel in range(1,5):
        for pixel in range(16):
            yield (channel, pixel, next(colour))

def pattern_reverse(other_pattern):
    """sets each pixel black in reverse order of other_pattern"""
    other_reversed = reversed(list(other_pattern))
    for update in other_reversed:
        yield (update[0], update[1], [0,0,0])

def run():
    """let's goooo"""
    mote = Mote()

    mote.configure_channel(1, 16, False)
    mote.configure_channel(2, 16, False)
    mote.configure_channel(3, 16, False)
    mote.configure_channel(4, 16, False)

    rand_cols = color_random()
    while True:
        constant_cols = color_constant(next(rand_cols))
        for update in pattern_floodfill(constant_cols):
            mote.set_pixel(update[0], update[1], update[2][0], update[2][1], update[2][2])
            mote.show()
            time.sleep(0.05)
        for update in pattern_reverse(pattern_floodfill(constant_cols)):
            mote.set_pixel(update[0], update[1], update[2][0], update[2][1], update[2][2])
            mote.show()
            time.sleep(0.05)
        mote.clear()
        mote.show()

run()
