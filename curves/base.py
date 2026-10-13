"""
Абстрактна чудова крива.

Крива задана параметрично (x(t), y(t)) з одним статичним параметром a, а
параметр t пов'язаний з кутом phi (у градусах), який використовується для
вибору точки та меж побудови.

Конкретна крива (наслідник) визначає лише рівняння та похідні. Уся загальна
поведінка -- вибірка точок, дотична, кривина, довжина дуги, перегини --
реалізована тут і працює для будь-якої кривої. Інтерфейс, що залежить від
особливостей конкретної кривої (петля, асимптоти, площі), має типові
порожні реалізації: наслідник перевизначає лише те, що в нього є.
"""

import math
from abc import ABC, abstractmethod

from core.point import Point
from curves.numeric import simpson


class Curve(ABC):
    LINEAR_IN_A = False        # True, якщо P(a) = a * P(1): дозволяє кешувати точки
    A_RANGE = (0.2, 10.0)      # допустимі значення параметра a
    PHI_MAX = 89.9             # межа phi (градуси) при побудові

    def __init__(self, a: float = 1.0):
        self.a = a

    # ------------------------------------------------------------------
    # Те, що має визначити конкретна крива
    # ------------------------------------------------------------------
    @abstractmethod
    def equations(self):
        """Рядки з рівняннями кривої для відображення."""

    @abstractmethod
    def point_t(self, t: float) -> Point:
        """Точка кривої за параметром t."""

    @abstractmethod
    def d1(self, t: float):
        """(x'(t), y'(t))."""

    @abstractmethod
    def d2(self, t: float):
        """(x''(t), y''(t))."""

    @abstractmethod
    def phi_to_t(self, phi_deg: float) -> float:
        """Зв'язок кута phi (градуси) з параметром t."""

    @abstractmethod
    def dt_dphi(self, t: float) -> float:
        """dt/dphi (phi у радіанах) -- для інтегрування по куту."""

    # ------------------------------------------------------------------
    # Необов'язкові особливості кривої (за замовчуванням їх немає)
    # ------------------------------------------------------------------
    def loop_range(self):
        """(phi1, phi2) замкненої петлі або None."""
        return None

    def vertical_asymptotes(self):
        """Список x вертикальних асимптот."""
        return []

    def areas(self):
        """Список (підпис, значення) площ."""
        return []

    def notes(self):
        """Додаткові текстові зауваження до розрахунків."""
        return []

    # ------------------------------------------------------------------
    # Загальна поведінка
    # ------------------------------------------------------------------
    def unit(self) -> "Curve":
        """Така сама крива з a = 1."""
        return type(self)(1.0)

    def point(self, phi_deg: float) -> Point:
        return self.point_t(self.phi_to_t(phi_deg))

    def sample(self, phi1=None, phi2=None, step_deg: float = 0.1):
        """Точки кривої для phi in [phi1, phi2] (градуси) з кроком step_deg."""
        phi1 = -self.PHI_MAX if phi1 is None else phi1
        phi2 = self.PHI_MAX if phi2 is None else phi2
        n = max(1, int(round(abs(phi2 - phi1) / step_deg)))
        return [self.point(phi1 + (phi2 - phi1) * i / n) for i in range(n + 1)]

    def tangent_dir(self, t: float):
        """Одиничний вектор дотичної в напрямку зростання t."""
        x1, y1 = self.d1(t)
        n = math.hypot(x1, y1)
        return x1 / n, y1 / n

    def curvature_num(self, t: float) -> float:
        """x'y'' - y'x'' (знак визначає напрям кривини)."""
        x1, y1 = self.d1(t)
        x2, y2 = self.d2(t)
        return x1 * y2 - y1 * x2

    def curvature_radius(self, t: float) -> float:
        x1, y1 = self.d1(t)
        num = abs(self.curvature_num(t))
        if num < 1e-12:
            return math.inf
        return (x1 * x1 + y1 * y1) ** 1.5 / num

    def curvature_center(self, t: float) -> Point:
        p = self.point_t(t)
        ux, uy = self.tangent_dir(t)
        r = self.curvature_radius(t)
        sign = 1.0 if self.curvature_num(t) >= 0 else -1.0
        return Point(p.x - sign * uy * r, p.y + sign * ux * r)

    def inflection_params(self, n: int = 4000):
        """Значення t, де кривина змінює знак (чисельний пошук за phi)."""
        result = []
        prev = None
        for i in range(n + 1):
            t = self.phi_to_t(-89.5 + 179.0 * i / n)
            v = self.curvature_num(t)
            if prev is not None and prev * v < 0:
                result.append(t)
            prev = v
        return result

    def arc_length(self, phi1_deg: float, phi2_deg: float, n: int = 2000) -> float:
        """
        L = integral sqrt(x'^2 + y'^2) dt. Інтегруємо по phi (dt = dt/dphi dphi),
        так підінтегральна функція гладка.
        """
        def g(phi):
            t = self.phi_to_t(math.degrees(phi))
            x1, y1 = self.d1(t)
            return math.hypot(x1, y1) * self.dt_dphi(t)

        lo, hi = sorted((math.radians(phi1_deg), math.radians(phi2_deg)))
        return simpson(g, lo, hi, n)

    def loop_length(self):
        rng = self.loop_range()
        return None if rng is None else self.arc_length(*rng)
