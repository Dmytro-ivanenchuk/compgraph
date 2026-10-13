"""Текстовий звіт з розрахунків (без tkinter)."""

import math

from core.point import Point

SEP = "─" * 44


def fmt(v: float) -> str:
    return "∞" if not math.isfinite(v) or abs(v) > 1e6 else f"{v:.4f}"


def line_eq(p: Point, dx: float, dy: float) -> str:
    """Рівняння прямої через p з напрямним вектором (dx, dy)."""
    if abs(dx) < 1e-9:
        return f"x = {p.x:.3f}"
    k = dy / dx
    b = p.y - k * p.x
    return f"y = {k:.3f}·x {'+' if b >= 0 else '−'} {abs(b):.3f}"


class CalculationReport:
    def __init__(self, scene):
        self.scene = scene
        self._infl = None   # (ключ, список) -- перегини рахуємо лише коли треба

    def text(self) -> str:
        lines = []
        lines += self._header()
        lines += [SEP] + self._point_section()
        lines += [SEP] + self._global_section()
        lines += [SEP, "Матриця перетворення:", repr(self.scene.local)]
        return "\n".join(lines)

    # ------------------------------------------------------------------
    def _header(self):
        c = self.scene.curve
        return c.equations() + [f"a = {c.a:.3f}"]

    def _point_section(self):
        s, c = self.scene, self.scene.curve
        t = s.t
        p0 = c.point_t(t)
        ux, uy = c.tangent_dir(t)
        P = s.apply(p0)                                  # усе -- після перетворень
        Q = s.apply(Point(p0.x + ux, p0.y + uy))
        dx, dy = Q.x - P.x, Q.y - P.y
        return [
            f"φ = {s.phi:.1f}°,  t = {t:.4f}",
            f"P = ({P.x:.3f}; {P.y:.3f})",
            f"Дотична:  {line_eq(P, dx, dy)}",
            f"Нормаль:  {line_eq(P, -dy, dx)}",
            f"Радіус кривини R = {fmt(c.curvature_radius(t))}",
        ]

    def _global_section(self):
        s, c = self.scene, self.scene.curve
        lines = []

        for x in c.vertical_asymptotes():
            A = s.apply(Point(x, 0.0))
            B = s.apply(Point(x, 1.0))
            lines.append(f"Асимптота: {line_eq(A, B.x - A.x, B.y - A.y)}")
        if not c.vertical_asymptotes():
            lines.append("Асимптот немає")
        lines += c.notes()

        infl = self._inflections()
        lines.append("Точки перегину: " + ("немає (κ ≠ 0)" if not infl
                                           else ", ".join(f"t={v:.3f}" for v in infl)))

        loop = c.loop_length()
        if loop is not None:
            lines.append(f"Довжина петлі = {loop:.4f}")
        lines.append(f"Довжина дуги [{s.arc[0]:g}°; {s.arc[1]:g}°] = {c.arc_length(*s.arc):.4f}")
        for label, value in c.areas():
            lines.append(f"{label} = {value:.4f}")
        return lines

    def _inflections(self):
        c = self.scene.curve
        key = None if c.LINEAR_IN_A else c.a   # для подібних кривих перегини від a не залежать
        if self._infl is None or self._infl[0] != key:
            self._infl = (key, c.inflection_params())
        return self._infl[1]
