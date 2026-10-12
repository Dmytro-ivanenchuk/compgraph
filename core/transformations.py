from core.matrix import Matrix3x3
from core.point import Point


class EuclideanTransforms:

    @staticmethod
    def shift(dx: float, dy: float) -> Matrix3x3:
        return Matrix3x3.translation(dx, dy)

    @staticmethod
    def rotate(px: float, py: float, angle_deg: float) -> Matrix3x3:
        return Matrix3x3.rotation_around_point(px, py, angle_deg)


class AffineTransforms:

    @staticmethod
    def point_symmetry(px: float, py: float) -> Matrix3x3:
        return Matrix3x3.point_symmetry(px, py)

    @staticmethod
    def scale(sx: float, sy: float) -> Matrix3x3:
        return Matrix3x3.scaling(sx, sy)

    @staticmethod
    def general(origin: Point, x_unit: Point, y_unit: Point) -> Matrix3x3:
        return Matrix3x3.affine_from_basis(origin, x_unit, y_unit)


class ProjectiveTransforms:

    @staticmethod
    def general(x_end: Point, y_end: Point, origin: Point,
                wx: float, wy: float, w0: float) -> Matrix3x3:
        return Matrix3x3.projective_from_points(x_end, y_end, origin, wx, wy, w0)
