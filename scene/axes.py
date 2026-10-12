from core.point import Point
from scene.primitives import Line


class Axes:
    def __init__(self, grid_num: int = 20):
        self.p0 = Point(0.0, 0.0)
        self.p1 = Point(1.0, 0.0)
        self.p2 = Point(0.0, 1.0)
        self.grid_num = grid_num

    def axis_lines(self):
        n = self.grid_num

        x_pos = Point(
            self.p1.x * n,
            self.p1.y * n
        )
        x_neg = Point(
            -self.p1.x * n,
            -self.p1.y * n
        )

        y_pos = Point(
            self.p2.x * n,
            self.p2.y * n
        )
        y_neg = Point(
            -self.p2.x * n,
            -self.p2.y * n
        )

        return [
            Line(x_neg, x_pos),
            Line(y_neg, y_pos),
        ]

    def grid_lines(self):
        n = self.grid_num
        lines = []

        # Горизонтальні
        for k in range(-n, n + 1):
            if k == 0:
                continue

            start = Point(
                -n * self.p1.x + k * self.p2.x,
                -n * self.p1.y + k * self.p2.y
            )

            end = Point(
                n * self.p1.x + k * self.p2.x,
                n * self.p1.y + k * self.p2.y
            )

            lines.append(Line(start, end))

        # Вертикальні
        for k in range(-n, n + 1):
            if k == 0:
                continue

            start = Point(
                k * self.p1.x - n * self.p2.x,
                k * self.p1.y - n * self.p2.y
            )

            end = Point(
                k * self.p1.x + n * self.p2.x,
                k * self.p1.y + n * self.p2.y
            )

            lines.append(Line(start, end))

        return lines

    def axis_label_points(self):
        """
        Точки, біля яких малюємо підписи X та Y.
        Вони також проходять через world_transform.
        """
        n = self.grid_num

        x_label = Point(
            n + 0.5,
            0.0
        )

        y_label = Point(
            0.0,
            n + 0.5
        )

        return x_label, y_label