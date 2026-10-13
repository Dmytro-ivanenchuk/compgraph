"""Що показувати на сцені."""

from dataclasses import dataclass


@dataclass
class DisplayOptions:
    tangent: bool = True
    normal: bool = True
    asymptote: bool = True
    circle: bool = False
    loop: bool = True
    arc: bool = True


# (поле DisplayOptions, підпис прапорця в інтерфейсі)
OPTION_LABELS = (
    ("tangent", "Дотична"),
    ("normal", "Нормаль"),
    ("asymptote", "Асимптота"),
    ("circle", "Коло кривини"),
    ("loop", "Заливка петлі"),
    ("arc", "Підсвітити дугу"),
)
