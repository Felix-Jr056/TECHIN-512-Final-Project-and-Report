"""
difficulty.py

Difficulty + basic game states:
- STATE_MENU         : choosing difficulty
- STATE_CALIBRATING  : accelerometer calibration
- STATE_PLAYING      : game running
- STATE_GAME_OVER    : game ended, can restart
- STATE_WIN          : finished all levels successfully
"""

class Difficulty:
    STATE_MENU = 0
    STATE_CALIBRATING = 1
    STATE_PLAYING = 2
    STATE_GAME_OVER = 3
    STATE_WIN = 4

    def __init__(self):
        self.options = ["EASY", "MEDIUM", "HARD"]
        self.selected_index = 0
        self.state = Difficulty.STATE_MENU
        self.value = None

    def selected(self):
        return self.options[self.selected_index]

    def set_index(self, index: int) -> None:
        self.selected_index = index % len(self.options)

    def confirm(self) -> None:
        if self.state == Difficulty.STATE_MENU:
            self.value = self.selected
            self.state = Difficulty.STATE_CALIBRATING

    def start_playing(self) -> None:
        if self.state == Difficulty.STATE_CALIBRATING:
            self.state = Difficulty.STATE_PLAYING

    def game_over(self) -> None:
        if self.state == Difficulty.STATE_PLAYING:
            self.state = Difficulty.STATE_GAME_OVER

    def win(self) -> None:
        if self.state == Difficulty.STATE_PLAYING:
            self.state = Difficulty.STATE_WIN

    def restart(self) -> None:
        if self.state in (Difficulty.STATE_GAME_OVER, Difficulty.STATE_WIN):
            self.state = Difficulty.STATE_MENU
            self.selected_index = 0
            self.value = None