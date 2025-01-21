class CooldownTimer:
    def __init__(self, shoot_cd: float):
        self.shoot_cd: float = shoot_cd
        self.last_shot_time: float = -float('inf')  # Initial value indicates no shot fired yet.

    def clear(self):
        self.last_shot_time = -float('inf')

    def is_ended(self, current_time: float, auto_restart=False) -> bool:
        if current_time - self.last_shot_time >= self.shoot_cd:
            if auto_restart:
                self.start_timer(current_time)
            return True
        return False

    def start_timer(self, current_time: float):
        self.last_shot_time = current_time

    def get_remaining_time(self, current_time: float) -> float:
        time_since_last_shot = current_time - self.last_shot_time
        return max(0.0, self.shoot_cd - time_since_last_shot)

    def set_remaining_time(self, current_time: float, new_cd: float):
        self.last_shot_time = current_time - (self.shoot_cd - new_cd)

    def get_reload_percentage(self, current_time: float) -> float:
        time_since_last_shot = current_time - self.last_shot_time
        return min(1.0, max(0.0, time_since_last_shot / self.shoot_cd))

    def add_to_timer(self, val):
        self.last_shot_time += val
