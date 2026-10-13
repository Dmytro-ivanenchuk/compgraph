"""Низькорівневе малювання: відсікання відрізків та ламані."""

import math


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


def draw_polyline(canvas, pts, rect, **kw):
    """Ламана в екранних координатах із відсіканням прямокутником rect."""
    xmin, ymin, xmax, ymax = rect
    run = []

    def flush():
        if len(run) >= 4:
            canvas.create_line(*run, **kw)
        run.clear()

    for a, b in zip(pts, pts[1:]):
        x0, y0, x1, y1 = a.x, a.y, b.x, b.y
        if xmin <= x0 <= xmax and xmin <= x1 <= xmax and ymin <= y0 <= ymax and ymin <= y1 <= ymax:
            seg = (x0, y0, x1, y1)  # цілком у вікні -- відсікання не потрібне
        elif math.isfinite(x0 + y0 + x1 + y1):
            seg = clip_segment(x0, y0, x1, y1, xmin, ymin, xmax, ymax)
        else:
            seg = None
        if seg is None:
            flush()
            continue
        x0, y0, x1, y1 = seg
        if run and abs(run[-2] - x0) < 1e-6 and abs(run[-1] - y0) < 1e-6:
            run += [x1, y1]
        else:
            flush()
            run += [x0, y0, x1, y1]
    flush()
