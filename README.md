# TECHIN-512-Final-Project-and-Report

# Thunder Fighter
A snappy 90s‑style Taito Arcade tilt‑to‑dodge Thunder Fighter game, simplified by removing shooting functions, just dodging enemy fighters. Every level has a incresing difficulty of enemy plane patterns.

---

## Features
- **Splash animation**: quick “falling X” intro
- **3 difficulties**: EASY (0.5 rows/s), MEDIUM (0.9), HARD (1.4)
- **10 levels**: fixed lane patterns
- **Tilt controls**: X → left/right, Y → up/down
- **Invincibility**: D6 button, 2 s; player “+” becomes “*”
- **Idle timeout**: no movement for 5 s → Game Over
- **NeoPixel feedback**: Blue (menu), Yellow (calibrate), Green (play), Red (over), Purple (win)
- **High scores**: top‑3 integers saved to `highscores.txt`
- **Readable code**: small classes and a simple `mode` loop

---

## How to Play
1. **Power on** → watch the splash.
2. **Rotate encoder** to choose **EASY / MEDIUM / HARD**, **press** to confirm.
3. **HOLD STILL** while accelerometer calibration runs (1.5 s).
4. **Tilt to dodge**: avoid `X` planes; **press button** for 2 s invincibility.
5. Clear **10 levels** (one full pattern each) to **win**.
6. **Score**: +1 per level cleared → **0–10**. End screen shows **Your score** and **top‑3**.
---

## Hardware
| Component | Model / Bus | Notes |
|---|---|---|
| MCU | Seeed XIAO ESP32‑C3 | CircuitPython |
| Display | SSD1306 128×64 OLED (I²C `0x3C`) | 128×64 mono |
| Accelerometer | ADXL345 (I²C `0x53`) | acceleration (m/s²) |
| Rotary encoder | D0 (A), D1 (B) | menu + selection |
| Button (confirm/restart) | D2 | menu confirm, restart |
| Button (invincibility) | D6 | 2 s invincibility |
| NeoPixel | D7 | 1 LED, brightness 0.3 |
| Power | LiPo + toggle switch | USB‑C cut‑out for flashing |

---

## File Structure
```
/ (CIRCUITPY)
├─ code.py                # splash → menu → calibrate → play → end
├─ thunder.py             # ThunderFighterGame
├─ accelerometer.py       # ADXL345: setup / calibrate / get_tilt
├─ difficulty.py          # difficulty selector
├─ led.py                 # NeoPixel helper
├─ highscore.py           # top‑3 (load/insert/save)
├─ rotary_encoder.py      # wrapper for rotaryio.IncrementalEncoder
└─ lib/                   # adafruit_displayio_ssd1306, display_text, adxl34x, debouncer, i2cdisplaybus
```

---

## ⚙️ Install
1. Flash **CircuitPython** for XIAO ESP32‑C3.
2. Copy **`lib/`** deps to **CIRCUITPY/lib**.
3. Copy all `.py` files to **CIRCUITPY** root.
4. Reset or power‑cycle → splash appears, then menu.

---

## 🎛️ Game Tuning (in `thunder.py`)
```py
SPAWN_INTERVAL = 1.0  # seconds (fixed spacing within a level)
TILT_GAIN_X = 1.5     # X tilt → columns (L/R)
TILT_GAIN_Y = 1.5     # Y tilt → rows (U/D)
IDLE_TIMEOUT = 5.0    # seconds without movement → Game Over

# difficulty speeds (rows/sec)
{"EASY": 0.5, "MEDIUM": 0.9, "HARD": 1.4}
```
