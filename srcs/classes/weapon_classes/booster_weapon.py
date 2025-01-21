from srcs.classes.weapon_classes.general_weapon import GeneralWeapon


class BoosterWeapon(GeneralWeapon):
    def _start_overdrive(self):
        super()._start_overdrive()
        self._recoil *= 5

    def _end_overdrive(self):
        super()._end_overdrive()
        self._recoil /= 5