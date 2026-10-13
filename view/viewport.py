"""Вікно перегляду: зум, панорама та перехід між світовими й екранними координатами."""

from core.matrix import Matrix3x3


class Viewport:
    MIN_ZOOM = 2.0
    MAX_ZOOM = 500.0

    def __init__(self):
        self.zoom = 30.0      # пікселів на одиницю
        self.ox = 0.0         # піксельна позиція початку координат
        self.oy = 0.0
        self.width = 0
        self.height = 0

    def resize(self, width: int, height: int):
        if self.width == 0:                       # перший показ
            self.width, self.height = width, height
            self.fit()
        else:                                     # центр лишається на місці
            self.ox += (width - self.width) / 2
            self.oy += (height - self.height) / 2
            self.width, self.height = width, height

    def fit(self, half_range: float = 8.0):
        """Видима приблизно область [-half_range; half_range] по меншій стороні."""
        self.zoom = max(5.0, min(self.width, self.height) / (2 * half_range))
        self.ox = self.width / 2
        self.oy = self.height / 2

    def zoom_at(self, factor: float, sx: float, sy: float):
        """Масштаб навколо екранної точки (sx, sy)."""
        new = max(self.MIN_ZOOM, min(self.MAX_ZOOM, self.zoom * factor))
        f = new / self.zoom
        self.ox = sx - (sx - self.ox) * f
        self.oy = sy - (sy - self.oy) * f
        self.zoom = new

    def to_world(self, sx: float, sy: float):
        return (sx - self.ox) / self.zoom, (self.oy - sy) / self.zoom

    def matrix(self) -> Matrix3x3:
        """Світ -> пікселі (вектор-рядок, як у лабораторній №1)."""
        s = self.zoom
        return Matrix3x3([[s, 0.0, 0.0], [0.0, -s, 0.0], [self.ox, self.oy, 1.0]])

    def key(self):
        """Змінюється, коли треба перемалювати сітку."""
        return (self.ox, self.oy, self.zoom, self.width, self.height)
