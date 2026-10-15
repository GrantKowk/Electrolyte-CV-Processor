from __future__ import annotations

from ..i18n import tr

import os
import re
from pathlib import Path
import numpy as np
import pandas as pd

from .logging_utils import log_info, log_warning
from .parsers import parse_txt_to_curves, parse_excel_to_curves
from .analysis import (
    analyze_cv_features, filter_curves, split_at_extreme,
    generate_auto_indices,
)
from .export import _write_main_results_workbook, _style_simple_data_workbook


def _trapezoid_integral(y, x):
    """NumPy-version-compatible trapezoidal integration.

    NumPy 2.x introduced ``np.trapezoid`` and newer releases may no longer
    expose the legacy ``np.trapz`` name.  Prefer the modern API and only fall
    back to ``np.trapz`` on older NumPy versions.  The numerical operation and
    sign handling are intentionally unchanged from the original implementation.
    """
    if hasattr(np, "trapezoid"):
        return np.trapezoid(y, x)
    legacy_trapz = getattr(np, "trapz", None)
    if legacy_trapz is not None:
        return legacy_trapz(y, x)
    raise RuntimeError(tr('当前 NumPy 版本既不提供 trapezoid 也不提供 trapz'))

def process_cv_file(input_path, mode, scan_rate_mv, precision_mv, start_voltage, end_voltage,
                    save_verification, selection_mode, auto_target, manual_indices,
                    apply_cut_to_all, output_dir=None, return_all=False, include_raw_curves=False):
    "Process a CV file with configurable selection and output options.\n\nselection_mode: 'auto' or 'manual'.\nauto_target: target cycle count for automatic selection.\nmanual_indices: cycle numbers for manual selection (list of int).\napply_cut_to_all: apply cycle selection to all output files.\noutput_dir: output folder; default to the input file's folder when empty."
    if not os.path.isfile(input_path):
        raise FileNotFoundError(tr('文件不存在：{0}', input_path))

    scan_rate_v = scan_rate_mv / 1000.0

    input_path_obj = Path(input_path)
    if output_dir:
        output_path_obj = Path(output_dir).expanduser()
        output_path_obj.mkdir(parents=True, exist_ok=True)
        base = str(output_path_obj / input_path_obj.stem)
    else:
        # Without an explicit output path, write next to the input file.
        base = str(input_path_obj.with_suffix(''))

    split_file = base + "_Split.xlsx"
    prefix = "Positive" if mode == 'max' else "Negative"
    calc_file = base + "_" + prefix + ".xlsx" if save_verification else None
    extreme_suffix = "Max" if mode == 'max' else "Min"
    extreme_file = base + "_" + prefix + "_" + extreme_suffix + ".xlsx" if save_verification else None
    integral_file = base + "_Integral_Results.xlsx"

    target_voltage = end_voltage
    if mode == 'max' and end_voltage <= start_voltage:
        raise ValueError(tr('Max模式：终止电压须大于起始电压'))
    if mode == 'min' and start_voltage <= end_voltage:
        raise ValueError(tr('Min模式：起始电压须大于终止电压'))

    log_info(tr('开始处理：{0}', input_path))
    log_info(tr('输出目录：{0}', Path(base).parent))
    log_info(tr('模式：{0}，扫描速率：{1} mV/s', mode, scan_rate_mv))
    log_info(tr('电压范围：{0}V → {1}V', start_voltage, end_voltage))
    log_info(tr('切分精度：±{0} mV，目标电压：{1}V', precision_mv, target_voltage))
    if save_verification:
        log_info(tr('生成验证文件'))
    else:
        log_info(tr('不生成验证文件'))
    if apply_cut_to_all:
        log_info(tr('仅输出圈号列表数据'))
    else:
        log_info(tr('输出全部圈数数据'))

    ext = Path(input_path).suffix.lower()
    if ext in ('.txt', '.dta'):
        curves = parse_txt_to_curves(input_path)
    else:
        curves = parse_excel_to_curves(input_path)

    # Feature analysis must use raw curves before filtering out baseline points by current sign.
    log_info(tr('正在分析峰电位与起始电位...'))
    feature_df_all, feature_verification = analyze_cv_features(curves, mode)
    if not feature_df_all.empty:
        log_info(tr('特征电位分析完成，共 {0} 条有效曲线', len(feature_df_all)))
    else:
        log_warning(tr('特征电位分析未得到有效结果；积分流程仍继续'))

    # Preserve the integration workflow's positive/negative current filtering.
    filtered = filter_curves(curves, mode)

    # Split curves.
    log_info(tr('正在切分曲线...'))
    split_results = {}
    for name, df in filtered.items():
        try:
            p1, p2 = split_at_extreme(df, mode, target_voltage, precision_mv)
            split_results[name] = (p1, p2)
        except ValueError as e:
            raise ValueError(tr('曲线 {0} 切分失败：{1}', name, e))

    log_info(tr('切分完成，开始计算积分...'))

    # ---- Integrate all curves for _Integral_Results and subsequent filtering ----
    integral_rows = []
    for name, (p1, p2) in split_results.items():
        if p1 is not None and len(p1) > 1:
            area1 = abs(_trapezoid_integral(p1['Im'], p1['Vf']))
            q1 = area1 / scan_rate_v
            v_start1 = p1['Vf'].iloc[0]
            v_end1 = p1['Vf'].iloc[-1]
        else:
            area1 = 0.0; q1 = 0.0; v_start1 = v_end1 = None
        if p2 is not None and len(p2) > 1:
            area2 = abs(_trapezoid_integral(p2['Im'], p2['Vf']))
            q2 = area2 / scan_rate_v
            v_start2 = p2['Vf'].iloc[0]
            v_end2 = p2['Vf'].iloc[-1]
        else:
            area2 = 0.0; q2 = 0.0; v_start2 = v_end2 = None
        if q1 >= q2:
            Q1, Q2 = q1, q2; A1, A2 = area1, area2
        else:
            Q1, Q2 = q2, q1; A1, A2 = area2, area1
        total_area = A1 + A2
        record = {
            'Curve': name,
            'Q1 (C)': Q1,
            'Q2 (C)': Q2,
            'A1 (A·V)': A1,
            'A2 (A·V)': A2,
            'A_total (A·V)': total_area,
            'V_start_Part1': v_start1,
            'V_end_Part1': v_end1,
            'V_start_Part2': v_start2,
            'V_end_Part2': v_end2
        }
        integral_rows.append(record)

    if not integral_rows:
        raise ValueError(tr('未生成积分数据'))

    df_integral_all = pd.DataFrame(integral_rows)
    charge_type = "Q_ox (C)" if mode == 'max' else "Q_red (C)"
    df_integral_all[charge_type] = df_integral_all['Q1 (C)'] + df_integral_all['Q2 (C)']

    # Analyze features on all raw curves, then apply the requested cycle selection.
    # Outer-merge so cycles with valid features remain visible in GUI/QC even when integration fails.
    if feature_df_all is not None and not feature_df_all.empty:
        df_integral_all = df_integral_all.merge(feature_df_all, on='Curve', how='outer')

    def _curve_no(name):
        m = re.search(r'(\d+)$', str(name))
        return int(m.group(1)) if m else 10**9

    df_integral_all['_curve_no'] = df_integral_all['Curve'].map(_curve_no)
    df_integral_all = (
        df_integral_all.sort_values('_curve_no')
        .drop(columns=['_curve_no'])
        .reset_index(drop=True)
    )

    # ---- Determine the final output cycles ----
    available_indices = sorted({_curve_no(name) for name in df_integral_all['Curve'] if _curve_no(name) < 10**9})
    total_curves = len(available_indices)
    log_info(tr('总有效圈数：{0}', total_curves))
    if total_curves == 0:
        raise ValueError(tr('未检测到有效曲线'))

    if selection_mode == 'auto':
        target_count = auto_target if auto_target > 0 else 5
        if total_curves <= target_count:
            selected_indices = list(available_indices)
        else:
            # Sample evenly from existing cycle numbers without assuming consecutive numbering.
            positions = generate_auto_indices(total_curves, target_count)
            selected_indices = [available_indices[pos - 1] for pos in positions]
        log_info(tr('自动选择圈号：{0}', selected_indices))
    else:
        selected_indices = [i for i in manual_indices if i in available_indices]
        if not selected_indices:
            raise ValueError(tr('手动模式：指定的圈号均无效，请检查输入'))
        if len(selected_indices) < len(manual_indices):
            log_warning(tr('部分圈号不存在或无效，已忽略'))
        log_info(tr('手动选择圈号：{0}', selected_indices))

    # Apply cycle selection according to apply_cut_to_all.
    if apply_cut_to_all:
        selected_curve_names = [f"CURVE{i}" for i in selected_indices]
        # Filter integration results.
        df_integral_filtered = df_integral_all[df_integral_all['Curve'].isin(selected_curve_names)].copy()
        # Preserve ordering.
        order_map = {name: idx for idx, name in enumerate(selected_curve_names)}
        df_integral_filtered['_order'] = df_integral_filtered['Curve'].map(order_map)
        df_integral_filtered = df_integral_filtered.sort_values('_order').drop('_order', axis=1)
        log_info(tr('积分结果已过滤，保留 {0} 条曲线', len(df_integral_filtered)))
        # Filter curves and filtered data for _Split.xlsx and verification files as well.
        curves_filtered = {name: df for name, df in curves.items() if name in selected_curve_names}
        filtered_filtered = {name: df for name, df in filtered.items() if name in selected_curve_names}
        split_results_filtered = {name: (p1, p2) for name, (p1, p2) in split_results.items() if name in selected_curve_names}
        feature_verification_filtered = {name: df for name, df in feature_verification.items() if name in selected_curve_names}
    else:
        # Export all cycles without filtering.
        df_integral_filtered = df_integral_all.copy()
        curves_filtered = curves
        filtered_filtered = filtered
        split_results_filtered = split_results
        feature_verification_filtered = feature_verification
        selected_curve_names = None  # Not applicable.

    # ---- Save _Split.xlsx with the selected-cycle rule ----
    log_info(tr('保存拆分文件...'))
    with pd.ExcelWriter(split_file, engine='openpyxl') as writer:
        for name, df in curves_filtered.items():
            df.to_excel(writer, sheet_name=name, index=False)
    _style_simple_data_workbook(split_file)
    log_info(tr('已生成：{0}', split_file))

    # ---- Optional verification files ----
    if save_verification and calc_file:
        log_info(tr('保存筛选数据到 {0}...', calc_file))
        with pd.ExcelWriter(calc_file, engine='openpyxl') as writer:
            for name, df in filtered_filtered.items():
                df.to_excel(writer, sheet_name=name, index=False)
        _style_simple_data_workbook(calc_file)
        log_info(tr('已生成：{0}', calc_file))

    if save_verification and extreme_file:
        log_info(tr('保存切分数据到 {0}...', extreme_file))
        with pd.ExcelWriter(extreme_file, engine='openpyxl') as writer:
            for name, (p1, p2) in split_results_filtered.items():
                if p1 is not None and not p1.empty:
                    p1.to_excel(writer, sheet_name=f"{name}_Part1", index=False)
                if p2 is not None and not p2.empty:
                    p2.to_excel(writer, sheet_name=f"{name}_Part2", index=False)
        _style_simple_data_workbook(extreme_file)
        log_info(tr('已生成：{0}', extreme_file))

    # ---- Save the four-sheet results workbook with QC last ----
    _write_main_results_workbook(integral_file, df_integral_filtered, mode)
    log_info(tr('积分与特征结果工作簿：{0}', integral_file))

    # Append integration, feature results and diagnostic data to verification files when enabled.
    if save_verification and extreme_file:
        with pd.ExcelWriter(extreme_file, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            df_integral_filtered.to_excel(writer, sheet_name='Integral_Results', index=False)
            if feature_df_all is not None and not feature_df_all.empty:
                feature_summary = feature_df_all.copy()
                if apply_cut_to_all and selected_curve_names is not None:
                    feature_summary = feature_summary[feature_summary['Curve'].isin(selected_curve_names)].copy()
                    order_map = {name: idx for idx, name in enumerate(selected_curve_names)}
                    feature_summary['_order'] = feature_summary['Curve'].map(order_map)
                    feature_summary = feature_summary.sort_values('_order').drop(columns=['_order'])
                feature_summary.to_excel(writer, sheet_name='Feature_Results', index=False)
            for name, verify_df in feature_verification_filtered.items():
                # Excel sheet names are limited to 31 characters; names such as F_CURVE20 fit.
                verify_df.to_excel(writer, sheet_name=f"F_{name}"[:31], index=False)
        _style_simple_data_workbook(extreme_file)
        log_info(tr('积分结果与特征电位验证数据已追加到验证文件'))

    if return_all:
        base_result = (
            (extreme_file if save_verification else split_file),
            integral_file,
            df_integral_filtered,
            df_integral_all,
        )
        # GUI previews may reuse the original CURVE data parsed during this analysis.
        # Keep the original four-value return by default for compatibility with existing callers.
        if include_raw_curves:
            return base_result + (curves,)
        return base_result
    return (extreme_file if save_verification else split_file), integral_file, df_integral_filtered
