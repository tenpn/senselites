"""runs a sensory garden"""
from random import randrange, choice
import time
from mote import Mote


def pattern_floodfill(colour):
    """fills each channel in order"""
    for channel in range(1,5):
        for pixel in range(16):
            yield (channel, pixel, colour)

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
        
    while True:
        s = randrange(256)
        c = choice([[s,s,0], [s,0,s], [0,s,s], [0,0,s], [0,s,0], [s,0,0]])
        for update in pattern_floodfill(c):
            mote.set_pixel(update[0], update[1], update[2][0], update[2][1], update[2][2])
            mote.show()
            time.sleep(0.05)
        for update in pattern_reverse(pattern_floodfill(c)):
            mote.set_pixel(update[0], update[1], update[2][0], update[2][1], update[2][2])
            mote.show()
            time.sleep(0.05)
        mote.clear()
        mote.show()

run()
