import math

from core.point import Point
from scene.primitives import Line, Arc, Circle, EllipseArc


DEFAULT_PARAMS = {
    "half_top_width": 2.5,
    "top_y": 6.0,

    "half_shoulder_width": 5.0,
    "shoulder_y": -1.0,

    "bottom_y": -6.0,
    "middle_y": -4.5,

    "arc_radius": 2.5,

    "circle_radius": 1.5,
    "circle_y": 0.0,

    "ellipse_rx": 1.0,
    "ellipse_ry": 5.0,
}


class Model:
    def __init__(self, **params):
        self.params = dict(DEFAULT_PARAMS)
        self.params.update(params)

        # Середні та внутрішні точки не залежать
        # автоматично від ширини плечей.
        hsw = abs(self.params["half_shoulder_width"])
        self._middle_x = hsw * 0.60
        self._inner_x = hsw * 0.40

        self._lines = []
        self._arcs = []
        self._ellipses = []
        self._circle = None

        self.rebuild()

    def set_param(self, name: str, value: float):
        self.set_params(**{name: value})

    def set_params(self, **params):
        for name in params:
            if name not in self.params:
                raise KeyError(
                    f"Невідомий параметр моделі: {name}"
                )

        changed = set(params)

        for name, value in params.items():
            self.params[name] = float(value)

        if "ellipse_ry" in changed:
            self.params["ellipse_ry"] = max(
                0.05,
                abs(self.params["ellipse_ry"])
            )

            self.params["bottom_y"] = (
                self.params["shoulder_y"]
                - self.params["ellipse_ry"]
            )

        elif "bottom_y" in changed:
            ry = (
                self.params["shoulder_y"]
                - self.params["bottom_y"]
            )

            self.params["ellipse_ry"] = max(
                0.05,
                abs(ry)
            )

            self.params["bottom_y"] = (
                self.params["shoulder_y"]
                - self.params["ellipse_ry"]
            )

        elif "shoulder_y" in changed:
            self.params["bottom_y"] = (
                self.params["shoulder_y"]
                - self.params["ellipse_ry"]
            )

        self.rebuild()

    def reset_dimensions(self):
        self.params = dict(DEFAULT_PARAMS)

        hsw = abs(self.params["half_shoulder_width"])

        self._middle_x = hsw * 0.60
        self._inner_x = hsw * 0.40

        self.rebuild()

    def rebuild(self):
        p = self.params

        top_half = max(
            0.05,
            abs(p["half_top_width"])
        )

        top_y = p["top_y"]

        hsw = max(
            self._inner_x + 0.1,
            abs(p["half_shoulder_width"])
        )

        shoulder_y = p["shoulder_y"]

        middle_y = p["middle_y"]

        if middle_y <= p["bottom_y"]:
            middle_y = p["bottom_y"] + 0.05

        if middle_y >= shoulder_y:
            middle_y = shoulder_y - 0.05

        self.params["middle_y"] = middle_y

        ellipse_rx = max(
            0.05,
            abs(p["ellipse_rx"])
        )

        outer_x = hsw - ellipse_rx

        if outer_x <= self._inner_x:
            outer_x = self._inner_x + 0.05
            ellipse_rx = hsw - outer_x

        self.params["ellipse_rx"] = ellipse_rx

        ellipse_ry = max(
            0.05,
            abs(p["ellipse_ry"])
        )

        bottom_y = shoulder_y - ellipse_ry

        self.params["ellipse_ry"] = ellipse_ry
        self.params["bottom_y"] = bottom_y

        radius = max(
            0.05,
            abs(p["arc_radius"])
        )

        radius = min(
            radius,
            self._middle_x,
            abs(middle_y) * 0.95
        )

        self.params["arc_radius"] = radius


        top_left = Point(
            -top_half,
            top_y
        )

        top_right = Point(
            top_half,
            top_y
        )

        shoulder_left = Point(
            -hsw,
            shoulder_y
        )

        shoulder_right = Point(
            hsw,
            shoulder_y
        )

        bottom_outer_left = Point(
            -outer_x,
            bottom_y
        )

        bottom_outer_right = Point(
            outer_x,
            bottom_y
        )

        bottom_inner_left = Point(
            -self._inner_x,
            bottom_y
        )

        bottom_inner_right = Point(
            self._inner_x,
            bottom_y
        )

        middle_left = Point(
            -self._inner_x,
            middle_y
        )

        middle_right = Point(
            self._inner_x,
            middle_y
        )

        middle_outer_left = Point(
            -self._middle_x,
            middle_y
        )

        middle_outer_right = Point(
            self._middle_x,
            middle_y
        )

        arc_left = Point(
            -radius,
            0.0
        )

        arc_right = Point(
            radius,
            0.0
        )


        self._lines = [
            # Верх
            Line(
                top_left,
                top_right
            ),

            Line(
                shoulder_left,
                top_left
            ),

            Line(
                shoulder_right,
                top_right
            ),

            Line(
                bottom_outer_left,
                bottom_inner_left
            ),

            Line(
                bottom_outer_right,
                bottom_inner_right
            ),

            Line(
                bottom_inner_left,
                middle_left
            ),

            Line(
                bottom_inner_right,
                middle_right
            ),

            Line(
                middle_outer_left,
                middle_left
            ),

            Line(
                middle_outer_right,
                middle_right
            ),

            Line(
                middle_outer_left,
                arc_left
            ),

            Line(
                middle_outer_right,
                arc_right
            ),
        ]

        self._arcs = [
            Arc(
                Point(0.0, 0.0),
                radius,
                180.0,
                360.0
            )
        ]

        self._ellipses = [

            EllipseArc(
                Point(
                    -outer_x,
                    shoulder_y
                ),
                ellipse_rx,
                ellipse_ry,
                180.0,
                270.0
            ),

            EllipseArc(
                Point(
                    outer_x,
                    shoulder_y
                ),
                ellipse_rx,
                ellipse_ry,
                0.0,
                -90.0
            ),
        ]


        circle_r = max(
            0.05,
            abs(p["circle_radius"])
        )

        self.params["circle_radius"] = circle_r

        self._circle = Circle(
            Point(
                0.0,
                p["circle_y"]
            ),
            circle_r
        )


    def primitives(self):
        return (
            self._lines
            + self._arcs
            + self._ellipses
            + [self._circle]
        )

