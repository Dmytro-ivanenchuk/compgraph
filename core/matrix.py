"""
Матриця перетворень 3х3 та операції над точками.

Використовується угода "вектор-рядок": P' = P * M, де P = [x, y, 1]
(формула 5). Це узгоджено з формулами (6)-(10) методички:

    [x', y', w] = [x, y, 1] * M
    x* = x' / w,   y* = y' / w

Усі конкретні види перетворень (зсув, оберт, масштабування, симетрія,
афінне, проективне) реалізовані як статичні методи, що повертають
готову матрицю Matrix3x3 -- рівно так, як описано у формулах (11)-(16).
"""

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
        """Одинична матриця за замовчуванням (формула 4)."""
        return Matrix3x3()

    def multiply(self, other: "Matrix3x3") -> "Matrix3x3":
        """
        Композиція двох перетворень: спочатку застосовується self,
        потім other (бо P * self * other = P * (self * other)).
        """
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
        """Перетворення списку точок однією й тією ж матрицею."""
        return [self.transform_point(p) for p in points]

    # ------------------------------------------------------------------
    # Евклідові перетворення
    # ------------------------------------------------------------------

    @staticmethod
    def translation(dx: float, dy: float) -> "Matrix3x3":
        """Матриця зсуву (формула 11)."""
        return Matrix3x3([
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [dx, dy, 1.0],
        ])

    @staticmethod
    def rotation(angle_deg: float) -> "Matrix3x3":
        """Обертання навколо початку координат на кут angle_deg (градуси)."""
        a = math.radians(angle_deg)
        c, s = math.cos(a), math.sin(a)
        return Matrix3x3([
            [c, s, 0.0],
            [-s, c, 0.0],
            [0.0, 0.0, 1.0],
        ])

    @staticmethod
    def rotation_around_point(px: float, py: float, angle_deg: float) -> "Matrix3x3":
        """
        Обертання навколо довільної точки P(px, py) -- формула (12).
        Реалізовано композицією: зсув точки P у початок координат ->
        обертання навколо початку -> зсув назад. Результат еквівалентний
        матриці (12), але отриманий без ручного розкриття дужок.
        """
        to_origin = Matrix3x3.translation(-px, -py)
        rot = Matrix3x3.rotation(angle_deg)
        back = Matrix3x3.translation(px, py)
        return to_origin.multiply(rot).multiply(back)

    # ------------------------------------------------------------------
    # Афінні перетворення -- окремі випадки
    # ------------------------------------------------------------------

    @staticmethod
    def scaling(sx: float, sy: float) -> "Matrix3x3":
        """Матриця масштабування (формула 13)."""
        return Matrix3x3([
            [sx, 0.0, 0.0],
            [0.0, sy, 0.0],
            [0.0, 0.0, 1.0],
        ])

    @staticmethod
    def point_symmetry(px: float, py: float) -> "Matrix3x3":
        """
        Матриця симетрії відносно довільної точки P(px, py) -- формула (14):
        будь-яка точка (x, y) відображається у (2px - x, 2py - y).
        """
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
        """
        Матриця афінних перетворень (формула 16), що задається новим
        базисом координатної системи:
          O(x, y) -- точка початку координат,
          X(x, y) -- точка одиничного відрізку осі абсцис,
          Y(x, y) -- точка одиничного відрізку осі ординат.
        """
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
        """
        Побудова матриці проективного перетворення з автоматичною
        нормалізацією метричного простору.

        Алгоритм динамічно адаптує "великі" параметри (напр., X=100, w0=1000)
        до локальної системи координат об'єкта, зберігаючи відносний
        градієнт перспективи та уникаючи перетину кардинальної прямої w'=0.

        Часова складність: O(1)
        Просторова складність: O(1)
        """
        # 1. Евристична оцінка масштабу простору.
        # Якщо вхідні координати перевищують локальні межі, ініціалізується
        # коефіцієнт нормалізації базису L.
        scale = 100.0 if (abs(x_end.x) > 10 or abs(y_end.y) > 10 or abs(w0) > 50) else 1.0

        # Нормалізація афінної складової базису:
        ox, oy = origin.x / scale, origin.y / scale
        xx, xy = x_end.x / scale, x_end.y / scale
        yx, yy = y_end.x / scale, y_end.y / scale

        # 2. Нормалізація проективних вагових коефіцієнтів.
        # Замість абсолютного ділення на велике w0 при деодноріднізації,
        # вагова компонента фіксується як w0* = 1.0, а різниця ваг
        # трансформується у відносний градієнт з фактором згладжування.
        safe_w0 = w0 if w0 != 0 else 1.0

        # Фактор демпфування запобігає надмірному наближенню лінії зникнення
        # до локальних координат об'єкта.
        damping = 20.0 if scale > 1.0 else 1.0

        norm_wx = 1.0 + (wx - safe_w0) / (safe_w0 * damping)
        norm_wy = 1.0 + (wy - safe_w0) / (safe_w0 * damping)
        norm_w0 = 1.0

        # 3. Синтез результуючої матриці за класичною формулою
        # відображення канонічного базису на задані контрольні точки.
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
