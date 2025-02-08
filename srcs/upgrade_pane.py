from random import shuffle, random, randint

from srcs.classes.UI.button import Button
from srcs.classes.UI.pane import Pane, VPane
from srcs.classes.entity.unit import Unit
from srcs.classes.game_data import GameData
from srcs.classes.weapon_classes.weapons_enum import MainWeaponEnum, SubWeaponEnum
from srcs.constants import SCREEN_HEIGHT, SCREEN_WIDTH
from srcs.unit_classes.advanced_weapons import AdvancedWeaponsEnum


class BaseUpgrade:
    def __init__(self, data: GameData, score: int, *args):
        self.data: GameData = data
        self.score: int = score
        self.args: list = list(args)

    def on_click(self):
        pass

    def get_description(self):
        return f"Score -{self.score}"

    def is_available(self):
        return self.score <= self.data.player.score


class UpgradeHP(BaseUpgrade):
    def get_description(self):
        return f"HP {self.args[0]:+}"

    def on_click(self):
        self.data.player.max_hp += self.args[0]
        self.data.player.hp += self.args[0]


class UpgradeSpeed(BaseUpgrade):
    def get_description(self):
        return f"SPEED {self.args[0]:+}"

    def on_click(self):
        self.data.player.speed += self.args[0]
        if isinstance(self.data.player, Unit):
            self.data.player.max_speed += self.args[0]

class UpgradeRad(BaseUpgrade):
    def get_description(self):
        return f"RAD {self.args[0]:+}"

    def on_click(self):
        self.data.player.max_rad += self.args[0]
        self.data.player.rad += self.args[0]
        if isinstance(self.data.player, Unit):
            self.data.player.shield.max_rad = max(self.data.player.shield.max_rad, self.data.player.max_rad + 100)

class UpgradeOverdriveCD(BaseUpgrade):
    def get_description(self):
        return f"Overdrive {self.args[0] * 100:+.0f}%"

    def on_click(self):
        if isinstance(self.data.player, Unit):
            self.data.player.main_weapon.overdrive_percentage += self.args[0]
            self.data.player.sub_weapon.overdrive_percentage += self.args[0]

class ChangeMainWeapon(BaseUpgrade):
    def get_description(self):
        return f"MAIN WEAPON {self.args[0]}"

    def on_click(self):
        if isinstance(self.data.player, Unit):
            self.data.player.main_weapon.reinit_weapons(self.args)

    def is_available(self):
        if (isinstance(self.data.player, Unit)
                and self.data.player.main_weapon.weapon != self.args[0]):
            return super().is_available()
        return False

class ChangeSubWeapon(BaseUpgrade):
    def get_description(self):
        return f"SUB WEAPON {self.args[0]}"

    def on_click(self):
        if isinstance(self.data.player, Unit):
            self.data.player.sub_weapon.reinit_weapons(self.args)

    def is_available(self):
        if (isinstance(self.data.player, Unit)
                and self.data.player.sub_weapon.weapon != self.args[0]):
            return super().is_available()
        return False

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

class UpgradeShieldHp(BaseUpgrade):
    def get_description(self):
        return f"SHIELD HP {self.args[0]:+}"

    def on_click(self):
        if isinstance(self.data.player, Unit):
            self.data.player.shield.hp += self.args[0]
            self.data.player.shield.max_hp += self.args[0]

class UpgradeShieldRad(BaseUpgrade):
    def get_description(self):
        return f"SHIELD RAD {self.args[0]:+}"

    def on_click(self):
        if isinstance(self.data.player, Unit):
            self.data.player.shield.max_rad += self.args[0]
            self.data.player.shield.max_hp = max(1.0, self.data.player.shield.max_hp)

class UpgradePane(VPane):
    def __init__(self, data: GameData):
        super().__init__(5, SCREEN_HEIGHT // 2 + 200, 405, SCREEN_HEIGHT - 20)
        self.data = data
        self.hide()

        self.upgrades: list[BaseUpgrade] = [
            UpgradeHP(self.data, 50, 10),
            UpgradeSpeed(self.data, 50, 1),
            UpgradeRad(self.data, 50, 10),
            UpgradeShieldHp(self.data, 50, 10),
            UpgradeShieldRad(self.data, 50, 100),
            UpgradeMainWeapon(self.data, 100, 1),
            UpgradeSubWeapon(self.data, 100, 1),
            UpgradeMainWeapon(self.data, 250, 3),
            UpgradeSubWeapon(self.data, 250, 3),
            UpgradeSpeed(self.data, 300, 10),
            UpgradeOverdriveCD(self.data, 300, 0.1),
            UpgradeRad(self.data, 300, 100),
            ChangeMainWeapon(self.data, 200, MainWeaponEnum.shotgun),
            ChangeMainWeapon(self.data, 200, MainWeaponEnum.lazer_mini),
            ChangeMainWeapon(self.data, 500, MainWeaponEnum.lazer),
            ChangeMainWeapon(self.data, 1000, MainWeaponEnum.lazer_super),
            ChangeMainWeapon(self.data, 1000, MainWeaponEnum.giant_canon),
            ChangeSubWeapon(self.data, 200, MainWeaponEnum.dancer),
            ChangeSubWeapon(self.data, 200, MainWeaponEnum.missile),
            ChangeSubWeapon(self.data, 500, MainWeaponEnum.swarm),
            ChangeSubWeapon(self.data, 200, MainWeaponEnum.flash),
            ChangeSubWeapon(self.data, 500, MainWeaponEnum.warp),
            ChangeSubWeapon(self.data, 1000, AdvancedWeaponsEnum.mini_spawner),
            ChangeSubWeapon(self.data, 3000, AdvancedWeaponsEnum.elite_spawner),
            ChangeSubWeapon(self.data, 5000, AdvancedWeaponsEnum.rammer_spawner),
            UpgradeHP(self.data, 5000, 2000),
            UpgradeMainWeapon(self.data, 5000, 100),
            UpgradeOverdriveCD(self.data, 10000, 1.0),
        ]
        self.current_upgrades: list[BaseUpgrade] = []
        self.prev_upgrade_idx: int = 0
        self.prev_upgrade: BaseUpgrade = self.upgrades[0]

    def create_upgrade_button(self, upgrade: BaseUpgrade):
        def on_click():
            self.data.player.use_score(upgrade.score)
            upgrade.on_click()
            self.set_child()
            self.prev_upgrade = upgrade
            self.prev_upgrade_idx = self.current_upgrades.index(upgrade)
        return Button(upgrade.get_description(), on_click)

    def update_status(self):
        if not self.get_all_child():
            self._generate_upgrades()

    def _generate_upgrades(self):
        self.current_upgrades = [i for i in self.upgrades if i.is_available()]
        if not self.current_upgrades:
            self.hide()
            return
        shuffle(self.current_upgrades)
        if self.prev_upgrade in self.current_upgrades:
            self.current_upgrades.remove(self.prev_upgrade)
        if self.prev_upgrade.is_available():
            self.current_upgrades.insert(self.prev_upgrade_idx, self.prev_upgrade)
        self.current_upgrades = self.current_upgrades[:4]
        self.set_child(*[self.create_upgrade_button(upgrade) for upgrade in self.current_upgrades])
        self.show()



