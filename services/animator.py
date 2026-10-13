"""Логіка анімації (без tkinter): параметр a ходить між мінімумом і максимумом."""

from services.errors import ValidationError


class Animator:
    PHI_LIMIT = 80.0     # точка дотику ходить у межах [-80, 80] градусів
    PHI_STEP = 1.0

    def __init__(self):
        self.lo = self.hi = self.step = 0.0
        self.move_point = False
        self._a_dir = 1
        self._phi_dir = 1

    def configure(self, scene, lo: float, hi: float, step: float, move_point: bool):
        a_min, a_max = scene.curve.A_RANGE
        if not (a_min <= lo < hi <= a_max and step > 0):
            raise ValidationError(
                f"Анімація: {a_min:g} ≤ a мін < a макс ≤ {a_max:g}, крок > 0")
        self.lo, self.hi, self.step, self.move_point = lo, hi, step, move_point
        scene.set_a(max(lo, min(hi, scene.curve.a)))

    def advance(self, scene):
        """Один кадр: змінює a (та, за потреби, точку дотику) у сцені."""
        a = scene.curve.a + self._a_dir * self.step
        if a >= self.hi:
            a, self._a_dir = self.hi, -1
        elif a <= self.lo:
            a, self._a_dir = self.lo, 1
        scene.set_a(a)

        if self.move_point:
            phi = scene.phi + self._phi_dir * self.PHI_STEP
            if phi >= self.PHI_LIMIT:
                phi, self._phi_dir = self.PHI_LIMIT, -1
            elif phi <= -self.PHI_LIMIT:
                phi, self._phi_dir = -self.PHI_LIMIT, 1
            scene.set_phi(phi)
