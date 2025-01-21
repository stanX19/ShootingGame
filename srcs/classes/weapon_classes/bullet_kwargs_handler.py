import random
from typing import Any


def is_tuple_of_two_numbers(val):
    return isinstance(val, tuple) and len(val) == 2 and all(isinstance(i, (int, float)) for i in val)

class BulletKwargsHandler:
    def __init__(self, bullet_kwargs: dict[str, Any]):
        self._original_kwargs: dict[str, Any] = bullet_kwargs
        self._static_kwargs: dict[str, Any] = {}
        self._random_kwargs: dict[str, Any] = {}
        self._set_static_and_random_kwargs()

    def _set_static_and_random_kwargs(self):
        self._static_kwargs = {k: v for k, v in self._original_kwargs.items() if not is_tuple_of_two_numbers(v)}
        self._random_kwargs = {k: v for k, v in self._original_kwargs.items() if is_tuple_of_two_numbers(v)}

    def _get_generated_random_kwargs(self) -> dict[str, int | float]:
        return {key: random.uniform(*val) for key, val in self._random_kwargs.items()}

    def get_processed_kwargs(self) -> dict[str, Any]:
        return {**self._static_kwargs, **self._get_generated_random_kwargs()}

    def get_raw_kwargs(self):
        return self._original_kwargs.copy()

    def update_kwargs(self, **new_items: dict[str, Any]):
        self._original_kwargs.update(new_items)
        self._set_static_and_random_kwargs()

    def getattr(self, name: str, default: Any = None) -> Any:
        return self._original_kwargs.get(name, default)


