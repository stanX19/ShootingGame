class LevelHandler:
    def __init__(self, max_level: int, max_count: int, growth_factor: int):
        self.max_level = max_level
        self.max_count = max_count
        self.growth_factor = growth_factor
        self.current_level = 1

    @property
    def bullet_count(self) -> int:
        if self.growth_factor == 0:
            return self.max_count
        return min(
            self.max_count,
            self.growth_factor * (self.current_level - 1) + 1,
        )

    def level_up(self):
        if self.current_level < self.max_level:
            self.current_level += 1

    def __repr__(self):
        return f"LevelHandler(level={self.current_level}, max_level={self.max_level}, bullet_count={self.bullet_count})"
