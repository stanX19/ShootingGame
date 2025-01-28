import math


class LevelHandler:
    def __init__(self, max_level: int, min_count: int, max_count: int, growth_factor: int):
        """
        Handles level progression and bullet count calculations for weapons.

        :param max_level: The maximum level the weapon can reach.
        :param min_count: The minimum bullet count at the initial level.
        :param max_count: The maximum bullet count at the highest level.
        :param growth_factor: The number of bullets added per level.
        """
        if max_level < 1:
            raise ValueError("max_level must be at least 1.")
        if min_count < 1:
            raise ValueError("min_count must be at least 1.")
        if growth_factor < 0:
            raise ValueError("growth_factor cannot be negative.")
        if max_count < min_count:
            max_count = min_count

        self.max_level = math.ceil((max_count - min_count) / growth_factor) + 1
        self.min_count = min_count
        self.max_count = max_count
        self.growth_factor = growth_factor
        self.current_level = 1

    @property
    def bullet_count(self) -> int:
        count = self.min_count + (self.current_level - 1) * self.growth_factor
        return min(count, self.max_count)

    def level_up(self):
        if self.current_level < self.max_level:
            self.current_level += 1

    def is_max(self):
        return self.current_level >= self.max_level

    def __repr__(self):
        return f"LevelHandler(level={self.current_level}, max_level={self.max_level}, bullet_count={self.bullet_count})"
