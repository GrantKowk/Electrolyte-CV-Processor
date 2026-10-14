from __future__ import annotations

import numpy as np
import pandas as pd

from .config import QCStatus, ScanMode

def _valid_number(value) -> bool:
    try:
        return value is not None and not pd.isna(value) and np.isfinite(float(value))
    except Exception:
        return False


def fmt_potential(value) -> str:
    return f"{float(value):.4f} V" if _valid_number(value) else "N/A"


def fmt_current(value) -> str:
    return f"{float(value):.3E} A" if _valid_number(value) else "N/A"


def fmt_shift(value) -> str:
    if not _valid_number(value):
        return "N/A"
    value = float(value)
    return f"{value:+.1f} mV" if value != 0 else "0.0 mV"


def format_cv_tooltip(curve, potential, current, mode):
    sm = ScanMode.MAX if mode == 'max' else ScanMode.MIN
    return (
        f"{curve}\n\n"
        f"Potential / 电位：{fmt_potential(potential)}\n"
        f"Current / 电流：{fmt_current(current)}\n"
        f"Scan / 扫描支：{sm.en} / {sm.cn}"
    )


def format_peak_tooltip(curve, peak_potential, peak_current, status, mode):
    sm = ScanMode.MAX if mode == 'max' else ScanMode.MIN
    text = (
        f"{curve} · {sm.en} Peak / {sm.cn}峰\n\n"
        f"Peak potential / 峰电位：{fmt_potential(peak_potential)}\n"
        f"Peak current / 峰电流：{fmt_current(peak_current)}\n"
        f"Peak status / 峰状态：{status}"
    )
    if status == QCStatus.BOUNDARY.value:
        text += "\n\n峰位靠近扫描边界，可能尚未形成完整峰。"
    elif status == QCStatus.FAILED.value:
        text += "\n\n未识别到可靠峰值。"
    return text


def format_onset_tooltip(curve, threshold_onset, tangent_onset, difference_mv, threshold_qc, tangent_qc):
    return (
        f"{curve} · Onset\n\n"
        f"Threshold / 阈值法：{fmt_potential(threshold_onset)}\n"
        f"Threshold QC：{threshold_qc}\n"
        f"Tangent / 切线法：{fmt_potential(tangent_onset)}\n"
        f"Tangent QC：{tangent_qc}\n"
        f"Difference / 方法差值：{(f'{float(difference_mv):.1f} mV' if _valid_number(difference_mv) else 'N/A')}"
    )


def format_shift_tooltip(curve, reference, peak_shift_mv, threshold_shift_mv, tangent_shift_mv):
    return (
        f"{curve}\n\nReference / 参考圈：{reference}\n"
        f"Peak shift / 峰位移：{fmt_shift(peak_shift_mv)}\n"
        f"Threshold onset shift / 阈值法起始电位位移：{fmt_shift(threshold_shift_mv)}\n"
        f"Tangent onset shift / 切线法起始电位位移：{fmt_shift(tangent_shift_mv)}"
    )
