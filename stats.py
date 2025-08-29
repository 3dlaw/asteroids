
class GameStats:
    def __init__(self):
        self.stats = {
            "White_asteroids_destroyed": 0,
            "Blue_asteroids_destroyed": 0,
            "Green_asteroids_destroyed": 0,
            "Yellow_asteroids_destroyed": 0,
            "Orange_asteroids_destroyed": 0,
            "Red_asteroids_destroyed": 0,
            "shots_fired": 0,
            "accuracy": 0
        }

    def increment_stat(self, stat_name, amount = 1):
        if stat_name in self.stats:
            self.stats[stat_name] += amount
        else:
            self.stats[stat_name] = amount

    def accuracy(self):
        if self.stats["shots_fired"] > 0:
            hits = sum(v for k, v in self.stats.items() if "destroyed" in k)
            self.stats["accuracy"] = (hits / self.stats["shots_fired"]) * 100
