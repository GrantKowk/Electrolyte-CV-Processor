from __future__ import annotations

"""Pure, Qt-free helpers for preparing raw CV data for plotting.

This module deliberately contains no business-analysis decisions.  It only
normalizes already parsed Vf/Im data for the GUI preview and makes the preview
robust to an invalid scan branch, optional smoothing, and short placeholder
CURVEs produced by some instruments.
"""

import numpy as np
import pandas as pd

from .analysis import _extract_forward_scan, _smooth_current_by_voltage
from .config import FEATURE_SMOOTH_MV


MIN_PLOT_POINTS = 5


def prepare_cv_curve_for_plot(
    raw: pd.DataFrame,
    mode: str,
    *,
    full_scan: bool = False,
    smooth: bool = False,
    smooth_width_mv: float = FEATURE_SMOOTH_MV,
    min_points: int = MIN_PLOT_POINTS,
):
    """Prepare one raw CURVE for Matplotlib preview.

    Returns a dict containing ``v``, ``i_raw``, optional ``i_smooth`` and an
    optional ``scan_warning``.  Scan-branch extraction failure falls back to
    the cleaned raw curve.  Smoothing is *not called* when ``smooth=False``.

    ``ValueError`` is reserved for a curve that cannot reasonably be plotted;
    callers should skip that curve instead of aborting the whole canvas.
    """
    if raw is None or raw.empty:
        raise ValueError("曲线为空")
    if "Vf" not in raw.columns or "Im" not in raw.columns:
        raise ValueError("缺少 Vf/Im 列")

    clean = raw[["Vf", "Im"]].copy()
    clean["Vf"] = pd.to_numeric(clean["Vf"], errors="coerce")
    clean["Im"] = pd.to_numeric(clean["Im"], errors="coerce")
    clean = clean.dropna(subset=["Vf", "Im"]).reset_index(drop=True)
    if len(clean) < max(2, int(min_points)):
        raise ValueError(f"有效数值点不足 {max(2, int(min_points))} 个")

    scan_warning = None
    if full_scan:
        view = clean
    else:
        try:
            view, _direction_fraction = _extract_forward_scan(clean, mode)
            if view is None or view.empty:
                view = clean
                scan_warning = "分析扫描支为空，已回退完整 CV"
        except Exception as exc:
            view = clean
            scan_warning = f"分析扫描支识别失败，已回退完整 CV：{exc}"

    v = view["Vf"].to_numpy(dtype=float)
    i_raw = view["Im"].to_numpy(dtype=float)
    finite = np.isfinite(v) & np.isfinite(i_raw)
    v = v[finite]
    i_raw = i_raw[finite]
    if len(v) < max(2, int(min_points)):
        raise ValueError(f"绘图有效点不足 {max(2, int(min_points))} 个")

    i_smooth = None
    smooth_window = None
    if smooth:
        i_smooth, smooth_window = _smooth_current_by_voltage(v, i_raw, smooth_width_mv)
        i_smooth = np.asarray(i_smooth, dtype=float)
        if len(i_smooth) != len(v):
            raise ValueError("平滑结果长度与原始数据不一致")

    return {
        "v": v,
        "i_raw": i_raw,
        "i_smooth": i_smooth,
        "smooth_window": smooth_window,
        "scan_warning": scan_warning,
    }


def _valid_scalar(value):
    try:
        return value is not None and np.isfinite(float(value))
    except Exception:
        return False


def interpolate_current_on_analysis_branch(raw: pd.DataFrame, mode: str, potential: float,
                                           *, min_points: int = MIN_PLOT_POINTS) -> float:
    """Map a feature potential to current on the *analysis scan branch*.

    This helper is intentionally independent of whichever CV view is currently
    displayed.  In full-CV mode the displayed voltage trace is non-monotonic and
    the same potential can occur on two branches, so marker Y coordinates must
    never be obtained by sorting/interpolating the full loop.
    """
    prepared = prepare_cv_curve_for_plot(
        raw, mode, full_scan=False, smooth=False, min_points=min_points
    )
    v = np.asarray(prepared["v"], dtype=float)
    i = np.asarray(prepared["i_raw"], dtype=float)
    finite = np.isfinite(v) & np.isfinite(i)
    v = v[finite]; i = i[finite]
    if len(v) < 2:
        raise ValueError("分析扫描支有效点不足，无法定位标记")

    order = np.argsort(v, kind="mergesort")
    sv = v[order]; si = i[order]
    # Collapse duplicate/plateau voltages on the same branch by averaging their
    # currents.  This preserves branch identity while making interpolation stable.
    uniq, inverse = np.unique(sv, return_inverse=True)
    sums = np.zeros(len(uniq), dtype=float)
    counts = np.zeros(len(uniq), dtype=float)
    np.add.at(sums, inverse, si)
    np.add.at(counts, inverse, 1.0)
    ui = sums / np.maximum(counts, 1.0)
    if len(uniq) < 2:
        raise ValueError("分析扫描支电位变化不足，无法定位标记")
    return float(np.interp(float(potential), uniq, ui))


def build_cv_marker_positions(
    raw: pd.DataFrame,
    row,
    mode: str,
    columns: dict,
    *,
    show_peak: bool = True,
    show_threshold: bool = True,
    show_tangent: bool = True,
):
    """Build Qt-free marker coordinates for the CV preview layer.

    The analysis potentials themselves are never modified here.  We extract the
    analysis branch once and use it only to map feature potential -> display
    current, so full-CV view cannot accidentally place an onset marker on the
    opposite sweep branch.
    """
    out = []
    peak_col = columns["peak"]
    current_col = columns["current"]
    thr_col = columns["threshold"]
    tan_col = columns["tangent"]

    branch_cache = None

    def branch_current(potential):
        nonlocal branch_cache
        if branch_cache is None:
            prepared = prepare_cv_curve_for_plot(
                raw, mode, full_scan=False, smooth=False, min_points=MIN_PLOT_POINTS
            )
            v = np.asarray(prepared["v"], dtype=float)
            i = np.asarray(prepared["i_raw"], dtype=float)
            finite = np.isfinite(v) & np.isfinite(i)
            v = v[finite]; i = i[finite]
            if len(v) < 2:
                raise ValueError("分析扫描支有效点不足，无法定位标记")
            order = np.argsort(v, kind="mergesort")
            sv = v[order]; si = i[order]
            uniq, inverse = np.unique(sv, return_inverse=True)
            sums = np.zeros(len(uniq), dtype=float)
            counts = np.zeros(len(uniq), dtype=float)
            np.add.at(sums, inverse, si)
            np.add.at(counts, inverse, 1.0)
            ui = sums / np.maximum(counts, 1.0)
            if len(uniq) < 2:
                raise ValueError("分析扫描支电位变化不足，无法定位标记")
            branch_cache = (uniq, ui)
        uniq, ui = branch_cache
        return float(np.interp(float(potential), uniq, ui))

    if show_peak and _valid_scalar(row.get(peak_col)):
        x = float(row.get(peak_col))
        y = float(row.get(current_col)) if _valid_scalar(row.get(current_col)) else branch_current(x)
        out.append({"kind": "peak", "x": x, "y": y})

    if show_threshold and _valid_scalar(row.get(thr_col)):
        x = float(row.get(thr_col))
        out.append({"kind": "threshold", "x": x, "y": branch_current(x)})

    if show_tangent and _valid_scalar(row.get(tan_col)):
        x = float(row.get(tan_col))
        out.append({"kind": "tangent", "x": x, "y": branch_current(x)})

    return out
