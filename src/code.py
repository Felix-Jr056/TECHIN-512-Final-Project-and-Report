"""
code.py

Entry point for the ESP32.

On power-up:
- Shows an animated splash screen.
- Shows a difficulty selection menu using the rotary encoder and SSD1306 OLED.
- After a difficulty is chosen, it shows "HOLD STILL" and calibrates the accelerometer.
- Then it enters PLAYING where ThunderFighterGame runs the game.
- Game Over / Win screens show final score (0–10), then a simple High Score board,
  then allow restart without power cycling.
"""

import time
import board
from rotary_encoder import RotaryEncoder

import busio
import displayio
import terminalio
from adafruit_display_text import label
import i2cdisplaybus
import adafruit_displayio_ssd1306
import digitalio
from adafruit_debouncer import Debouncer

from difficulty import Difficulty
from accelerometer import Accelerometer
from thunder import ThunderFighterGame
from led import StatusLED
from highscore import HighScoreManager

displayio.release_displays()
i2c = busio.I2C(board.SCL, board.SDA)

display_bus = i2cdisplaybus.I2CDisplayBus(i2c, device_address=0x3C)
display = adafruit_displayio_ssd1306.SSD1306(display_bus, width=128, height=64)

def show_splash():
    for frame in range(14):
        g = displayio.Group()

        for col in range(8):
            x = 4 + col * 16

            y1 = (frame * 6 + col * 6) % 64
            y2 = (frame * 6 + col * 6 + 24) % 64

            e1 = label.Label(terminalio.FONT, text="X", x=x, y=y1)
            e2 = label.Label(terminalio.FONT, text="X", x=x, y=y2)
            g.append(e1)
            g.append(e2)

        display.root_group = g
        time.sleep(0.025)

    g = displayio.Group()
    t1 = label.Label(terminalio.FONT, text="THUNDER", x=42, y=24)
    t2 = label.Label(terminalio.FONT, text="FIGHTER", x=42, y=40)
    g.append(t1)
    g.append(t2)
    display.root_group = g
    time.sleep(3)

show_splash()

accel = Accelerometer(i2c)
led = StatusLED()
hs_manager = HighScoreManager()

encoder = RotaryEncoder(board.D0, board.D1, debounce_ms=3, pulses_per_detent=3)

pin = digitalio.DigitalInOut(board.D2)
pin.direction = digitalio.Direction.INPUT
pin.pull = digitalio.Pull.UP
btn = Debouncer(pin)

inv_pin = digitalio.DigitalInOut(board.D6)
inv_pin.direction = digitalio.Direction.INPUT
inv_pin.pull = digitalio.Pull.UP
inv_btn = Debouncer(inv_pin)

difficulty = Difficulty()
playing_drawn = False
game_over_drawn = False
win_drawn = False
highscore_drawn = False

game = None
last_time = time.monotonic()
last_index = None

led.off()

last_final_score = 0
post_game_stage = "none"   # "none", "score", "board"

# DRAW
def draw_menu(selected_index: int) -> None:
    main_group = displayio.Group()
    for i, name in enumerate(difficulty.options):
        prefix = "*" if i == selected_index else " "
        text = prefix + " " + name
        # positions from your version
        text_layer = label.Label(terminalio.FONT, text=text, x=36, y=16 + i * 16)
        main_group.append(text_layer)
    display.root_group = main_group

def draw_hold_still_screen() -> None:
    main_group = displayio.Group()
    text1 = label.Label(terminalio.FONT, text="HOLD STILL", x=32, y=24)
    text2 = label.Label(terminalio.FONT, text="Calibrating...", x=28, y=40)
    main_group.append(text1)
    main_group.append(text2)
    display.root_group = main_group

def draw_playing_screen() -> None:
    main_group = displayio.Group()
    text_layer = label.Label(terminalio.FONT, text="START!", x=48, y=30)
    main_group.append(text_layer)
    display.root_group = main_group

def draw_game_over_screen(score: int) -> None:
    main_group = displayio.Group()
    text1 = label.Label(terminalio.FONT, text="GAME OVER", x=36, y=18)
    text2 = label.Label(terminalio.FONT, text="Score: " + str(score), x=40, y=34)
    text3 = label.Label(terminalio.FONT, text="Click for highscores", x=8, y=52)
    main_group.append(text1)
    main_group.append(text2)
    main_group.append(text3)
    display.root_group = main_group

def draw_win_screen(score: int) -> None:
    main_group = displayio.Group()
    text1 = label.Label(terminalio.FONT, text="YOU WIN!", x=38, y=18)
    text2 = label.Label(terminalio.FONT, text="Score: " + str(score), x=40, y=34)
    text3 = label.Label(terminalio.FONT, text="Click for highscores", x=8, y=52)
    main_group.append(text1)
    main_group.append(text2)
    main_group.append(text3)
    display.root_group = main_group

def draw_highscore_screen(scores, last_score: int) -> None:
    main_group = displayio.Group()

    your_label = label.Label(
        terminalio.FONT,
        text="Your score: " + str(last_score),
        x=32,
        y=12,
    )
    main_group.append(your_label)

    y = 30
    for i, sc in enumerate(scores, start=1):
        line = "{}: {}".format(i, sc)
        lbl = label.Label(terminalio.FONT, text=line, x=54, y=y)
        main_group.append(lbl)
        y += 12

    display.root_group = main_group

# MAIN LOOP

while True:
    btn.update()
    inv_btn.update()

    # MENU
    if difficulty.state == Difficulty.STATE_MENU:
        playing_drawn = False
        game_over_drawn = False
        win_drawn = False
        highscore_drawn = False
        post_game_stage = "none"

        led.set((0, 0, 40))   # blue

        changed = encoder.update()
        if changed:
            index = encoder.position % len(difficulty.options)
            difficulty.set_index(index)

        if difficulty.selected_index != last_index:
            draw_menu(difficulty.selected_index)
            last_index = difficulty.selected_index

        if btn.fell:
            difficulty.confirm()

    # CALIBRATING
    elif difficulty.state == Difficulty.STATE_CALIBRATING:
        led.set((40, 40, 0))  # yellow
        draw_hold_still_screen()

        accel.calibrate()

        game = ThunderFighterGame(display, difficulty.value)
        game.reset(difficulty.value)

        last_time = time.monotonic()
        difficulty.start_playing()

    # PLAYING
    elif difficulty.state == Difficulty.STATE_PLAYING:
        if not playing_drawn:
            draw_playing_screen()
            playing_drawn = True
            game_over_drawn = False
            win_drawn = False
            highscore_drawn = False
            led.set((0, 40, 0))  # green

        now = time.monotonic()
        dt = now - last_time
        last_time = now

        dx, dy = accel.get_tilt()
        invincible_pressed = inv_btn.fell

        if game is not None:
            game.handle_input(dx, dy, invincible_pressed)
            status = game.update(dt)
            game.draw()

            if status == "game_over":
                last_final_score = game.score
                hs_manager.add_score(last_final_score)
                post_game_stage = "score"
                difficulty.game_over()

            elif status == "win":
                last_final_score = game.score
                hs_manager.add_score(last_final_score)
                post_game_stage = "score"
                difficulty.win()

    # GAME OVER
    elif difficulty.state == Difficulty.STATE_GAME_OVER:
        led.set((40, 0, 0))  # red

        if post_game_stage == "score":
            if not game_over_drawn:
                draw_game_over_screen(last_final_score)
                game_over_drawn = True
                highscore_drawn = False
            if btn.fell:
                post_game_stage = "board"
                scores = hs_manager.get_scores()
                draw_highscore_screen(scores, last_final_score)
                highscore_drawn = True

        elif post_game_stage == "board":
            if not highscore_drawn:
                scores = hs_manager.get_scores()
                draw_highscore_screen(scores, last_final_score)
                highscore_drawn = True

            if btn.fell:
                difficulty.restart()
                game = None
                post_game_stage = "none"
                last_index = None

    # WIN
    elif difficulty.state == Difficulty.STATE_WIN:
        led.set((30, 0, 30))  # purple

        if post_game_stage == "score":
            if not win_drawn:
                draw_win_screen(last_final_score)
                win_drawn = True
                highscore_drawn = False
            if btn.fell:
                post_game_stage = "board"
                scores = hs_manager.get_scores()
                draw_highscore_screen(scores, last_final_score)
                highscore_drawn = True

        elif post_game_stage == "board":
            if not highscore_drawn:
                scores = hs_manager.get_scores()
                draw_highscore_screen(scores, last_final_score)
                highscore_drawn = True

            if btn.fell:
                difficulty.restart()
                game = None
                post_game_stage = "none"
                last_index = None

    time.sleep(0.001)