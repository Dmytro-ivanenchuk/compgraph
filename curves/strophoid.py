"""
Строфоїда (права) -- варіант 5.

Декартове рівняння:        y^2 = x^2 (a + x) / (a - x)
Полярне рівняння:          r = -a cos(2 phi) / cos(phi),   -pi/2 < phi < pi/2
Параметричне (t = tg phi): x = a (t^2 - 1) / (t^2 + 1),
                           y = t * x

Тут phi -- полярний кут точки, тому одна й та сама змінна дає і полярне,
і параметричне задання. Крива неперервна на (-pi/2, pi/2), тож точки йдуть
"по порядку" і зайвих з'єднувальних ліній не виникає.

Особливості: вузол у початку координат (дотичні y = +-x, t = +-1), петля між
вузлом і вершиною (-a, 0), вертикальна асимптота x = a, точок перегину немає.
"""

import math

from core.point import Point
from curves.base import Curve


class Strophoid(Curve):
    LINEAR_IN_A = True        # обидві координати пропорційні a
    LOOP_PHI = 45.0           # петля: t in [-1, 1], тобто phi in [-45, 45]

    def equations(self):
        return ["y² = x²(a+x)/(a−x)",
                "x = a(t²−1)/(t²+1),  y = t·x,  t = tg φ"]

    def point_t(self, t):
        x = self.a * (t * t - 1.0) / (t * t + 1.0)
        return Point(x, t * x)

    def d1(self, t):
        d = t * t + 1.0
        return (4.0 * self.a * t / d ** 2,
                self.a * (t ** 4 + 4.0 * t * t - 1.0) / d ** 2)

    def d2(self, t):
        d = t * t + 1.0
        return (4.0 * self.a * (1.0 - 3.0 * t * t) / d ** 3,
                4.0 * self.a * t * (3.0 - t * t) / d ** 3)

    def phi_to_t(self, phi_deg):
        return math.tan(math.radians(phi_deg))

    def dt_dphi(self, t):
        return t * t + 1.0

    # --- особливості строфоїди -------------------------------------------
    def loop_range(self):
        return (-self.LOOP_PHI, self.LOOP_PHI)

    def vertical_asymptotes(self):
        return [self.a]                       # x = a

    def areas(self):
        a2 = self.a ** 2
        return [("Площа петлі", a2 * (2.0 - math.pi / 2.0)),
                ("Площа між кривою та асимптотою", a2 * (2.0 + math.pi / 2.0))]

    def notes(self):
        return ["Похилих асимптот немає"]
