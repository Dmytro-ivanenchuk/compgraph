import math

from core.point import Point


class Line:

    def __init__(self, p_start: Point, p_end: Point):
        self.p_start = p_start
        self.p_end = p_end

    def sample_points(self):
        return [
            self.p_start,
            self.p_end,
        ]


class Arc:

    def __init__(
        self,
        center: Point,
        radius: float,
        degree_from: float = 0.0,
        degree_to: float = 360.0,
        step_deg: float = 1.0,
    ):
        self.center = center
        self.radius = radius
        self.degree_from = degree_from
        self.degree_to = degree_to
        self.step_deg = step_deg

    def sample_points(self):
        points = []

        delta = self.degree_to - self.degree_from

        n_steps = max(
            1,
            int(
                round(
                    abs(delta) / self.step_deg
                )
            ),
        )

        actual_step = delta / n_steps

        for i in range(n_steps + 1):

            deg = (
                self.degree_from
                + i * actual_step
            )

            theta = math.radians(deg)

            x = (
                self.center.x
                + self.radius * math.cos(theta)
            )

            y = (
                self.center.y
                + self.radius * math.sin(theta)
            )

            points.append(
                Point(x, y)
            )

        return points


class Circle(Arc):

    def __init__(
        self,
        center: Point,
        radius: float,
        step_deg: float = 1.0,
    ):
        super().__init__(
            center,
            radius,
            0.0,
            360.0,
            step_deg,
        )


class EllipseArc:

    def __init__(
        self,
        center: Point,
        rx: float,
        ry: float,
        start_deg: float = 0.0,
        end_deg: float = 360.0,
        step_deg: float = 1.0,
    ):
        self.center = center
        self.rx = rx
        self.ry = ry
        self.start_deg = start_deg
        self.end_deg = end_deg
        self.step_deg = step_deg

    def sample_points(self):
        points = []

        delta = self.end_deg - self.start_deg

        n_steps = max(
            1,
            int(
                round(
                    abs(delta) / self.step_deg
                )
            ),
        )

        actual_step = delta / n_steps

        for i in range(n_steps + 1):

            deg = (
                self.start_deg
                + i * actual_step
            )

            theta = math.radians(deg)

            x = (
                self.center.x
                + self.rx * math.cos(theta)
            )

            y = (
                self.center.y
                + self.ry * math.sin(theta)
            )

            points.append(
                Point(x, y)
            )

        return points