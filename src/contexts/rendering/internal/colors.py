"""Rendering color helpers."""

from __future__ import annotations

from typing import Iterable

import numpy as np

from src.config.loader import load_config


_CFG = load_config()
_COLORS = dict(_CFG.mapping.palette)


class RGBColor:
    """RGB color utility with simple transform operators."""

    _DEFAULT_GOOD_COLORS = [
        "de6933",
        "f0b942",
        "42c246",
        "23bfbd",
        "41ccd1",
        "62a5d9",
        "717cd1",
        "7e5ae3",
        "9f65cc",
        "b55cac",
    ]

    def __init__(self, str_hex: str = "", rgb: tuple[int, int, int] = ()) -> None:
        self.good_colors = list(self._DEFAULT_GOOD_COLORS)

        if str_hex and rgb:
            raise ValueError("Only one parameter can be used")
        if str_hex:
            self.str_hex = str_hex.lstrip("#").upper()
            self.rgb = self.get_rgb(self.str_hex)
        elif rgb:
            self.rgb = rgb
            self.str_hex = self.get_str_hex(self.rgb)
        else:
            self.str_hex = str(np.random.choice(self.good_colors)).upper()
            self.rgb = self.get_rgb(self.str_hex)

    @staticmethod
    def get_rgb(str_hex: str) -> tuple[int, int, int]:
        return tuple(int(str_hex[i : i + 2], 16) for i in (0, 2, 4))

    @staticmethod
    def get_str_hex(rgb: tuple[int, int, int] | list[int]) -> str:
        return "".join(f"{x:02x}" for x in rgb).upper()

    @staticmethod
    def get_random_rgb() -> tuple[int, int, int]:
        return tuple(np.random.randint(50, 200, 3))

    @property
    def lighter(self) -> "RGBColor":
        rgb = [min(255, x + 10) for x in self.rgb]
        return RGBColor(str_hex=self.get_str_hex(rgb))

    @property
    def darker(self) -> "RGBColor":
        rgb = [max(0, x - 10) for x in self.rgb]
        return RGBColor(str_hex=self.get_str_hex(rgb))

    @property
    def v(self) -> str:
        return self.str_hex

    @property
    def gray(self) -> "RGBColor":
        gray = int(sum(self.rgb) / 3)
        return RGBColor(str_hex=self.get_str_hex((gray, gray, gray)))

    def __repr__(self) -> str:
        return self.str_hex

    def __str__(self) -> str:
        return self.str_hex

    def __add__(self, other: int) -> "RGBColor":
        if isinstance(other, int):
            rgb = [min(255, x + other) for x in self.rgb]
            return RGBColor(str_hex=self.get_str_hex(rgb))
        raise TypeError("RGBColor supports only integer addition.")

    def __sub__(self, other: int) -> "RGBColor":
        if isinstance(other, int):
            rgb = [max(0, x - other) for x in self.rgb]
            return RGBColor(str_hex=self.get_str_hex(rgb))
        raise TypeError("RGBColor supports only integer subtraction.")

    def __pow__(self, other: float) -> "RGBColor":
        rgb = [int(((x / 255) ** other) * 255) for x in self.rgb]
        return RGBColor(str_hex=self.get_str_hex(rgb))


class GetColor:
    """Color iterator and named color resolver."""

    def __init__(self) -> None:
        self.good_colors = ["5fad56", "f2c14e", "f78154", "4d9078", "b4436c"]
        self.n = len(self.good_colors)
        self.i = 0

    def __call__(self, color: str | None = None) -> RGBColor:
        if color:
            return RGBColor(_COLORS[color])
        item = RGBColor(self.good_colors[self.i % self.n])
        self.i += 1
        return item


def filter_hidden_stages(stages: Iterable[str], hidden_words: Iterable[str]) -> list[str]:
    """Filter out non-visible stage labels by forbidden keywords."""
    lowered_hidden = [str(word).lower() for word in hidden_words]
    return [
        stage
        for stage in stages
        if not any(word in str(stage).lower() for word in lowered_hidden)
    ]
