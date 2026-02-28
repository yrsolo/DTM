"""Color and sheet-coordinate utility helpers."""

from __future__ import annotations

from typing import Iterable, Mapping

import numpy as np

from config import COLORS, NO_VISIBLE_STAGES


def color_to_str(color: Mapping[str, float]) -> str:
    """Convert RGB mapping in [0..1] range to `#RRGGBB` string."""
    return "#{:02X}{:02X}{:02X}".format(
        int(color["red"] * 255),
        int(color["green"] * 255),
        int(color["blue"] * 255),
    )


def color_to_rgb(color: Mapping[str, float] | str | tuple[float, float, float] | list[float]) -> dict[str, float]:
    """Convert color value into normalized RGB mapping."""
    if isinstance(color, dict):
        rgb = color
    elif isinstance(color, str):
        color = color.lstrip("#")
        hlen = len(color)
        rgb = {
            "red": int(color[0 : hlen // 3], 16) / 255,
            "green": int(color[hlen // 3 : 2 * hlen // 3], 16) / 255,
            "blue": int(color[2 * hlen // 3 : hlen], 16) / 255,
        }
    elif isinstance(color, (list, tuple)):
        rgb = {"red": color[0], "green": color[1], "blue": color[2]}
    else:
        rgb = color_to_rgb(str(color))
    return rgb


def cell_to_indices(cell: str) -> tuple[int, int]:
    """Convert A1-style cell to zero-based `(col, row)` indices."""
    col = 0
    row = 0
    for item in cell:
        if item.isalpha():
            col = col * 26 + ord(item.upper()) - 64
        else:
            row = row * 10 + int(item)
    return col - 1, row - 1


def parse_range(range_: str) -> tuple[int, int, int, int]:
    """Convert A1 range string into zero-based index tuple."""
    start, end = range_.split(":")
    start_col, start_row = cell_to_indices(start)
    end_col, end_row = cell_to_indices(end)
    return start_col, start_row, end_col, end_row


def filter_stages(stages: Iterable[str], stop_world: Iterable[str] | None = None) -> list[str]:
    """Filter out non-visible stage labels by forbidden keywords."""
    stop_words = list(stop_world) if stop_world is not None else list(NO_VISIBLE_STAGES)
    return [stage for stage in stages if not any(word in stage.lower() for word in stop_words)]


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
            return RGBColor(COLORS[color])
        item = RGBColor(self.good_colors[self.i % self.n])
        self.i += 1
        return item
