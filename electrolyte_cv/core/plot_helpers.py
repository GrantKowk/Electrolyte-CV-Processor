from __future__ import annotations

"""Qt-free helpers shared by Matplotlib result plots.

These helpers only arrange display objects.  They do not alter CV analysis
results or electrochemical feature calculations.
"""

from dataclasses import dataclass
import math


@dataclass(frozen=True)
class LabelPlacement:
    dx: float
    dy: float
    ha: str
    va: str
    arrow: bool


def _overlaps(a, b, pad=2.0):
    ax0, ay0, ax1, ay1 = a
    bx0, by0, bx1, by1 = b
    return not (
        ax1 + pad < bx0 or bx1 + pad < ax0 or
        ay1 + pad < by0 or by1 + pad < ay0
    )


def _candidate_offsets(preferred: str, near_left: bool, near_right: bool,
                       near_bottom: bool, near_top: bool):
    """Return deterministic point-offset candidates ordered by preference.

    The candidate ladder intentionally contains several vertical levels.  A
    20-cycle two-series plot can contain about 40 labels, and six fixed offsets
    are not enough once the traces converge.  Larger offsets automatically get
    leader lines in :class:`MplPanel`, so readability is preferred over putting
    multiple labels in the same box.
    """
    up = [
        (0, 9), (10, 10), (-10, 10),
        (0, 22), (16, 18), (-16, 18),
        (0, 35), (24, 30), (-24, 30),
        (0, 49), (32, 42), (-32, 42),
        (0, 63),
    ]
    down = [
        (0, -10), (10, -11), (-10, -11),
        (0, -24), (16, -20), (-16, -20),
        (0, -37), (24, -32), (-24, -32),
        (0, -51), (32, -44), (-32, -44),
        (0, -65),
    ]
    neutral = [
        (7, 8), (-7, 8), (7, -11), (-7, -11),
        (14, 17), (-14, 17), (14, -19), (-14, -19),
        (0, 28), (0, -30), (26, 26), (-26, 26),
        (26, -28), (-26, -28),
    ]
    candidates = (up + down + neutral) if preferred == "up" else (
        down + up + neutral if preferred == "down" else neutral + up + down
    )

    # Prefer offsets pointing into the axes near boundaries without removing
    # the other candidates entirely; a later collision check may still need
    # them.
    def score(v):
        dx, dy = v
        penalty = 0
        if near_right and dx > 0: penalty += 4
        if near_left and dx < 0: penalty += 4
        if near_top and dy > 0: penalty += 4
        if near_bottom and dy < 0: penalty += 4
        penalty += (abs(dx) + abs(dy)) * 0.002
        return penalty
    return sorted(candidates, key=score)


def _overlap_area(a, b):
    x0 = max(a[0], b[0]); y0 = max(a[1], b[1])
    x1 = min(a[2], b[2]); y1 = min(a[3], b[3])
    if x1 <= x0 or y1 <= y0:
        return 0.0
    return (x1 - x0) * (y1 - y0)


def smart_label_layout(items, xlim, ylim, axes_size=(900.0, 520.0), fontsize=8.5):
    """Compute collision-aware annotation offsets without Matplotlib/Qt.

    Parameters
    ----------
    items:
        Iterable of dict-like objects containing ``x``, ``y``, ``text`` and
        optional ``preferred`` (``up``/``down``/``neutral``).

    Returns
    -------
    list[LabelPlacement]
        One placement per input item, preserving order.

    Notes
    -----
    This is intentionally lightweight.  It approximates text boxes in display
    pixels and tries several offsets.  It avoids a new third-party dependency
    while producing deterministic, readable layouts for typical 20-cycle CV
    result charts.
    """
    items = list(items)
    if not items:
        return []
    x0, x1 = map(float, xlim)
    y0, y1 = map(float, ylim)
    w, h = map(float, axes_size)
    xspan = x1 - x0 if abs(x1 - x0) > 1e-15 else 1.0
    yspan = y1 - y0 if abs(y1 - y0) > 1e-15 else 1.0
    occupied = []
    out = []

    for item in items:
        x = float(item["x"]); y = float(item["y"])
        text = str(item.get("text", ""))
        preferred = str(item.get("preferred", "neutral")).lower()
        px = (x - x0) / xspan * w
        py = (y - y0) / yspan * h
        near_left = px < 0.12 * w
        near_right = px > 0.88 * w
        near_bottom = py < 0.16 * h
        near_top = py > 0.84 * h
        candidates = _candidate_offsets(preferred, near_left, near_right, near_bottom, near_top)

        # Approximate a compact annotation bbox.  CJK glyphs are close to one
        # em wide; Latin numeric labels are usually narrower, so this is a safe
        # but not wildly oversized estimate.
        text_w = max(24.0, min(180.0, len(text) * fontsize * 0.72 + 8.0))
        text_h = fontsize * 1.55 + 5.0
        chosen = candidates[-1]
        chosen_box = None
        chosen_align = ("left", "bottom")
        fallback = None

        for order, (dx, dy) in enumerate(candidates):
            ax = px + dx
            ay = py + dy
            ha = "right" if dx < 0 else ("center" if dx == 0 else "left")
            va = "top" if dy < 0 else "bottom"
            if ha == "right":
                bx0, bx1 = ax - text_w, ax
            elif ha == "center":
                bx0, bx1 = ax - text_w / 2.0, ax + text_w / 2.0
            else:
                bx0, bx1 = ax, ax + text_w
            if va == "top":
                by0, by1 = ay - text_h, ay
            else:
                by0, by1 = ay, ay + text_h
            box = (bx0, by0, bx1, by1)
            outside_extent = (
                max(0.0, -bx0) + max(0.0, bx1 - w) +
                max(0.0, -by0) + max(0.0, by1 - h)
            )
            overlap_cost = sum(_overlap_area(box, old) for old in occupied)
            # Keep a least-bad candidate for pathological density instead of
            # blindly reusing the final offset.  Boundary violations are much
            # more expensive than a small overlap.
            cost = overlap_cost + outside_extent * 250.0 + order * 0.01
            if fallback is None or cost < fallback[0]:
                fallback = (cost, (dx, dy), box, (ha, va))
            if outside_extent > 0:
                continue
            if not any(_overlaps(box, old) for old in occupied):
                chosen = (dx, dy)
                chosen_box = box
                chosen_align = (ha, va)
                break

        if chosen_box is None and fallback is not None:
            _cost, chosen, chosen_box, chosen_align = fallback

        occupied.append(chosen_box)
        dx, dy = chosen
        out.append(LabelPlacement(
            dx=float(dx), dy=float(dy),
            ha=chosen_align[0], va=chosen_align[1],
            arrow=(abs(dx) >= 9 or abs(dy) >= 12),
        ))
    return out



def build_onset_label_items(x_values, threshold_values, tangent_values,
                            *, show_threshold=True, show_tangent=True, precision=4):
    """Build semantic onset label items for the shared layout engine.

    This keeps the display-only de-duplication rule headless-testable: when both
    methods round to the same shown value, one combined label is used.  The
    underlying Threshold/Tangent values remain completely independent.
    """
    out = []
    both = bool(show_threshold and show_tangent)
    fmt = f"{{:.{int(precision)}f}}"
    for x, t, g in zip(x_values, threshold_values, tangent_values):
        try:
            t_ok = t is not None and math.isfinite(float(t))
        except Exception:
            t_ok = False
        try:
            g_ok = g is not None and math.isfinite(float(g))
        except Exception:
            g_ok = False
        if both and t_ok and g_ok and fmt.format(float(t)) == fmt.format(float(g)):
            out.append({
                "x": float(x), "y": (float(t) + float(g)) / 2.0,
                "text": f"阈/切 {fmt.format(float(t))}",
                "kind": "combined", "preferred": "up",
            })
            continue
        if show_threshold and t_ok:
            out.append({
                "x": float(x), "y": float(t),
                "text": f"阈 {fmt.format(float(t))}" if both else fmt.format(float(t)),
                "kind": "threshold", "preferred": "up",
            })
        if show_tangent and g_ok:
            out.append({
                "x": float(x), "y": float(g),
                "text": f"切 {fmt.format(float(g))}" if both else fmt.format(float(g)),
                "kind": "tangent", "preferred": "down",
            })
    return out

def adaptive_legend_layout(count: int):
    """Return legend kwargs and a transient layout reservation.

    ``layout_override`` is merged with the panel's user layout only while the
    legend needs outside space; it never overwrites the user's stored margins.
    """
    count = max(0, int(count))
    if count <= 6:
        return {
            "kwargs": {"loc": "best", "ncol": 1},
            "layout_override": {},
        }
    if count <= 12:
        return {
            "kwargs": {"loc": "lower center", "bbox_to_anchor": (0.5, 1.02), "ncol": 3},
            "layout_override": {"top": 0.78},
        }
    ncol = min(5, max(3, math.ceil(count / 4.0)))
    return {
        "kwargs": {"loc": "lower center", "bbox_to_anchor": (0.5, 1.02), "ncol": ncol},
        "layout_override": {"top": 0.70},
    }
