class ReloadCounter:
    def __init__(self, shoot_cd: float):
        self.shoot_cd: float = shoot_cd
        self.last_shot_time: float = -float('inf')  # Initial value indicates no shot fired yet.

    def reset(self):
        self.last_shot_time = -float('inf')

    def can_fire(self, current_time: float) -> bool:
        return current_time - self.last_shot_time >= self.shoot_cd

    def record_shot(self, current_time: float):
        self.last_shot_time = current_time

    def get_remaining_time(self, current_time: float) -> float:
        time_since_last_shot = current_time - self.last_shot_time
        return max(0.0, self.shoot_cd - time_since_last_shot)

    def get_reload_percentage(self, current_time: float) -> float:
        time_since_last_shot = current_time - self.last_shot_time
        return min(1.0, max(0.0, time_since_last_shot / self.shoot_cd))

    def record_if_can_fire(self, current_time: float) -> bool:
        """

        :return: returns value of can_fire()
        """
        if self.can_fire(current_time):
            self.record_shot(current_time)
            return True
        return False

