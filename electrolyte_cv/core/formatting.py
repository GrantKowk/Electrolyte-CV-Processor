from __future__ import annotations

from ..i18n import tr

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
        tr('{0}\n\nPotential / 电位：{1}\nCurrent / 电流：{2}\nScan / 扫描支：{3} / {4}', curve, fmt_potential(potential), fmt_current(current), sm.en, sm.cn)
    )


def format_peak_tooltip(curve, peak_potential, peak_current, status, mode):
    sm = ScanMode.MAX if mode == 'max' else ScanMode.MIN
    text = (
        tr('{0} · {1} Peak / {2}峰\n\nPeak potential / 峰电位：{3}\nPeak current / 峰电流：{4}\nPeak status / 峰状态：{5}', curve, sm.en, sm.cn, fmt_potential(peak_potential), fmt_current(peak_current), status)
    )
    if status == QCStatus.BOUNDARY.value:
        text += tr('\n\n峰位靠近扫描边界，可能尚未形成完整峰。')
    elif status == QCStatus.FAILED.value:
        text += tr('\n\n未识别到可靠峰值。')
    return text


def format_onset_tooltip(curve, threshold_onset, tangent_onset, difference_mv, threshold_qc, tangent_qc):
    return (
        tr('{0} · Onset\n\nThreshold / 阈值法：{1}\nThreshold QC：{2}\nTangent / 切线法：{3}\nTangent QC：{4}\nDifference / 方法差值：{5}', curve, fmt_potential(threshold_onset), threshold_qc, fmt_potential(tangent_onset), tangent_qc, f'{float(difference_mv):.1f} mV' if _valid_number(difference_mv) else 'N/A')
    )


def format_shift_tooltip(curve, reference, peak_shift_mv, threshold_shift_mv, tangent_shift_mv):
    return (
        tr('{0}\n\nReference / 参考圈：{1}\nPeak shift / 峰位移：{2}\nThreshold onset shift / 阈值法起始电位位移：{3}\nTangent onset shift / 切线法起始电位位移：{4}', curve, reference, fmt_shift(peak_shift_mv), fmt_shift(threshold_shift_mv), fmt_shift(tangent_shift_mv))
    )
