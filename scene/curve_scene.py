"""
Сцена: крива + стан користувача (обрана точка, дуга, центр C) + матриця
евклідових перетворень. Нічого не знає про tkinter та малювання.

Усі методи geometry повертають точки в координатах кривої (до перетворення);
малювання множить їх на  local * view  -- так само, як у лабораторній №1:
усі об'єкти (крива і прямі) проходять через одну матрицю.
"""

import math

from core.matrix import Matrix3x3
from core.point import Point
from curves.base import Curve
from curves.sampler import CurveSampler


class CurveScene:
    BIG = 1e5   # "нескінченна" півдовжина асимптоти; відсікається при малюванні

    def __init__(self, curve: Curve):
        self.curve = curve
        self.sampler = CurveSampler(curve)
        self.local = Matrix3x3.identity()
        self.phi = 60.0                  # обрана точка кривої, градуси
        self.arc = (-60.0, 60.0)         # дуга для розрахунку довжини, градуси
        self.center = (0.0, 0.0)         # центр C обертання

    # ------------------------------------------------------------------
    # Стан
    # ------------------------------------------------------------------
    def set_a(self, a: float):
        self.curve.a = a

    def set_phi(self, phi: float):
        self.phi = phi

    def set_arc(self, phi1: float, phi2: float):
        lim = self.curve.PHI_MAX
        self.arc = (max(-lim, min(lim, phi1)), max(-lim, min(lim, phi2)))

    def set_center(self, x: float, y: float):
        self.center = (x, y)

    # ------------------------------------------------------------------
    # Евклідові перетворення
    # ------------------------------------------------------------------
    def shift(self, dx: float, dy: float):
        self.local = self.local.multiply(Matrix3x3.translation(dx, dy))

    def rotate(self, px: float, py: float, angle_deg: float):
        self.local = self.local.multiply(Matrix3x3.rotation_around_point(px, py, angle_deg))

    def reset_transform(self):
        self.local = Matrix3x3.identity()

    def apply(self, p: Point) -> Point:
        """Точка кривої -> точка на сцені (після перетворень)."""
        return self.local.transform_point(p)

    # ------------------------------------------------------------------
    # Вибірки точок кривої: (точки, множник), див. CurveSampler
    # ------------------------------------------------------------------
    def curve_samples(self):
        return self.sampler.sample(step_deg=0.2)

    def loop_samples(self):
        rng = self.curve.loop_range()
        return None if rng is None else self.sampler.sample(rng[0], rng[1], 0.5)

    def arc_samples(self):
        return self.sampler.sample(self.arc[0], self.arc[1], 0.2)

    # ------------------------------------------------------------------
    # Геометрія обраної точки
    # ------------------------------------------------------------------
    @property
    def t(self) -> float:
        return self.curve.phi_to_t(self.phi)

    def selected_point(self) -> Point:
        return self.curve.point_t(self.t)

    def tangent_points(self, half_len: float):
        p = self.selected_point()
        ux, uy = self.curve.tangent_dir(self.t)
        return [Point(p.x - ux * half_len, p.y - uy * half_len),
                Point(p.x + ux * half_len, p.y + uy * half_len)]

    def normal_points(self, half_len: float):
        p = self.selected_point()
        ux, uy = self.curve.tangent_dir(self.t)
        return [Point(p.x + uy * half_len, p.y - ux * half_len),
                Point(p.x - uy * half_len, p.y + ux * half_len)]

    def asymptote_lines(self):
        return [[Point(x, -self.BIG), Point(x, self.BIG)]
                for x in self.curve.vertical_asymptotes()]

    def curvature_circle_points(self, n: int = 180):
        r = self.curve.curvature_radius(self.t)
        if not math.isfinite(r) or r > 1e5:
            return []
        c = self.curve.curvature_center(self.t)
        return [Point(c.x + r * math.cos(2 * math.pi * i / n),
                      c.y + r * math.sin(2 * math.pi * i / n)) for i in range(n + 1)]
