
class GameStats:
    def __init__(self):
        self.stats = {
            "Stars_collected": 0,
            "Level0_asteroids_destroyed": 0,
            "Level1_asteroids_destroyed": 0,
            "Level2_asteroids_destroyed": 0,
            "Level3_asteroids_destroyed": 0,
            "Level4_asteroids_destroyed": 0,
            "Level5_asteroids_destroyed": 0,
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
