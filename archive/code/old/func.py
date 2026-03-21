from config import COLORS, NO_VISIBLE_STAGES


def color_to_str(color):
    """Конвертировать словарь цвета в строку формата #RRGGBB"""
    return "#{:02X}{:02X}{:02X}".format(
        int(color["red"] * 255), int(color["green"] * 255), int(color["blue"] * 255)
    )


def color_to_rgb(color):
    """Конвертировать строку hex в словарь rgb"""
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


def cell_to_indices(cell):
    """Конвертировать AB1000 в (27, 999)"""
    col = 0
    row = 0
    for i in cell:
        if i.isalpha():
            col = col * 26 + ord(i) - 64
        else:
            row = row * 10 + int(i)
    return col - 1, row - 1


def parse_range(range_):
    """Конвертировать диапазон A1:Z1000 в индексы (0, 0, 25, 1000)
    буквенные индексы могут быть из двех букв, например AA1:ZZ1000"""
    start, end = range_.split(":")
    start_col, start_row = cell_to_indices(start)
    end_col, end_row = cell_to_indices(end)
    return start_col, start_row, end_col, end_row


def filter_stages(stages, stop_world=None):
    """Отфильтровать этапы в который присутствуют такие слова"""
    if stop_world is None:
        stop_world = NO_VISIBLE_STAGES
    return [stage for stage in stages if not any([word in stage.lower() for word in stop_world])]


class RGBColor:
    """working with RGB color like ADADAD
    lihgter, darker, random, etc

    """

    def __init__(self, str_hex: str = "", rgb: tuple = ()):

        self.good_colors = [
            "e04141",
            "de6933",
            "f0b942",
            "41c483",
            "3fd1bb",
            "4b92c9",
            "626bba",
            "9f65cc",
            "cc3c84",
            "cf335f",
        ]
        self.good_colors = [
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

        if str_hex and rgb:
            raise ValueError("Only one parameter can be used")
        if str_hex:
            self.str_hex = str_hex.lstrip("#")
            self.rgb = self.get_rgb(self.str_hex)

        elif rgb:
            self.rgb = rgb
            self.str_hex = self.get_str_hex(self.rgb)

        else:
            self.str_hex = np.random.choice(self.good_colors).upper()
            self.rgb = self.get_rgb(self.str_hex)

    def get_rgb(self, str_hex):
        return tuple(int(str_hex[i : i + 2], 16) for i in (0, 2, 4))

    def get_str_hex(self, rgb):
        return "".join([f"{x:02x}" for x in rgb]).upper()

    def get_random_rgb(self):
        return tuple(np.random.randint(50, 200, 3))

    @property
    def lighter(self):
        rgb = [min(255, x + 10) for x in self.rgb]
        return RGBColor(str_hex=self.get_str_hex(rgb))

    @property
    def darker(self):
        rgb = [max(0, x - 10) for x in self.rgb]
        return RGBColor(str_hex=self.get_str_hex(rgb))

    @property
    def v(self):
        return self.str_hex

    @property
    def gray(self):
        gray = int(sum(self.rgb) / 3)
        return RGBColor(str_hex=self.get_str_hex((gray, gray, gray)))

    def __repr__(self):
        return self.str_hex

    def __str__(self):
        return self.str_hex

    def __add__(self, other):
        if isinstance(other, int):
            rgb = [min(255, x + other) for x in self.rgb]
            return RGBColor(str_hex=self.get_str_hex(rgb))

    def __sub__(self, other):
        if isinstance(other, int):
            rgb = [max(0, x - other) for x in self.rgb]
            return RGBColor(str_hex=self.get_str_hex(rgb))

    def __pow__(self, other):
        rgb = [int(((x / 255) ** other) * 255) for x in self.rgb]
        return RGBColor(str_hex=self.get_str_hex(rgb))


class GetColor:
    def __init__(self):
        self.good_colors = [
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
        self.good_colors = ["5fad56", "f2c14e", "f78154", "4d9078", "b4436c"]
        # self.good_colors = ['f3c259', 'fe9a62', 'f4787a', 'd36492', '9e5da2', '585aa1']
        self.n = len(self.good_colors)
        self.i = 0

    def __call__(self, color: str = None):
        if color:
            return RGBColor(COLORS[color])
        color = RGBColor(self.good_colors[self.i % self.n])
        self.i += 1
        return color
