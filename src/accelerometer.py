"""
accelerometer.py

ADXL345 helper for Thunder Fighter.
"""

import time
import adafruit_adxl34x


class Accelerometer:
    def __init__(self, i2c, alpha=0.4, deadzone=0.05):
        """
        i2c: I2C object from busio.I2C
        alpha: low-pass filter factor
        deadzone: ignore very small movements near 0g
        """
        self._sensor = adafruit_adxl34x.ADXL345(i2c)
        self._alpha = alpha
        self._deadzone = deadzone

        self._base_x = 0.0
        self._base_y = 0.0

        self._fx = 0.0
        self._fy = 0.0

    def calibrate(self, samples: int = 30, delay: float = 0.05) -> None:
        sx = 0.0
        sy = 0.0

        for _ in range(samples):
            x, y, z = self._sensor.acceleration
            sx += x
            sy += y
            time.sleep(delay)

        self._base_x = sx / samples
        self._base_y = sy / samples

        self._fx = 0.0
        self._fy = 0.0

    def get_tilt(self):
        x, y, z = self._sensor.acceleration

        dx_raw = x - self._base_x
        dy_raw = y - self._base_y

        self._fx = self._alpha * dx_raw + (1.0 - self._alpha) * self._fx
        self._fy = self._alpha * dy_raw + (1.0 - self._alpha) * self._fy

        if -self._deadzone < self._fx < self._deadzone:
            dx = 0.0
        else:
            dx = self._fx

        if -self._deadzone < self._fy < self._deadzone:
            dy = 0.0
        else:
            dy = self._fy

        return dx, dy

