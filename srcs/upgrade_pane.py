import math
from collections.abc import Callable
from random import shuffle, random, randint

from PIL.ImageCms import isIntentSupported

from srcs.classes.UI.button import RoundedButton
from srcs.classes.UI.pane import Pane, VPane
from srcs.classes.entity.unit import Unit
from srcs.classes.game_data import GameData
from srcs.classes.weapon_classes.base_weapon import BaseWeapon
from srcs.classes.weapon_classes.weapons_enum import MainWeaponEnum, SubWeaponEnum
from srcs.constants import SCREEN_HEIGHT, SCREEN_WIDTH, UNIT_RADIUS
from srcs.unit_classes.advanced_weapons import AdvancedWeaponsEnum
from srcs.unit_classes.basic_unit import BasicShootingUnit, BasicLazerUnit, EliteUnit
from srcs.unit_classes.spawner_unit import SpawningTurretUnit, UnitMothership
from srcs.unit_classes.turret_unit import BulletTurretUnit, LazerTurretUnit, AdvancedLazerTurretUnit, ShieldTurretUnit, \
    MissileTurretUnit


class BaseUpgrade:
    def __init__(self, data: GameData, score: int, *args, condition=lambda : 1):
        self.data: GameData = data
        self.score: int = score
        self.args: list = list(args)
        self.condition: callable = condition

    def on_click(self):
        pass

    def get_description(self):
        return f""

    def is_available(self):
        return self.score <= self.data.player.score and self.condition()

    def __str__(self):
        return f"{self.__class__.__name__}<score={self.score}, args={self.args}>"

    def __repr__(self):
        return self.__str__()


class UpgradeHull(BaseUpgrade):
    def get_description(self):
        return f"Hull Strength {self.args[0]:+}"

    def on_click(self):
        self.data.player.max_hp += self.args[0]
        self.data.player.hp += self.args[0]
        self.data.player.dmg += self.args[0] * 0.05
        self.data.player.speed -= self.args[0] * 0.01
        self.data.player.max_rad += self.args[0] * 0.1
        self.data.player.rad += self.args[0] * 0.1
        if isinstance(self.data.player, Unit):
            self.data.player.max_speed -= self.args[0] * 0.01
            self.data.player.shield.max_rad = max(self.data.player.shield.max_rad, self.data.player.max_rad + 100)


# class UpgradeHP(BaseUpgrade):
#     def get_description(self):
#         return f"HP {self.args[0]:+}"
#
#     def on_click(self):
#         self.data.player.max_hp += self.args[0]
#         self.data.player.hp += self.args[0]
#
# class UpgradeBodyDmg(BaseUpgrade):
#     def get_description(self):
#         return f"BODY DAMAGE {self.args[0]:+}"
#
#     def on_click(self):
#         self.data.player.dmg += self.args[0]

class UpgradeAgility(BaseUpgrade):
    def get_description(self):
        return f"Agility {self.args[0]:+}"

    def on_click(self):
        self.data.player.speed += self.args[0]
        if self.data.player.max_rad - self.args[0] * 3 > UNIT_RADIUS:
            self.data.player.max_rad -= self.args[0] * 3
        if self.data.player.rad - self.args[0] > UNIT_RADIUS:
            self.data.player.rad -= self.args[0] * 3
        if isinstance(self.data.player, Unit):
            self.data.player.max_speed += self.args[0]

# class UpgradeSpeed(BaseUpgrade):
#     def get_description(self):
#         return f"SPEED {self.args[0]:+}"
#
#     def on_click(self):
#         self.data.player.speed += self.args[0]
#         if isinstance(self.data.player, Unit):
#             self.data.player.max_speed += self.args[0]

# class UpgradeRad(BaseUpgrade):
#     def get_description(self):
#         return f"SIZE {self.args[0]:+}"
#
#     def on_click(self):
#         self.data.player.max_rad += self.args[0]
#         self.data.player.rad += self.args[0]
#         if isinstance(self.data.player, Unit):
#             self.data.player.shield.max_rad = max(self.data.player.shield.max_rad, self.data.player.max_rad + 100)

class UpgradeOverdriveCD(BaseUpgrade):
    def get_description(self):
        return f"Overdrive {self.args[0] * 100:+.0f}%"

    def on_click(self):
        if isinstance(self.data.player, Unit):
            self.data.player.main_weapon.overdrive_percentage += self.args[0]
            self.data.player.sub_weapon.overdrive_percentage += self.args[0]

    def is_available(self):
        player = self.data.player
        if not isinstance(player, Unit):
            return False
        max_overdrive = max(player.main_weapon.overdrive_percentage, player.sub_weapon.overdrive_percentage)
        return super().is_available() and max_overdrive < 1.0

class ChangeMainWeapon(BaseUpgrade):
    def get_description(self):
        if isinstance(self.data.player, Unit):
            return f"MAIN WEAPON {self.data.player.main_weapon.get_weapon(self.args[0])}"
        else:
            f"MAIN WEAPON {self.args[0]}"

    def on_click(self):
        if isinstance(self.data.player, Unit):
            self.data.player.main_weapon.change_weapon(self.args[0])

    def _prerequisite_is_met(self):
        if len(self.args) <= 1:
            return True
        w = self.args[1]
        player = self.data.player
        if not isinstance(w, BaseWeapon) or not isinstance(player, Unit):
            return True
        if player.main_weapon.weapon == self.args[1] and player.main_weapon.is_max():
            return True
        return False

    def is_available(self):
        return (isinstance(self.data.player, Unit)
                and self.data.player.main_weapon.weapon != self.args[0]
                and self._prerequisite_is_met() and super().is_available())

class ChangeSubWeapon(BaseUpgrade):
    def get_description(self):
        if isinstance(self.data.player, Unit):
            return f"SUB WEAPON {self.data.player.sub_weapon.get_weapon(self.args[0])}"
        else:
            f"SUB WEAPON {self.args[0]}"

    def on_click(self):
        if isinstance(self.data.player, Unit):
            self.data.player.sub_weapon.change_weapon(self.args[0])

    def _prerequisite_is_met(self):
        if len(self.args) <= 1:
            return True
        w = self.args[1]
        player = self.data.player
        if not isinstance(w, BaseWeapon) or not isinstance(player, Unit):
            return True
        if player.sub_weapon.weapon == w and player.sub_weapon.is_max():
            return True
        return False

    def is_available(self):
        return (isinstance(self.data.player, Unit)
                and self.data.player.sub_weapon.weapon != self.args[0]
                and self._prerequisite_is_met()
                and super().is_available())

class UpgradeMainWeapon(BaseUpgrade):
    def get_description(self):
        return f"MAIN WEAPON Level {self.args[0]:+}"

    def on_click(self):
        if isinstance(self.data.player, Unit):
            self.data.player.main_weapon.upgrade_weapon(self.args[0])

    def is_available(self):
        if (isinstance(self.data.player, Unit)
                and not self.data.player.main_weapon.is_max()):
            return super().is_available()
        return False

class UpgradeSubWeapon(BaseUpgrade):
    def get_description(self):
        return f"SUB WEAPON Level {self.args[0]:+}"

    def on_click(self):
        if isinstance(self.data.player, Unit):
            self.data.player.sub_weapon.upgrade_weapon(self.args[0])

    def is_available(self):
        if (isinstance(self.data.player, Unit)
                and not self.data.player.sub_weapon.is_max()):
            return super().is_available()
        return False

class UpgradeShieldStrength(BaseUpgrade):
    def get_description(self):
        return f"SHIELD STRENGTH {self.args[0]:+}"

    def on_click(self):
        if isinstance(self.data.player, Unit):
            self.data.player.shield.hp += self.args[0]
            self.data.player.shield.max_hp += self.args[0]
            self.data.player.shield.dmg = max(self.data.player.shield.dmg, self.data.player.shield.max_hp // 100)
            self.data.player.shield.max_rad += self.args[0] * 0.5
            self.data.player.shield.max_hp = max(1.0, self.data.player.shield.max_hp)

# class UpgradeShieldRad(BaseUpgrade):
#     def get_description(self):
#         return f"SHIELD SIZE {self.args[0]:+}"
#
#     def on_click(self):
#         if isinstance(self.data.player, Unit):
#             self.data.player.shield.max_rad += self.args[0]
#             self.data.player.shield.max_hp = max(1.0, self.data.player.shield.max_hp)

class UpgradeNewUnit(BaseUpgrade):
    def get_description(self):
        return f"New unit: {self.args[0].__name__}"

    def on_click(self):
        player = self.data.player
        if isinstance(player, Unit):
            # mouse = self.data.get_mouse_pos_in_map()
            # angle = player.angle_with_cord(*mouse)
            # dis = min(player.rad + 300, player.distance_with_cord(*mouse))
            x = player.x #+ math.cos(angle) * dis
            y = player.y #+ math.sin(angle) * dis
            player.faction.parent_list.append(
                self.args[0](player.faction, x, y,
                             color=player.get_greatest_parent().color, parent=player)
            )


# TODO:
#  Idea: starter upgrade, one time upgrade
#  get machine gun, missile, and shield, cost score 5, remove upgrade afterwards
class UpgradePane(VPane):
    def __init__(self, data: GameData):
        super().__init__(5, SCREEN_HEIGHT // 2 + 150, 405, SCREEN_HEIGHT - 20)
        self.data = data
        self.hide()

        self.upgrade_main_weapon = UpgradeMainWeapon(self.data, 200, 1)
        self.upgrade_sub_weapon = UpgradeSubWeapon(self.data, 200, 1)
        self.filler_upgrade = BaseUpgrade(self.data, 0)
        self.current_upgrades: list[BaseUpgrade] = []
        self.prev_upgrade_idx: int = 0
        self.upgrades: list[list[BaseUpgrade]] = [
            [
                UpgradeHull(self.data, 50, 10, condition=lambda : self.data.player.max_hp < 100),
                UpgradeHull(self.data, 1000, 100, condition=lambda : self.data.player.max_hp < 1000),
                UpgradeHull(self.data, 20000, 1000, condition=lambda : self.data.player.max_hp < 3000),
                # UpgradeBodyDmg(self.data, 50, 5, condition=lambda : self.data.player.dmg < 50),
                # UpgradeBodyDmg(self.data, 1000, 50, condition=lambda : self.data.player.dmg < 300),
                UpgradeShieldStrength(self.data, 50, 10, condition=lambda : self.data.get_player_shield_max_hp() < 100),
                UpgradeShieldStrength(self.data, 1000, 100, condition=lambda : self.data.get_player_shield_max_hp() < 1000),
                UpgradeShieldStrength(self.data, 20000, 1000, condition=lambda : self.data.get_player_shield_max_hp() < 3000),
            ], [
                UpgradeAgility(self.data, 50, 1, condition=lambda : isinstance(self.data.player, Unit) and self.data.player.max_speed < 5),
                UpgradeAgility(self.data, 1000, 5, condition=lambda : isinstance(self.data.player, Unit) and self.data.player.max_speed < 10),
                # UpgradeRad(self.data, 50, 10, condition=lambda : self.data.player.max_rad < 100),
                # UpgradeRad(self.data, 1000, 100, condition=lambda : self.data.player.max_rad < 300),
                # UpgradeShieldRad(self.data, 50, 10, condition=lambda : self.data.get_player_shield_max_rad() < 100),
                # UpgradeShieldRad(self.data, 500, 100, condition=lambda : self.data.get_player_shield_max_rad() < 2000),
            ], [
                self.upgrade_main_weapon,
                *self.generate_weapon_series(ChangeMainWeapon, [
                    [
                        MainWeaponEnum.lazer_mini,
                        [
                            [MainWeaponEnum.lazer, MainWeaponEnum.beam],
                            [MainWeaponEnum.charged_lazer, MainWeaponEnum.deleter],
                        ]
                    ], [
                        MainWeaponEnum.machine_gun,
                        [
                            [MainWeaponEnum.shotgun, MainWeaponEnum.fireworks],
                            [MainWeaponEnum.piercing_machine_gun, MainWeaponEnum.giant_canon]
                        ]
                    ]
                ], 200),
            ], [
                self.upgrade_sub_weapon,
                *self.generate_weapon_series(ChangeSubWeapon, [
                    [
                        MainWeaponEnum.missile,
                        [
                            MainWeaponEnum.swarm,
                            MainWeaponEnum.torpedo,
                            MainWeaponEnum.spike,
                            [[AdvancedWeaponsEnum.mini_spawner,
                              [AdvancedWeaponsEnum.elite_spawner, AdvancedWeaponsEnum.rammer_spawner]]]
                        ]
                    ], [
                        MainWeaponEnum.dancer
                    ], [
                        MainWeaponEnum.flash, MainWeaponEnum.warp
                    ]
                ], 200)
            ], [
                UpgradeNewUnit(self.data, 100, BasicShootingUnit),
                UpgradeNewUnit(self.data, 150, BasicLazerUnit),
                UpgradeNewUnit(self.data, 500, EliteUnit),
                UpgradeNewUnit(self.data, 100, BulletTurretUnit),
                UpgradeNewUnit(self.data, 500, SpawningTurretUnit),
                UpgradeNewUnit(self.data, 300, LazerTurretUnit),
                UpgradeNewUnit(self.data, 500, AdvancedLazerTurretUnit),
                UpgradeNewUnit(self.data, 500, ShieldTurretUnit),
                UpgradeNewUnit(self.data, 500, MissileTurretUnit),
                UpgradeNewUnit(self.data, 5000, UnitMothership),
                # UpgradeOverdriveCD(self.data, 300, 0.1),
                # UpgradeOverdriveCD(self.data, 10000, 1.0),
            ]
        ]
        self.prev_upgrade: BaseUpgrade = self.upgrades[0][0]

    def create_upgrade_button(self, upgrade: BaseUpgrade):
        def on_click():
            self.data.player.use_score(upgrade.score)
            upgrade.on_click()
            self.set_child()
            self.prev_upgrade = upgrade
            self.prev_upgrade_idx = self.current_upgrades.index(upgrade)
        return RoundedButton(f"{upgrade.score:4} {upgrade.get_description()}", on_click)

    # TODO:
    #  make [x [[a, b], [c, d]]] means two different pathways x--a--b and x--c--d
    def generate_weapon_series(self, upgrade_class:type[BaseUpgrade],
                               weapon_series: list, score: int, roots: list|None=None,
                               is_series:bool=True):
        roots = roots if roots else []
        ret = []
        prev_w = roots
        child_is_series = all(isinstance(i, list) for i in weapon_series)
        is_series = is_series and not child_is_series

        for w in weapon_series:
            # if provided parent, follow parent
            # else follow weapon to the left
            inherit = roots if not is_series else prev_w

            if isinstance(w, BaseWeapon):
                if not inherit:
                    ret.append(upgrade_class(self.data, score, w))
                for pw in inherit:
                    ret.append(upgrade_class(self.data, score, w, pw))
                prev_w = [w]
            elif isinstance(w, list):
                new_ret: list[upgrade_class] = self.generate_weapon_series(
                    upgrade_class, w, score, inherit, child_is_series
                )
                prev_w = []
                for u in new_ret:
                    if u.args[0] not in prev_w:
                        prev_w.append(u.args[0])
                ret.extend(new_ret)
            else:
                raise ValueError(f"Unexpected value of type {type(w)} in weapon_series: {w}")
        return ret


    def update_status(self):
        if not self.get_all_child():
            self._generate_upgrades()

    def _generate_upgrades(self):
        available_upgrades: list[list[BaseUpgrade]] = [[i for i in u if i.is_available()] for u in self.upgrades ]
        if not any(u for u in available_upgrades):
            self.hide()
            return
        if isinstance(self.prev_upgrade, ChangeMainWeapon):
            self.prev_upgrade = self.upgrade_main_weapon
        elif isinstance(self.prev_upgrade, ChangeSubWeapon):
            self.prev_upgrade = self.upgrade_sub_weapon
        for u_list in available_upgrades:
            shuffle(u_list)
        self.current_upgrades = [i for u_list in available_upgrades for i in (u_list + [self.filler_upgrade])[:1]]
        if self.prev_upgrade.is_available() and not self.prev_upgrade is self.filler_upgrade:
            self.current_upgrades[self.prev_upgrade_idx] = self.prev_upgrade
        self.set_child(*[self.create_upgrade_button(upgrade) for upgrade in self.current_upgrades])
        self.show()


def main():
    pane = UpgradePane(GameData())
    weapon_series = pane.generate_weapon_series(
        ChangeMainWeapon,
        [
            MainWeaponEnum.missile,
            [
                MainWeaponEnum.swarm,
                MainWeaponEnum.torpedo,
                [[AdvancedWeaponsEnum.mini_spawner, [AdvancedWeaponsEnum.elite_spawner, AdvancedWeaponsEnum.rammer_spawner]]]
            ]
        ],
        200,
    )
    print(*weapon_series, sep="\n")

if __name__ == '__main__':
    main()


