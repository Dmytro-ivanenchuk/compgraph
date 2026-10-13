"""
Точка сцени.

Згідно методички, вектор довільної точки об'єкта має вигляд P = [x, y, 1]
(формула 5). Клас Point зберігає лише (x, y), а метод as_row_vector()
повертає повний вектор-рядок для множення на матрицю перетворень.
"""


class Point:
    __slots__ = ("x", "y")

    def __init__(self, x: float = 0.0, y: float = 0.0):
        self.x = float(x)
        self.y = float(y)

    def as_row_vector(self):
        """Повертає точку у вигляді [x, y, 1] -- формула (5)."""
        return (self.x, self.y, 1.0)

    def copy(self) -> "Point":
        return Point(self.x, self.y)

    def __iter__(self):
        yield self.x
        yield self.y

    def __repr__(self):
        return f"Point({self.x:.3f}, {self.y:.3f})"
