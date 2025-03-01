from srcs.classes.entity.base_unit import BaseUnit
from srcs.classes.entity.game_particle import GameParticle
from srcs.classes.weapon_classes.general_weapon import GeneralWeapon


class BoosterWeapon(GeneralWeapon):
    def _shoot(self, unit: BaseUnit, target_x: float, target_y: float) -> list[GameParticle]:
        shoot_angle = unit.angle_with_cord(target_x, target_y)
        new_bullets: list[GameParticle] = self._spawner.circular_spawn(
            unit.x, unit.y, shoot_angle, 1, unit
        )

        unit.faction.parent_list.extend(new_bullets)
        try:
            self._apply_recoil(unit, new_bullets[0].angle, self._recoil * self.level.bullet_count)
        except IndexError:
            pass
        return new_bullets

    def _start_overdrive(self):
        self._recoil *= 3

    def _end_overdrive(self):
        self._recoil /= 3