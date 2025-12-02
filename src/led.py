"""
led.py

Helper class for the single NeoPixel status LED.
"""
import board
import neopixel


class StatusLED:
    def __init__(self, pin=board.D7, brightness=0.3):
        self._pixels = neopixel.NeoPixel(pin, 1, brightness=brightness, auto_write=True)

    def set(self, color):
        self._pixels[0] = color

    def off(self):
        self._pixels[0] = (0, 0, 0)