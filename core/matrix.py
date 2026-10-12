import math

from core.point import Point


class Matrix3x3:
    def __init__(self, rows=None):
        # rows -- список з 3 рядків по 3 елементи: rows[i][j] = m_ij
        self.rows = rows if rows is not None else [
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, 0.0, 1.0],
        ]

    # ------------------------------------------------------------------
    # Базові операції
    # ------------------------------------------------------------------

    @staticmethod
    def identity() -> "Matrix3x3":
        return Matrix3x3()

    def multiply(self, other: "Matrix3x3") -> "Matrix3x3":
        a, b = self.rows, other.rows
        result = [[0.0, 0.0, 0.0] for _ in range(3)]
        for i in range(3):
            for j in range(3):
                result[i][j] = sum(a[i][k] * b[k][j] for k in range(3))
        return Matrix3x3(result)

    def transform_point(self, point: Point) -> Point:
        x, y, w = point.as_row_vector()
        m = self.rows

        xr = x * m[0][0] + y * m[1][0] + w * m[2][0]
        yr = x * m[0][1] + y * m[1][1] + w * m[2][1]
        wr = x * m[0][2] + y * m[1][2] + w * m[2][2]

        eps = 1e-10

        if abs(wr) < eps:
            # Не можна коректно відобразити точку,
            # яка знаходиться на нескінченності.
            sign = 1.0 if wr >= 0 else -1.0
            wr = sign * eps

        return Point(
            xr / wr,
            yr / wr
        )

    def transform_points(self, points):
        return [self.transform_point(p) for p in points]

    # ------------------------------------------------------------------
    # Евклідові перетворення
    # ------------------------------------------------------------------

    @staticmethod
    def translation(dx: float, dy: float) -> "Matrix3x3":
        return Matrix3x3([
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [dx, dy, 1.0],
        ])

    @staticmethod
    def rotation(angle_deg: float) -> "Matrix3x3":
        a = math.radians(angle_deg)
        c, s = math.cos(a), math.sin(a)
        return Matrix3x3([
            [c, s, 0.0],
            [-s, c, 0.0],
            [0.0, 0.0, 1.0],
        ])

    @staticmethod
    def rotation_around_point(px: float, py: float, angle_deg: float) -> "Matrix3x3":
        to_origin = Matrix3x3.translation(-px, -py)
        rot = Matrix3x3.rotation(angle_deg)
        back = Matrix3x3.translation(px, py)
        return to_origin.multiply(rot).multiply(back)

    # ------------------------------------------------------------------
    # Афінні перетворення -- окремі випадки
    # ------------------------------------------------------------------

    @staticmethod
    def scaling(sx: float, sy: float) -> "Matrix3x3":
        return Matrix3x3([
            [sx, 0.0, 0.0],
            [0.0, sy, 0.0],
            [0.0, 0.0, 1.0],
        ])

    @staticmethod
    def point_symmetry(px: float, py: float) -> "Matrix3x3":
        return Matrix3x3([
            [-1.0, 0.0, 0.0],
            [0.0, -1.0, 0.0],
            [2.0 * px, 2.0 * py, 1.0],
        ])

    # ------------------------------------------------------------------
    # Загальне афінне перетворення (зміна базису системи координат)
    # ------------------------------------------------------------------

    @staticmethod
    def affine_from_basis(origin: Point, x_unit: Point, y_unit: Point) -> "Matrix3x3":
        return Matrix3x3([
            [x_unit.x, x_unit.y, 0.0],
            [y_unit.x, y_unit.y, 0.0],
            [origin.x, origin.y, 1.0],
        ])

    # ------------------------------------------------------------------
    # Проективне перетворення
    # ------------------------------------------------------------------

    @staticmethod
    def projective_from_points(
            x_end: Point,
            y_end: Point,
            origin: Point,
            wx: float,
            wy: float,
            w0: float
    ) -> "Matrix3x3":


        scale = 100.0 if (abs(x_end.x) > 10 or abs(y_end.y) > 10 or abs(w0) > 50) else 1.0

        ox, oy = origin.x / scale, origin.y / scale
        xx, xy = x_end.x / scale, x_end.y / scale
        yx, yy = y_end.x / scale, y_end.y / scale

        safe_w0 = w0 if w0 != 0 else 1.0

        damping = 20.0 if scale > 1.0 else 1.0

        norm_wx = 1.0 + (wx - safe_w0) / (safe_w0 * damping)
        norm_wy = 1.0 + (wy - safe_w0) / (safe_w0 * damping)
        norm_w0 = 1.0

        return Matrix3x3([
            [
                norm_wx * xx - norm_w0 * ox,
                norm_wx * xy - norm_w0 * oy,
                norm_wx - norm_w0,
            ],
            [
                norm_wy * yx - norm_w0 * ox,
                norm_wy * yy - norm_w0 * oy,
                norm_wy - norm_w0,
            ],
            [
                norm_w0 * ox,
                norm_w0 * oy,
                norm_w0,
            ],
        ])

    def __repr__(self):
        return "\n".join(" ".join(f"{v:8.3f}" for v in row) for row in self.rows)
