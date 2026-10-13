"""Малювання об'єктів сцени: крива, дотична, нормаль, асимптоти, коло кривини, легенда."""

from core.matrix import Matrix3x3
from core.point import Point
from view import theme
from view.drawing import draw_polyline

# (поле DisplayOptions, підпис у легенді, колір)
LEGEND = (
    ("tangent", "дотична", theme.TANGENT),
    ("normal", "нормаль", theme.NORMAL),
    ("asymptote", "асимптота", theme.ASYMPTOTE),
    ("circle", "коло кривини", theme.CIRCLE),
    ("arc", "дуга", theme.ARC),
)


class SceneRenderer:
    TAG = "dyn"
    TANGENT_HALF_PX = 200.0   # дотична й нормаль: 200 px в обидва боки

    def __init__(self, canvas):
        self.canvas = canvas
        self._rect = (0, 0, 0, 0)

    def draw(self, scene, vp, options):
        self.canvas.delete(self.TAG)
        w, h = vp.width, vp.height
        self._rect = (-60.0, -60.0, w + 60.0, h + 60.0)
        view = vp.matrix()
        full = scene.local.multiply(view)   # крива -> пікселі

        if options.loop:
            self._loop(scene, full)
        if options.asymptote:
            self._asymptotes(scene, full)
        self._curve(scene, full)
        if options.arc:
            self._arc(scene, full)
        if options.circle:
            self._poly(full.transform_points(scene.curvature_circle_points()),
                       fill=theme.CIRCLE, width=2, dash=(5, 3))
        half = self.TANGENT_HALF_PX / vp.zoom
        if options.tangent:
            self._poly(full.transform_points(scene.tangent_points(half)), fill=theme.TANGENT, width=2)
        if options.normal:
            self._poly(full.transform_points(scene.normal_points(half)), fill=theme.NORMAL, width=2)
        self._selected_point(scene, full)
        self._center(scene, view)
        self._legend(options)

    # ------------------------------------------------------------------
    @staticmethod
    def _scaled(full, scale):
        """Вносить множник a (для точок, обчислених при a = 1) у матрицю."""
        return full if scale == 1.0 else Matrix3x3.scaling(scale, scale).multiply(full)

    def _poly(self, pts, **kw):
        draw_polyline(self.canvas, pts, self._rect, tags=self.TAG, **kw)

    def _loop(self, scene, full):
        samples = scene.loop_samples()
        if samples is None:
            return
        pts, scale = samples
        coords = []
        for p in self._scaled(full, scale).transform_points(pts):
            coords += [p.x, p.y]
        if len(coords) >= 6:
            self.canvas.create_polygon(*coords, fill=theme.LOOP_FILL, outline="", tags=self.TAG)

    def _asymptotes(self, scene, full):
        for line in scene.asymptote_lines():
            self._poly(full.transform_points(line), fill=theme.ASYMPTOTE, width=2, dash=(7, 4))

    def _curve(self, scene, full):
        pts, scale = scene.curve_samples()
        self._poly(self._scaled(full, scale).transform_points(pts),
                   fill=theme.CURVE, width=2, capstyle="round", joinstyle="round")

    def _arc(self, scene, full):
        pts, scale = scene.arc_samples()
        self._poly(self._scaled(full, scale).transform_points(pts),
                   fill=theme.ARC, width=4, capstyle="round", joinstyle="round")

    def _selected_point(self, scene, full):
        p = full.transform_point(scene.selected_point())
        self.canvas.create_oval(p.x - 5, p.y - 5, p.x + 5, p.y + 5, fill=theme.POINT,
                                outline="white", tags=self.TAG)

    def _center(self, scene, view):
        q = view.transform_point(Point(*scene.center))
        c = self.canvas
        c.create_oval(q.x - 5, q.y - 5, q.x + 5, q.y + 5, outline=theme.CENTER, width=2, tags=self.TAG)
        c.create_line(q.x - 10, q.y, q.x + 10, q.y, fill=theme.CENTER, tags=self.TAG)
        c.create_line(q.x, q.y - 10, q.x, q.y + 10, fill=theme.CENTER, tags=self.TAG)
        c.create_text(q.x + 10, q.y - 10, text="C", fill=theme.CENTER,
                      font=("Arial", 10, "bold"), tags=self.TAG)

    def _legend(self, options):
        c = self.canvas
        entries = [("крива", theme.CURVE)] + [
            (label, color) for key, label, color in LEGEND if getattr(options, key)]
        y = 12
        for label, color in entries:
            c.create_line(12, y, 36, y, fill=color, width=3, tags=self.TAG)
            c.create_text(44, y, text=label, anchor="w", font=theme.FONT, fill=theme.TEXT, tags=self.TAG)
            y += 16
