from curves.base import Curve


class CurveSampler:

    MAX_ENTRIES = 12

    def __init__(self, curve: Curve):
        self.curve = curve
        self._cache = {}

    def sample(self, phi1=None, phi2=None, step_deg=0.1):
        c = self.curve
        if c.LINEAR_IN_A:
            key = (phi1, phi2, step_deg)
            source, scale = c.unit(), c.a
        else:
            key = (c.a, phi1, phi2, step_deg)
            source, scale = c, 1.0
        if key not in self._cache:
            if len(self._cache) >= self.MAX_ENTRIES:
                self._cache.clear()
            self._cache[key] = source.sample(phi1, phi2, step_deg)
        return self._cache[key], scale
