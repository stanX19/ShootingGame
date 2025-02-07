from random import shuffle

from srcs.classes.UI.button import Button
from srcs.classes.UI.pane import Pane
from srcs.classes.entity.unit import Unit
from srcs.classes.game_data import GameData
from srcs.classes.weapon_classes.weapons_enum import MainWeaponEnum, SubWeaponEnum
from srcs.constants import SCREEN_HEIGHT, SCREEN_WIDTH


class BaseUpgrade:
    def __init__(self, data: GameData, score: int, *args):
        self.data: GameData = data
        self.score: int = score
        self.args: list = list(args)

    def on_click(self):
        pass

    def get_description(self):
        return f"Score -{self.score}"


class HPUpgrade(BaseUpgrade):
    def get_description(self):
        return f"HP +{self.args[0]}"

    def on_click(self):
        self.data.player.max_hp += self.args[0]
        self.data.player.hp += self.args[0]


class SpeedUpgrade(BaseUpgrade):
    def get_description(self):
        return f"SPEED +{self.args[0]}"

    def on_click(self):
        self.data.player.speed += self.args[0]
        if isinstance(self.data.player, Unit):
            self.data.player.max_speed += self.args[0]

class RadUpgrade(BaseUpgrade):
    def get_description(self):
        return f"RAD +{self.args[0]}"

    def on_click(self):
        self.data.player.max_rad += self.args[0]
        self.data.player.rad += self.args[0]
        if isinstance(self.data.player, Unit):
            self.data.player.shield.max_rad = max(self.data.player.shield.max_rad, self.data.player.max_rad + 100)

class OverdriveCDUpgrade(BaseUpgrade):
    def get_description(self):
        return f"Overdrive +{self.args[0] * 100:.0f}%"

    def on_click(self):
        if isinstance(self.data.player, Unit):
            self.data.player.main_weapon.overdrive_percentage += self.args[0]
            self.data.player.sub_weapon.overdrive_percentage += self.args[0]

class ChangeMainWeaponUpgrade(BaseUpgrade):
    def get_description(self):
        return f"MAIN WEAPON {self.args[0]}"

    def on_click(self):
        if isinstance(self.data.player, Unit):
            self.data.player.main_weapon.reinit_weapons(self.args)

class ChangeSubWeaponUpgrade(BaseUpgrade):
    def get_description(self):
        return f"SUB WEAPON {self.args[0]}"

    def on_click(self):
        if isinstance(self.data.player, Unit):
            self.data.player.sub_weapon.reinit_weapons(self.args)

class ShieldHpUpgrade(BaseUpgrade):
    def get_description(self):
        return f"SHIELD HP +{self.args[0]}"

    def on_click(self):
        if isinstance(self.data.player, Unit):
            self.data.player.shield.max_hp += self.args[0]


class UpgradePane(Pane):
    def __init__(self, data: GameData):
        super().__init__(300, SCREEN_HEIGHT - 200, SCREEN_WIDTH - 300, SCREEN_HEIGHT - 100)
        self.data = data
        self.hide()

        self.upgrades: list[BaseUpgrade] = [
            HPUpgrade(self.data, 50, 10),
            SpeedUpgrade(self.data, 50, 1),
            RadUpgrade(self.data, 50, 10),
            SpeedUpgrade(self.data, 300, 10),
            OverdriveCDUpgrade(self.data, 300, 0.1),
            RadUpgrade(self.data, 300, 100),
            ChangeMainWeaponUpgrade(self.data, 500, MainWeaponEnum.lazer),
            ChangeMainWeaponUpgrade(self.data, 500, MainWeaponEnum.lazer_super),
            ChangeMainWeaponUpgrade(self.data, 500, MainWeaponEnum.missile),
            ChangeMainWeaponUpgrade(self.data, 500, MainWeaponEnum.giant_canon),
            ChangeSubWeaponUpgrade(self.data, 5000, MainWeaponEnum.lazer),
            ChangeSubWeaponUpgrade(self.data, 5000, MainWeaponEnum.lazer_super),
            ChangeSubWeaponUpgrade(self.data, 5000, MainWeaponEnum.missile),
            ChangeSubWeaponUpgrade(self.data, 5000, MainWeaponEnum.giant_canon),
            OverdriveCDUpgrade(self.data, 10000, 1),
            HPUpgrade(self.data, 5000, 2000),
        ]

    def create_upgrade_button(self, upgrade: BaseUpgrade):
        def on_click():
            self.data.player.use_score(upgrade.score)
            upgrade.on_click()
            self.set_child()
        return Button(upgrade.get_description(), on_click)

    def update_status(self):
        if not self.get_all_child():
            self._generate_upgrades()

    def _generate_upgrades(self):
        available_upgrades = [i for i in self.upgrades if i.score <= self.data.player.score]
        if not available_upgrades:
            self.hide()
            return
        shuffle(available_upgrades)
        chosen_upgrades: list[BaseUpgrade] = available_upgrades[:4]
        self.set_child(*[self.create_upgrade_button(upgrade) for upgrade in chosen_upgrades])
        self.show()



