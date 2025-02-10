import math

from srcs import utils


class LevelHandler:
    def __init__(self, min_count: int, max_count: int, growth_factor: float):
        """
        Handles level progression and bullet count calculations for weapons.

        :param min_count: The minimum bullet count at the initial level.
        :param max_count: The maximum bullet count at the highest level.
        :param growth_factor: The number of bullets added per level.
        """
        if growth_factor < 0:
            raise ValueError("growth_factor cannot be negative.")
        if max_count < min_count:
            max_count = min_count

        self.max_level = math.ceil((max_count - min_count) / growth_factor) + 1
        self.min_count = min_count
        self.max_count = max_count
        self.growth_factor = growth_factor
        self._current_level = 1

    @property
    def current_level(self):
        return self._current_level

    @current_level.setter
    def current_level(self, val):
        self._current_level = utils.clamp(val, 1, self.max_level)

    @property
    def bullet_count(self) -> int:
        count = self.min_count + (self.current_level - 1) * self.growth_factor
        return utils.clamp(int(count), 0, self.max_count)

    def level_up(self, amount):
        self.current_level += amount

    def is_max(self):
        return self.current_level >= self.max_level

    def __str__(self):
        return f"Lvl {self.current_level}{self.is_max() * " (Max)"}"

    def __repr__(self):
        return f"LevelHandler(level={self.current_level}, max_level={self.max_level}, bullet_count={self.bullet_count})"
