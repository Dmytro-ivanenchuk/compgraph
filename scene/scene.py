from core.matrix import Matrix3x3
from core.point import Point
from core.transformations import EuclideanTransforms, AffineTransforms, ProjectiveTransforms
from scene.axes import Axes
from scene.model import Model


class Scene:
    def __init__(self):
        self.axes = Axes()
        self.model = Model()
        self.model_local_transform = Matrix3x3.identity()
        self.world_transform = Matrix3x3.identity()

    def shift_model(self, dx: float, dy: float):
        m = EuclideanTransforms.shift(dx, dy)
        self.model_local_transform = self.model_local_transform.multiply(m)

    def rotate_model(self, px: float, py: float, angle_deg: float):
        m = EuclideanTransforms.rotate(px, py, angle_deg)
        self.model_local_transform = self.model_local_transform.multiply(m)

    # ------------------------------------------------------------
    # Афінні перетворення (окремі випадки) -- діють тільки на деталь
    # ------------------------------------------------------------

    def symmetry_model(self, px: float, py: float):
        m = AffineTransforms.point_symmetry(px, py)
        self.model_local_transform = self.model_local_transform.multiply(m)

    def scale_model(self, sx: float, sy: float):
        m = AffineTransforms.scale(sx, sy)
        self.model_local_transform = self.model_local_transform.multiply(m)

    # ------------------------------------------------------------
    # Загальне афінне і проективне -- діють на деталь + осі
    # ------------------------------------------------------------

    def set_affine_world(self, origin: Point, x_unit: Point, y_unit: Point):
        self.world_transform = AffineTransforms.general(origin, x_unit, y_unit)

    def set_projective_world(self, x_end: Point, y_end: Point, origin: Point,
                              wx: float, wy: float, w0: float):
        self.world_transform = ProjectiveTransforms.general(x_end, y_end, origin, wx, wy, w0)


    def reset_model_transform(self):
        self.model_local_transform = Matrix3x3.identity()

    def reset_world_transform(self):
        self.world_transform = Matrix3x3.identity()

    def reset_all(self):
        self.reset_model_transform()
        self.reset_world_transform()

    # ------------------------------------------------------------
    # Геометрія для відображення (вже в екранних координатах)
    # ------------------------------------------------------------

    def get_axis_polylines(self, view_transform: Matrix3x3):
        full = self.world_transform.multiply(view_transform)
        return [full.transform_points(line.sample_points()) for line in self.axes.axis_lines()]

    def get_grid_polylines(self, view_transform: Matrix3x3):
        full = self.world_transform.multiply(view_transform)
        return [full.transform_points(line.sample_points()) for line in self.axes.grid_lines()]

    def get_model_polylines(self, view_transform: Matrix3x3):
        full = self.model_local_transform.multiply(self.world_transform).multiply(view_transform)
        return [full.transform_points(prim.sample_points()) for prim in self.model.primitives()]
