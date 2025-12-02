"""
thunder.py

Thunder Fighter main game logic.

- Player plane: "+" (or "*" when invincible)
- Enemy planes: "X" falling from top to bottom
- Player moves via tilt:
    * X axis -> horizontal (left/right)
    * Y axis -> vertical   (up/down)
- Extra button gives 2 seconds of invincibility
- Player loses if they hit an enemy while not invincible or stay still too long

Scoring:
- Player gets 1 point for each level finished.
- Max score = 10 (10 levels).
"""

import displayio
import terminalio
from adafruit_display_text import label

SPAWN_INTERVAL = 1.0
TILT_GAIN_X = 1.5
TILT_GAIN_Y = 1.5
IDLE_TIMEOUT = 5.0

LEVEL_PATTERNS = [
    [0, 0, 4, 4, 7, 7],
    [1, 7, 4, 1, 4, 7, 4],
    [0, 2, 4, 6, 4, 2, 0],
    [7, 5, 3, 1, 3, 5, 7],
    [0, 3, 6, 2, 1, 4, 7, 2],
    [1, 4, 2, 7, 5, 4, 1],
    [1, 2, 3, 7, 6, 5, 4, 1, 2, 3],
    [2, 4, 6, 4, 2, 3, 5, 7, 4],
    [0, 7, 3, 4, 1, 6, 2, 5, 7, 4, 3],
    [1, 3, 7, 5, 2, 6, 4, 0, 3, 4, 6, 5, 7, 2],
]


class ThunderFighterGame:
    def __init__(self, display, difficulty_name: str):
        self.display = display

        self.cols = 8
        self.rows = 5

        self.level_patterns = LEVEL_PATTERNS
        self.max_level = len(self.level_patterns)
        self.current_level = 1

        self.enemy_speed = self._speed_for_difficulty(difficulty_name)
        self.spawn_interval = SPAWN_INTERVAL

        self._load_pattern_for_level(self.current_level)

        self.player_x = self.cols // 2
        self.player_y = self.rows - 1

        self.last_move_x = self.player_x
        self.last_move_y = self.player_y
        self.idle_timer = 0.0

        self.enemies = []
        self.spawn_timer = 0.0

        self.invincible = False
        self.invincible_timer = 0.0

        self.score = 0

    def _speed_for_difficulty(self, name: str) -> float:
        if name == "EASY":
            return 0.5
        if name == "MEDIUM":
            return 0.9
        if name == "HARD":
            return 1.4
        return 0.5

    def _load_pattern_for_level(self, level: int) -> None:
        idx = max(0, min(level - 1, self.max_level - 1))
        self.current_pattern = self.level_patterns[idx]
        self.pattern_length = len(self.current_pattern)
        self.spawn_index = 0
        self.enemies_spawned_in_level = 0
        self.spawn_timer = 0.0

    def reset(self, difficulty_name: str = None) -> None:
        if difficulty_name is not None:
            self.enemy_speed = self._speed_for_difficulty(difficulty_name)

        self.current_level = 1
        self._load_pattern_for_level(self.current_level)

        self.player_x = self.cols // 2
        self.player_y = self.rows - 1

        self.last_move_x = self.player_x
        self.last_move_y = self.player_y
        self.idle_timer = 0.0

        self.enemies = []
        self.spawn_timer = 0.0
        self.invincible = False
        self.invincible_timer = 0.0

        self.score = 0

    def handle_input(self, dx, dy, invincible_pressed: bool) -> None:
        # X axis
        if dx is not None:
            cx = (self.cols - 1) / 2.0
            pos_x = cx + dx * TILT_GAIN_X
            pos_x = max(0.0, min(self.cols - 1, pos_x))
            self.player_x = int(pos_x + 0.5)

        # Y axis
        if dy is not None:
            cy = (self.rows - 1) / 2.0
            pos_y = cy - dy * TILT_GAIN_Y
            pos_y = max(0.0, min(self.rows - 1, pos_y))
            self.player_y = int(pos_y + 0.5)

        if invincible_pressed and not self.invincible:
            self.invincible = True
            self.invincible_timer = 2.0

    def update(self, dt: float) -> str:
        if self.invincible:
            self.invincible_timer -= dt
            if self.invincible_timer <= 0.0:
                self.invincible = False

        if self.enemies_spawned_in_level < self.pattern_length:
            self.spawn_timer += dt
            if self.spawn_timer >= self.spawn_interval:
                self.spawn_timer = 0.0
                col = self.current_pattern[self.spawn_index]
                self.spawn_index += 1
                self.enemies_spawned_in_level += 1
                self.enemies.append({"x": float(col), "y": 0.0})
        else:
            if not self.enemies:
                if self.current_level >= self.max_level:
                    self.score = self.max_level
                    return "win"
                else:
                    self.score = self.current_level
                    self.current_level += 1
                    self._load_pattern_for_level(self.current_level)

        new_enemies = []
        for e in self.enemies:
            e["y"] += self.enemy_speed * dt
            if e["y"] < self.rows:
                new_enemies.append(e)
        self.enemies = new_enemies

        if self.player_x == self.last_move_x and self.player_y == self.last_move_y:
            self.idle_timer += dt
        else:
            self.idle_timer = 0.0
            self.last_move_x = self.player_x
            self.last_move_y = self.player_y

        if self.idle_timer >= IDLE_TIMEOUT:
            return "game_over"

        if not self.invincible:
            for e in self.enemies:
                ex = int(e["x"] + 0.5)
                ey = int(e["y"] + 0.5)
                if ex == self.player_x and ey == self.player_y:
                    return "game_over"

        return "running"

    def draw(self) -> None:
        group = displayio.Group()
        level_label = label.Label(
            terminalio.FONT,
            text="LV" + str(self.current_level),
            x=0,
            y=8,
        )
        group.append(level_label)

        score_label = label.Label(
            terminalio.FONT,
            text="Sc" + str(self.score),
            x=110,
            y=8,
        )
        group.append(score_label)

        # Player
        ch = "+" if not self.invincible else "*"
        px = 4 + self.player_x * 16
        py = 10 + self.player_y * 11
        player_label = label.Label(terminalio.FONT, text=ch, x=px, y=py)
        group.append(player_label)

        # Enemies
        for e in self.enemies:
            ex = 4 + int(e["x"] + 0.5) * 16
            ey = 10 + int(e["y"] + 0.5) * 11
            enemy_label = label.Label(terminalio.FONT, text="X", x=ex, y=ey)
            group.append(enemy_label)

        if self.idle_timer <= 0.0:
            remaining = IDLE_TIMEOUT
        else:
            remaining = IDLE_TIMEOUT - self.idle_timer
            if remaining < 0:
                remaining = 0

        seconds = int(remaining + 0.5)
        countdown_label = label.Label(
            terminalio.FONT,
            text=str(seconds),
            x=112,
            y=60,
        )
        group.append(countdown_label)

        self.display.root_group = group