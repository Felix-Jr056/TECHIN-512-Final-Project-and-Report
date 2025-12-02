"""
highscore.py

High score manager for Thunder Fighter.
Stores top 3 scores in internal flash.
"""

DEFAULT_FILE = "highscores.txt"

class HighScoreManager:
    def __init__(self, filename: str = DEFAULT_FILE, size: int = 3):
        self._filename = filename
        self._size = size
        self._scores = self._load()

    def add_score(self, score: int) -> None:
        self._scores.append(int(score))
        self._scores.sort(reverse=True)
        self._scores = self._scores[: self._size]
        self._save()

    def get_scores(self):
        return list(self._scores)

    def _load(self):
        try:
            scores = []
            with open(self._filename, "r") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        scores.append(int(line))
                    except ValueError:
                        pass

            if not scores:
                scores = []
        except OSError:
            scores = []

        while len(scores) < self._size:
            scores.append(0)

        scores.sort(reverse=True)
        return scores[: self._size]

    def _save(self):
        with open(self._filename, "w") as f:
            for s in self._scores:
                f.write(str(int(s)) + "\n")

