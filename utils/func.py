from config import NO_VISIBLE_STAGES


def color_to_str(color):
    """ Конвертировать словарь цвета в строку формата #RRGGBB """
    return "#{:02X}{:02X}{:02X}".format(int(color['red'] * 255), int(color['green'] * 255),
                                        int(color['blue'] * 255))


def color_to_rgb(color):
    """ Конвертировать строку hex в словарь rgb"""
    if isinstance(color, dict):
        rgb = color
    elif isinstance(color, str):
        color = color.lstrip('#')
        hlen = len(color)
        rgb = {"red": int(color[0:hlen // 3], 16) / 255, "green": int(color[hlen // 3:2 * hlen // 3], 16) / 255,
               "blue": int(color[2 * hlen // 3:hlen], 16) / 255}
    elif isinstance(color, (list, tuple)):
        rgb = {"red": color[0], "green": color[1], "blue": color[2]}
    else:
        rgb = None
    return rgb


def cell_to_indices(cell):
    """ Конвертировать AB1000 в (27, 999) """
    col = 0
    row = 0
    for i in cell:
        if i.isalpha():
            col = col * 26 + ord(i) - 64
        else:
            row = row * 10 + int(i)
    return col - 1, row - 1


def parse_range(range_):
    """ Конвертировать диапазон A1:Z1000 в индексы (0, 0, 25, 1000)
    буквенные индексы могут быть из двех букв, например AA1:ZZ1000"""
    start, end = range_.split(':')
    start_col, start_row = cell_to_indices(start)
    end_col, end_row = cell_to_indices(end)
    return start_col, start_row, end_col, end_row


def filter_stages(stages, stop_world=None):
    """ Отфильтровать этапы в который присутствуют такие слова """
    if stop_world is None:
        stop_world = NO_VISIBLE_STAGES
    return [stage for stage in stages if not any([word in stage.lower() for word in stop_world])]
