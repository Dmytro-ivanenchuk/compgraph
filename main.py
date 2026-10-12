import math
import tkinter as tk
from tkinter import ttk

from core.matrix import Matrix3x3
from core.point import Point
from scene.scene import Scene

# ----------------------------------------------------------------------
# Оформлення
# ----------------------------------------------------------------------
BG = "#ffffff"
GRID_MINOR = "#ececec"
GRID_MAJOR = "#cfcfcf"
AXIS = "#202020"
MODEL = "#1565c0"
PIVOT = "#d32f2f"
TEXT = "#555555"
FONT = ("Arial", 9)
FONT_AXIS = ("Arial", 12, "bold")

NICE_STEPS = (1, 2, 5, 10, 20, 50, 100, 200, 500)

# (підпис, ім'я параметра моделі, мінімум, максимум)
DIMS = [
    ("Півширина верху", "half_top_width", 0.2, 8.0),
    ("Верх (y)", "top_y", 0.5, 12.0),
    ("Півширина плечей", "half_shoulder_width", 2.2, 10.0),
    ("Плечі (y)", "shoulder_y", -5.0, 5.0),
    ("Еліпс rx", "ellipse_rx", 0.2, 4.0),
    ("Еліпс ry", "ellipse_ry", 0.5, 10.0),
    ("Низ (y)", "bottom_y", -12.0, 0.0),
    ("Середня лінія (y)", "middle_y", -10.0, 0.0),
    ("Радіус дуги", "arc_radius", 0.3, 3.0),
    ("Радіус кола", "circle_radius", 0.2, 4.0),
    ("Центр кола (y)", "circle_y", -5.0, 5.0),
]


# ----------------------------------------------------------------------
# Допоміжні функції
# ----------------------------------------------------------------------
def finite(*values):
    return all(math.isfinite(v) for v in values)


def clip_segment(x0, y0, x1, y1, xmin, ymin, xmax, ymax):
    """Відсікання відрізка прямокутником (Ліанг-Барські). None -- поза межами."""
    dx, dy = x1 - x0, y1 - y0
    t0, t1 = 0.0, 1.0
    for p, q in ((-dx, x0 - xmin), (dx, xmax - x0), (-dy, y0 - ymin), (dy, ymax - y0)):
        if p == 0:
            if q < 0:
                return None
        else:
            r = q / p
            if p < 0:
                if r > t1:
                    return None
                t0 = max(t0, r)
            else:
                if r < t0:
                    return None
                t1 = min(t1, r)
    return x0 + t0 * dx, y0 + t0 * dy, x0 + t1 * dx, y0 + t1 * dy


def invert3(m):
    """Обернена матриця 3x3 (список рядків) або None, якщо вироджена."""
    a, b, c = m[0]
    d, e, f = m[1]
    g, h, i = m[2]
    det = a * (e * i - f * h) - b * (d * i - f * g) + c * (d * h - e * g)
    if abs(det) < 1e-14:
        return None
    return [
        [(e * i - f * h) / det, (c * h - b * i) / det, (b * f - c * e) / det],
        [(f * g - d * i) / det, (a * i - c * g) / det, (c * d - a * f) / det],
        [(d * h - e * g) / det, (b * g - a * h) / det, (a * e - b * d) / det],
    ]


# ----------------------------------------------------------------------
# Застосунок
# ----------------------------------------------------------------------
class App:
    def __init__(self, root: tk.Tk):
        self.root = root
        root.title("Лабораторна робота №1 — Лінійні перетворення")
        root.geometry("1280x800")
        root.minsize(900, 600)

        self.scene = Scene()

        # Вигляд: піксель = ox + x*zoom, oy - y*zoom
        self.zoom = 30.0
        self.ox = 0.0
        self.oy = 0.0
        self._w = 0
        self._h = 0
        self._pan = None
        self._pending = False
        self._syncing = False

        self.vars = {}
        self.dim_scales = {}
        self.show_grid = tk.BooleanVar(value=True)
        self.grid_n = tk.StringVar(value=str(self.scene.axes.grid_num))

        self._build_ui()
        self._sync_dims()
        self._refresh_matrices()

    # ------------------------------------------------------------------
    # Побудова інтерфейсу
    # ------------------------------------------------------------------
    def _build_ui(self):
        panel = ttk.Frame(self.root, padding=6)
        panel.pack(side="left", fill="y")

        right = ttk.Frame(self.root)
        right.pack(side="left", fill="both", expand=True)

        self.canvas = tk.Canvas(right, bg=BG, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.status = ttk.Label(right, anchor="w", padding=(8, 3))
        self.status.pack(fill="x")
        self._set_status()

        self.canvas.bind("<Configure>", self._on_configure)
        self.canvas.bind("<Button-1>", self._on_left_click)
        self.canvas.bind("<Motion>", self._on_motion)
        for b in ("2", "3"):  # права кнопка (на macOS -- Button-2) та середня
            self.canvas.bind(f"<ButtonPress-{b}>", self._pan_start)
            self.canvas.bind(f"<B{b}-Motion>", self._pan_move)
            self.canvas.bind(f"<ButtonRelease-{b}>", self._pan_end)
        self.canvas.bind("<MouseWheel>", self._on_wheel)
        self.canvas.bind("<Button-4>", self._on_wheel)  # Linux
        self.canvas.bind("<Button-5>", self._on_wheel)

        nb = ttk.Notebook(panel)
        nb.pack(fill="x")
        self._build_tab_dims(nb)
        self._build_tab_basic(nb)
        self._build_tab_world(nb)

        # --- Вигляд ---
        view = ttk.LabelFrame(panel, text="Вигляд", padding=6)
        view.pack(fill="x", pady=(8, 0))
        ttk.Checkbutton(view, text="Сітка", variable=self.show_grid,
                        command=self._schedule_redraw).grid(row=0, column=0, sticky="w")
        ttk.Label(view, text="Розмір сітки:").grid(row=0, column=1, padx=(12, 2))
        sp = ttk.Spinbox(view, from_=5, to=100, width=5, textvariable=self.grid_n,
                         command=self._on_grid_n)
        sp.grid(row=0, column=2)
        sp.bind("<Return>", lambda e: self._on_grid_n())
        ttk.Button(view, text="Вмістити", command=self._fit_and_redraw).grid(
            row=0, column=3, padx=(12, 0))

        # --- Скидання ---
        res = ttk.Frame(panel)
        res.pack(fill="x", pady=(8, 0))
        ttk.Button(res, text="Скинути деталь", command=self._reset_model_tf).pack(
            side="left", expand=True, fill="x")
        ttk.Button(res, text="Скинути СК", command=self._reset_world_tf).pack(
            side="left", expand=True, fill="x", padx=4)
        ttk.Button(res, text="Все", command=self._reset_all).pack(
            side="left", expand=True, fill="x")

        # --- Матриці ---
        mf = ttk.LabelFrame(panel, text="Поточні матриці", padding=4)
        mf.pack(fill="x", pady=(8, 0))
        self.mat_text = tk.Text(mf, height=9, width=38, font=("Courier", 9),
                                bg="#f4f4f4", relief="flat", state="disabled")
        self.mat_text.pack(fill="x")

    def _row(self, parent, row, label, fields):
        """Рядок: підпис + кілька полів вводу. fields = [(ключ, значення за замовч.)]."""
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w", pady=2)
        for j, (key, default) in enumerate(fields):
            var = tk.StringVar(value=str(default))
            self.vars[key] = var
            ttk.Entry(parent, textvariable=var, width=7).grid(row=row, column=j + 1, padx=2)

    def _button(self, parent, row, text, fn, span=4):
        ttk.Button(parent, text=text, command=lambda: self._run(fn)).grid(
            row=row, column=0, columnspan=span, sticky="ew", pady=(2, 6))

    def _build_tab_dims(self, nb):
        tab = ttk.Frame(nb, padding=6)
        nb.add(tab, text="Розміри")
        params = self.scene.model.params
        self._syncing = True
        for r, (label, name, lo, hi) in enumerate(DIMS):
            ttk.Label(tab, text=label).grid(row=r, column=0, sticky="sw")
            sc = tk.Scale(tab, from_=lo, to=hi, resolution=0.1, orient="horizontal",
                          length=180, command=lambda v, n=name: self._on_dim(n, v))
            sc.set(params[name])
            sc.grid(row=r, column=1, padx=4)
            self.dim_scales[name] = sc
        self._syncing = False
        ttk.Button(tab, text="Скинути розміри", command=self._reset_dims).grid(
            row=len(DIMS), column=0, columnspan=2, sticky="ew", pady=(6, 0))

    def _build_tab_basic(self, nb):
        tab = ttk.Frame(nb, padding=6)
        nb.add(tab, text="Евклідові / афінні")

        lf = ttk.LabelFrame(tab, text="Центр C (клік ЛКМ на сцені)", padding=6)
        lf.pack(fill="x")
        self._row(lf, 0, "C (x, y)", [("cx", 0), ("cy", 0)])

        lf = ttk.LabelFrame(tab, text="Евклідові", padding=6)
        lf.pack(fill="x", pady=(8, 0))
        self._row(lf, 0, "Зсув (dx, dy)", [("dx", 1), ("dy", 1)])
        self._button(lf, 1, "Зсунути", self._do_shift)
        self._row(lf, 2, "Кут, °", [("angle", 30)])
        self._button(lf, 3, "Обернути навколо C", self._do_rotate)

        lf = ttk.LabelFrame(tab, text="Афінні (окремі випадки)", padding=6)
        lf.pack(fill="x", pady=(8, 0))
        self._button(lf, 0, "Симетрія відносно C", self._do_symmetry)
        self._row(lf, 1, "Масштаб (sx, sy)", [("sx", 1.5), ("sy", 1.5)])
        self._button(lf, 2, "Масштабувати (відносно початку)", self._do_scale)

    def _build_tab_world(self, nb):
        tab = ttk.Frame(nb, padding=6)
        nb.add(tab, text="Афінне / проективне")

        lf = ttk.LabelFrame(tab, text="Загальне афінне (зміна базису)", padding=6)
        lf.pack(fill="x")
        self._row(lf, 0, "O (x, y)", [("a_ox", 0), ("a_oy", 0)])
        self._row(lf, 1, "X (x, y)", [("a_xx", 1), ("a_xy", 0)])
        self._row(lf, 2, "Y (x, y)", [("a_yx", 0), ("a_yy", 1)])
        self._button(lf, 3, "Застосувати афінне", self._do_affine)

        lf = ttk.LabelFrame(tab, text="Проективне", padding=6)
        lf.pack(fill="x", pady=(8, 0))
        self._row(lf, 0, "X кінець (x, y)", [("p_xx", 1), ("p_xy", 0)])
        self._row(lf, 1, "Y кінець (x, y)", [("p_yx", 0), ("p_yy", 1)])
        self._row(lf, 2, "O (x, y)", [("p_ox", 0), ("p_oy", 0)])
        self._row(lf, 3, "Ваги wx, wy, w0", [("p_wx", 1), ("p_wy", 1), ("p_w0", 1)])
        self._button(lf, 4, "Застосувати проективне", self._do_projective, span=4)
        ttk.Label(lf, foreground="#777", wraplength=300, justify="left",
                  text="Ваги всі = 1 -- тотожне перетворення. Різні ваги дають "
                       "перспективу; пряма w'=0 не повинна перетинати сцену."
                  ).grid(row=5, column=0, columnspan=4, sticky="w")

        ttk.Button(tab, text="Скинути систему координат",
                   command=self._reset_world_tf).pack(fill="x", pady=(8, 0))

    # ------------------------------------------------------------------
    # Допоміжне
    # ------------------------------------------------------------------
    def _num(self, key):
        return float(self.vars[key].get().strip().replace(",", "."))

    def _nums(self, *keys):
        return [self._num(k) for k in keys]

    def _run(self, fn):
        try:
            fn()
        except ValueError:
            self._set_status("Помилка: введіть коректні числа")

    def _set_status(self, text=None):
        hint = "ЛКМ — центр C   |   ПКМ — рух   |   колесо — масштаб"
        self.status.config(text=f"{text}     {hint}" if text else hint)

    def _changed(self):
        self._refresh_matrices()
        self._schedule_redraw()

    def _refresh_matrices(self):
        txt = ("Деталь (локальна):\n" + repr(self.scene.model_local_transform) +
               "\n\nСистема координат:\n" + repr(self.scene.world_transform))
        self.mat_text.config(state="normal")
        self.mat_text.delete("1.0", "end")
        self.mat_text.insert("1.0", txt)
        self.mat_text.config(state="disabled")

    # ------------------------------------------------------------------
    # Розміри
    # ------------------------------------------------------------------
    def _on_dim(self, name, value):
        if self._syncing:
            return
        self.scene.model.set_param(name, float(value))
        self._sync_dims()
        self._schedule_redraw()

    def _sync_dims(self):
        """Модель може скоригувати параметри (щоб деталь лишалась цілісною)."""
        self._syncing = True
        try:
            params = self.scene.model.params
            for name, sc in self.dim_scales.items():
                if abs(float(sc.get()) - params[name]) > 0.05:
                    sc.set(params[name])
        finally:
            self._syncing = False

    def _reset_dims(self):
        self.scene.model.reset_dimensions()
        self._sync_dims()
        self._schedule_redraw()

    # ------------------------------------------------------------------
    # Перетворення
    # ------------------------------------------------------------------
    def _do_shift(self):
        dx, dy = self._nums("dx", "dy")
        self.scene.shift_model(dx, dy)
        self._changed()

    def _do_rotate(self):
        cx, cy, ang = self._nums("cx", "cy", "angle")
        self.scene.rotate_model(cx, cy, ang)
        self._changed()

    def _do_symmetry(self):
        cx, cy = self._nums("cx", "cy")
        self.scene.symmetry_model(cx, cy)
        self._changed()

    def _do_scale(self):
        sx, sy = self._nums("sx", "sy")
        self.scene.scale_model(sx, sy)
        self._changed()

    def _do_affine(self):
        ox, oy, xx, xy, yx, yy = self._nums("a_ox", "a_oy", "a_xx", "a_xy", "a_yx", "a_yy")
        self.scene.set_affine_world(Point(ox, oy), Point(xx, xy), Point(yx, yy))
        self._changed()

    def _do_projective(self):
        xx, xy, yx, yy, ox, oy, wx, wy, w0 = self._nums(
            "p_xx", "p_xy", "p_yx", "p_yy", "p_ox", "p_oy", "p_wx", "p_wy", "p_w0")
        self.scene.set_projective_world(Point(xx, xy), Point(yx, yy), Point(ox, oy), wx, wy, w0)
        self._changed()

    def _reset_model_tf(self):
        self.scene.reset_model_transform()
        self._changed()

    def _reset_world_tf(self):
        self.scene.reset_world_transform()
        self._changed()

    def _reset_all(self):
        self.scene.reset_all()
        self._changed()

    def _on_grid_n(self):
        try:
            n = max(1, min(200, int(float(self.grid_n.get()))))
        except ValueError:
            return
        self.scene.axes.grid_num = n
        self._schedule_redraw()

    # ------------------------------------------------------------------
    # Вигляд: матриця, миша
    # ------------------------------------------------------------------
    def _view_matrix(self) -> Matrix3x3:
        s = self.zoom
        return Matrix3x3([
            [s, 0.0, 0.0],
            [0.0, -s, 0.0],
            [self.ox, self.oy, 1.0],
        ])

    def _full_matrix(self) -> Matrix3x3:
        """Світ осей/сітки -> пікселі."""
        return self.scene.world_transform.multiply(self._view_matrix())

    def _fit_view(self):
        self.zoom = max(5.0, min(self._w, self._h) / 22.0)  # видно приблизно ±11 одиниць
        self.ox = self._w / 2
        self.oy = self._h / 2

    def _fit_and_redraw(self):
        self._fit_view()
        self._schedule_redraw()

    def _on_configure(self, e):
        if self._w == 0:
            self._w, self._h = e.width, e.height
            self._fit_view()
        else:
            self.ox += (e.width - self._w) / 2
            self.oy += (e.height - self._h) / 2
            self._w, self._h = e.width, e.height
        self._schedule_redraw()

    def _screen_to_grid(self, sx, sy):
        inv = invert3(self._full_matrix().rows)
        if inv is None:
            return None
        x = sx * inv[0][0] + sy * inv[1][0] + inv[2][0]
        y = sx * inv[0][1] + sy * inv[1][1] + inv[2][1]
        w = sx * inv[0][2] + sy * inv[1][2] + inv[2][2]
        if abs(w) < 1e-12:
            return None
        return x / w, y / w

    def _on_left_click(self, e):
        pt = self._screen_to_grid(e.x, e.y)
        if pt is None:
            return
        self.vars["cx"].set(f"{pt[0]:.2f}")
        self.vars["cy"].set(f"{pt[1]:.2f}")
        self._schedule_redraw()

    def _on_motion(self, e):
        pt = self._screen_to_grid(e.x, e.y)
        if pt is None:
            self._set_status()
        else:
            self._set_status(f"x = {pt[0]:.2f},  y = {pt[1]:.2f}")

    def _pan_start(self, e):
        self._pan = (e.x, e.y, self.ox, self.oy)
        self.canvas.config(cursor="fleur")

    def _pan_move(self, e):
        if self._pan is None:
            return
        x0, y0, ox, oy = self._pan
        self.ox = ox + (e.x - x0)
        self.oy = oy + (e.y - y0)
        self._schedule_redraw()

    def _pan_end(self, e):
        self._pan = None
        self.canvas.config(cursor="")

    def _on_wheel(self, e):
        if e.num == 4 or e.delta > 0:
            f = 1.1
        elif e.num == 5 or e.delta < 0:
            f = 1 / 1.1
        else:
            return
        new = max(2.0, min(500.0, self.zoom * f))
        f = new / self.zoom
        self.ox = e.x - (e.x - self.ox) * f
        self.oy = e.y - (e.y - self.oy) * f
        self.zoom = new
        self._schedule_redraw()

    # ------------------------------------------------------------------
    # Рендеринг
    # ------------------------------------------------------------------
    def _schedule_redraw(self):
        if not self._pending:
            self._pending = True
            self.root.after_idle(self._redraw)

    def _flush(self, run, kw):
        if len(run) >= 4:
            self.canvas.create_line(*run, **kw)

    def _draw_poly(self, pts, rect, **kw):
        """Ламана у екранних координатах з відсіканням (захист від величезних значень)."""
        run = []
        for a, b in zip(pts, pts[1:]):
            seg = None
            if finite(a.x, a.y, b.x, b.y):
                seg = clip_segment(a.x, a.y, b.x, b.y, *rect)
            if seg is None:
                self._flush(run, kw)
                run = []
                continue
            x0, y0, x1, y1 = seg
            if run and abs(run[-2] - x0) < 1e-6 and abs(run[-1] - y0) < 1e-6:
                run += [x1, y1]
            else:
                self._flush(run, kw)
                run = [x0, y0, x1, y1]
        self._flush(run, kw)

    def _redraw(self):
        self._pending = False
        c = self.canvas
        c.delete("all")
        w, h = self._w, self._h
        if w < 10 or h < 10:
            return

        view = self._view_matrix()
        full = self._full_matrix()
        rect = (-60, -60, w + 60, h + 60)

        # --- сітка ---
        if self.show_grid.get():
            grid = self.scene.get_grid_polylines(view)
            n = self.scene.axes.grid_num
            ks = [k for k in range(-n, n + 1) if k != 0]
            known = len(grid) == 2 * len(ks)
            for i, poly in enumerate(grid):
                major = known and ks[i % len(ks)] % 5 == 0
                self._draw_poly(poly, rect, fill=GRID_MAJOR if major else GRID_MINOR, width=1)

        # --- осі ---
        axes = self.scene.get_axis_polylines(view)
        for poly in axes:
            self._draw_poly(poly, rect, fill=AXIS, width=2)

        self._draw_ticks(full, w, h)
        self._draw_axis_names(axes, full, w, h)

        # --- деталь ---
        for poly in self.scene.get_model_polylines(view):
            self._draw_poly(poly, rect, fill=MODEL, width=2, capstyle="round", joinstyle="round")

        # --- центр C ---
        try:
            cx, cy = self._nums("cx", "cy")
        except ValueError:
            return
        p = full.transform_point(Point(cx, cy))
        if finite(p.x, p.y) and -20 < p.x < w + 20 and -20 < p.y < h + 20:
            c.create_oval(p.x - 5, p.y - 5, p.x + 5, p.y + 5, outline=PIVOT, width=2)
            c.create_line(p.x - 10, p.y, p.x + 10, p.y, fill=PIVOT)
            c.create_line(p.x, p.y - 10, p.x, p.y + 10, fill=PIVOT)
            c.create_text(p.x + 10, p.y - 10, text="C", fill=PIVOT, font=("Arial", 10, "bold"))

    def _draw_ticks(self, full, w, h):
        """Цифри вздовж осей (слідують за перетворенням системи координат)."""
        c = self.canvas
        n = self.scene.axes.grid_num
        o = full.transform_point(Point(0.0, 0.0))
        for axis in (0, 1):
            e = full.transform_point(Point(1.0, 0.0) if axis == 0 else Point(0.0, 1.0))
            unit = math.hypot(e.x - o.x, e.y - o.y)
            if not finite(unit) or unit < 1e-6:
                continue
            step = next((s for s in NICE_STEPS if s * unit >= 42), NICE_STEPS[-1])
            for k in range(-n, n + 1):
                if k == 0 or k % step:
                    continue
                p = full.transform_point(Point(k, 0.0) if axis == 0 else Point(0.0, k))
                if not (-20 < p.x < w + 20 and -20 < p.y < h + 20):
                    continue  # також відсіює NaN/inf
                c.create_oval(p.x - 2, p.y - 2, p.x + 2, p.y + 2, fill=AXIS, outline="")
                if axis == 0:
                    c.create_text(p.x, p.y + 6, text=str(k), anchor="n", font=FONT, fill=TEXT)
                else:
                    c.create_text(p.x - 7, p.y, text=str(k), anchor="e", font=FONT, fill=TEXT)
        if finite(o.x, o.y) and -20 < o.x < w + 20 and -20 < o.y < h + 20:
            c.create_text(o.x - 6, o.y + 6, text="0", anchor="ne", font=FONT, fill=TEXT)

    def _draw_axis_names(self, axes, full, w, h):
        """Підписи X та Y -- біля видимого кінця додатної півосі."""
        o = full.transform_point(Point(0.0, 0.0))
        inner = (25, 25, w - 25, h - 25)
        for poly, name, (dx, dy) in zip(axes, ("X", "Y"), ((-12, -14), (14, 12))):
            pos = poly[1]
            if not finite(o.x, o.y, pos.x, pos.y):
                continue
            seg = clip_segment(o.x, o.y, pos.x, pos.y, *inner)
            if seg is None:
                continue
            self.canvas.create_text(seg[2] + dx, seg[3] + dy, text=name,
                                    font=FONT_AXIS, fill=AXIS)


def main():
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()