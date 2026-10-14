from __future__ import annotations

import re
import numpy as np
import pandas as pd

from .config import (
    QCStatus, FEATURE_SMOOTH_MV, FEATURE_BASELINE_FRACTION,
    FEATURE_BASELINE_MIN_MV, FEATURE_BASELINE_MAX_MV, FEATURE_ONSET_SIGMA,
    FEATURE_ONSET_PERSIST_MV, FEATURE_TANGENT_LOW_FRAC, FEATURE_TANGENT_HIGH_FRAC,
    FEATURE_TANGENT_R2_MIN, FEATURE_BOUNDARY_MV,
)
from .logging_utils import log_info, log_warning

def filter_curves(curves, mode):
    """根据模式筛选，跳过无效曲线"""
    log_info(f"开始筛选数据（模式：{mode}）")
    filtered = {}
    MIN_POINTS = 100
    for name, df in curves.items():
        df = df.copy()
        df['Im'] = pd.to_numeric(df['Im'], errors='coerce')
        df = df.dropna(subset=['Im'])
        if df.empty:
            log_warning(f"曲线 {name} 无有效 Im 数据，跳过")
            continue
        if mode == 'max':
            mask = df['Im'] >= 0
        else:
            mask = df['Im'] <= 0
        filtered_df = df.loc[mask].reset_index(drop=True)
        if filtered_df.empty:
            log_warning(f"曲线 {name} 筛选后为空，已跳过")
            continue
        if len(filtered_df) < MIN_POINTS:
            log_warning(f"曲线 {name} 数据点仅 {len(filtered_df)}（少于 {MIN_POINTS}），判定无效，已跳过")
            continue
        filtered[name] = filtered_df
    if not filtered:
        raise ValueError("所有曲线筛选后均为空，无法继续")
    log_info(f"筛选完成，共 {len(filtered)} 条有效曲线")
    return filtered

# ================== 极值切分 ==================
def split_at_extreme(df, mode, target_voltage, precision_mv):
    if len(df) == 0:
        raise ValueError("数据框为空，无法切分")
    half_width = precision_mv / 1000.0
    v_min = target_voltage - half_width
    v_max = target_voltage + half_width
    mask = (df['Vf'] >= v_min) & (df['Vf'] <= v_max)
    window_df = df.loc[mask]
    if window_df.empty:
        raise ValueError(f"电压 {target_voltage:.4f} V ± {precision_mv} mV 内无数据点")
    if mode == 'max':
        idx = window_df['Im'].idxmax()
    else:
        idx = window_df['Im'].idxmin()
    part1 = df.iloc[:idx+1].reset_index(drop=True)
    part2 = df.iloc[idx:].reset_index(drop=True)
    return part1, part2

# ================== 特征电位分析 ==================
def _clean_numeric_curve(df):
    """仅保留可用于特征分析的数值 Vf / Im 数据。"""
    if df is None or df.empty or 'Vf' not in df.columns or 'Im' not in df.columns:
        return pd.DataFrame(columns=['Vf', 'Im'])
    out = df[['Vf', 'Im']].copy()
    out['Vf'] = pd.to_numeric(out['Vf'], errors='coerce')
    out['Im'] = pd.to_numeric(out['Im'], errors='coerce')
    out = out.dropna(subset=['Vf', 'Im']).reset_index(drop=True)
    return out


def _odd_window_from_voltage(v, width_mv, min_points=5):
    """把目标平滑电压宽度转换为奇数窗口点数。"""
    v = np.asarray(v, dtype=float)
    if len(v) < min_points:
        return max(1, len(v))
    dv = np.abs(np.diff(v))
    dv = dv[np.isfinite(dv) & (dv > 0)]
    if len(dv) == 0:
        return min_points if min_points % 2 == 1 else min_points + 1
    step_v = float(np.median(dv))
    points = int(round((width_mv / 1000.0) / step_v))
    points = max(min_points, points)
    if points % 2 == 0:
        points += 1
    max_window = len(v) if len(v) % 2 == 1 else len(v) - 1
    return max(1, min(points, max_window))


def _smooth_current_by_voltage(v, current, width_mv=FEATURE_SMOOTH_MV):
    """轻度稳健平滑：滚动中位数去毛刺，再做小窗口均值。无 scipy 依赖。"""
    current = np.asarray(current, dtype=float)
    if len(current) < 5:
        return current.copy(), 1
    window = _odd_window_from_voltage(v, width_mv, min_points=5)
    if window < 3:
        return current.copy(), window
    series = pd.Series(current)
    median_smoothed = series.rolling(window, center=True, min_periods=1).median()
    mean_window = max(3, window // 3)
    if mean_window % 2 == 0:
        mean_window += 1
    smoothed = median_smoothed.rolling(mean_window, center=True, min_periods=1).mean()
    return smoothed.to_numpy(dtype=float), window


def _robust_line_fit(x, y, sigma_clip=3.0, max_iter=5):
    """迭代 MAD 裁剪的一次直线拟合，返回 slope, intercept, R2。"""
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    valid = np.isfinite(x) & np.isfinite(y)
    x = x[valid]
    y = y[valid]
    if len(x) < 3:
        return np.nan, np.nan, np.nan

    keep = np.ones(len(x), dtype=bool)
    for _ in range(max_iter):
        if keep.sum() < 3:
            break
        slope, intercept = np.polyfit(x[keep], y[keep], 1)
        residual = y - (slope * x + intercept)
        center = float(np.median(residual[keep]))
        mad = float(np.median(np.abs(residual[keep] - center)))
        sigma = 1.4826 * mad
        if not np.isfinite(sigma) or sigma <= np.finfo(float).eps:
            break
        new_keep = np.abs(residual - center) <= sigma_clip * sigma
        if new_keep.sum() < max(3, int(0.5 * len(x))):
            break
        if np.array_equal(new_keep, keep):
            keep = new_keep
            break
        keep = new_keep

    slope, intercept = np.polyfit(x[keep], y[keep], 1)
    pred = slope * x[keep] + intercept
    ss_res = float(np.sum((y[keep] - pred) ** 2))
    ss_tot = float(np.sum((y[keep] - np.mean(y[keep])) ** 2))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else np.nan
    return float(slope), float(intercept), float(r2)


def _extract_forward_scan(df, mode):
    """
    根据实际 dV 方向提取去程扫描支，而不是只依赖全局最大/最小电压点。

    max: 目标方向 dV > 0；min: 目标方向 dV < 0。
    对起始小幅抖动设置容忍区，并以“持续反向扫描”识别真正换向点。
    返回 (branch, direction_fraction)。
    """
    clean = _clean_numeric_curve(df)
    if len(clean) < 20:
        raise ValueError('有效数值点不足 20 个')

    v = clean['Vf'].to_numpy(dtype=float)
    direction = 1.0 if mode == 'max' else -1.0
    dv = np.diff(v)
    abs_dv = np.abs(dv[np.isfinite(dv) & (np.abs(dv) > 0)])
    if len(abs_dv) == 0:
        raise ValueError('电压序列没有有效变化')

    step_v = float(np.median(abs_dv))
    tol = max(step_v * 0.15, 1e-8)
    signed_dv = direction * dv

    extreme_idx = int(np.argmax(v)) if mode == 'max' else int(np.argmin(v))
    full_span = float(direction * (v[extreme_idx] - v[0]))
    if not np.isfinite(full_span) or full_span <= 0:
        raise ValueError('无法识别目标方向的有效电压跨度')

    # 持续至少约 5 mV 的反向变化才视作真正回扫，避免把单点抖动误判为换向。
    reverse_run = max(3, int(round(0.005 / max(step_v, 1e-12))))
    reverse_run = min(reverse_run, 25)
    min_progress = min(max(0.05, 0.20 * full_span), 0.50 * full_span)

    vertex_idx = None
    for i in range(max(8, reverse_run), len(signed_dv) - reverse_run + 1):
        progress_i = float(direction * (v[i] - v[0]))
        if progress_i < min_progress:
            continue
        segment = signed_dv[i:i + reverse_run]
        if len(segment) >= reverse_run and np.all(segment < -tol):
            vertex_idx = i
            break

    if vertex_idx is None:
        vertex_idx = extreme_idx

    if vertex_idx < 10:
        raise ValueError('无法识别有效去程扫描支')

    branch = clean.iloc[:vertex_idx + 1].reset_index(drop=True)
    vb = branch['Vf'].to_numpy(dtype=float)
    dvb = np.diff(vb)
    moving = np.abs(dvb) > tol
    if moving.any():
        direction_fraction = float(np.mean(direction * dvb[moving] > 0))
    else:
        direction_fraction = 0.0

    return branch, direction_fraction


def _contiguous_true_groups(mask):
    """返回布尔数组中连续 True 的 [start, end] 索引。"""
    mask = np.asarray(mask, dtype=bool)
    groups = []
    i = 0
    n = len(mask)
    while i < n:
        if not mask[i]:
            i += 1
            continue
        j = i
        while j + 1 < n and mask[j + 1]:
            j += 1
        groups.append((i, j))
        i = j + 1
    return groups


def _tangent_onset(v, progress, reaction_signal, baseline_width_v, peak_idx):
    """
    用基线校正后的反应信号做辅助切线法：
    取主峰前、靠近主峰的 10%~40% 反应幅度区间拟合并求零交点。
    """
    if len(v) < 20 or peak_idx <= 5:
        return np.nan, np.nan
    y = np.asarray(reaction_signal, dtype=float)
    valid_search = (progress >= baseline_width_v) & (np.arange(len(v)) <= peak_idx)
    if not valid_search.any():
        return np.nan, np.nan

    max_signal = float(np.nanmax(y[valid_search]))
    if not np.isfinite(max_signal) or max_signal <= 0:
        return np.nan, np.nan

    low = FEATURE_TANGENT_LOW_FRAC * max_signal
    high = FEATURE_TANGENT_HIGH_FRAC * max_signal
    mask = valid_search & (y >= low) & (y <= high)
    groups = _contiguous_true_groups(mask)
    if not groups:
        return np.nan, np.nan

    # 选择离主峰最近且点数足够的连续区间，避免把早期肩峰和主氧化过程混在一起。
    groups = [(s, e) for s, e in groups if e - s + 1 >= 8]
    if not groups:
        return np.nan, np.nan
    s, e = groups[-1]

    xv = v[s:e + 1]
    yv = y[s:e + 1]
    slope, intercept, r2 = _robust_line_fit(xv, yv, sigma_clip=3.0, max_iter=3)
    if not np.isfinite(slope) or abs(slope) <= np.finfo(float).eps:
        return np.nan, r2
    onset = -intercept / slope

    v_lo = float(np.min(v))
    v_hi = float(np.max(v))
    if not (v_lo <= onset <= v_hi):
        return np.nan, r2
    return float(onset), float(r2)


def analyze_curve_features(df, mode):
    """
    分析单圈 CV 特征。

    - 去程扫描支：按 dV 方向与持续换向识别。
    - 峰位：在去除早期基线区后，于轻度平滑信号上寻找主峰候选；
      边界峰保留数值但标记 Boundary，内部肩峰标记 Review。
    - 起始电位：稳健线性基线 + MAD 噪声阈值 + 持续电压区间。
    - 切线法仅作为辅助校验，不强行替代主阈值法。
    """
    branch, direction_fraction = _extract_forward_scan(df, mode)
    v = branch['Vf'].to_numpy(dtype=float)
    current = branch['Im'].to_numpy(dtype=float)
    direction = 1.0 if mode == 'max' else -1.0
    progress = direction * (v - v[0])
    span_v = float(progress[-1] - progress[0])
    if not np.isfinite(span_v) or span_v <= 0:
        raise ValueError('去程扫描电压跨度无效')

    smooth_current, smooth_points = _smooth_current_by_voltage(v, current, FEATURE_SMOOTH_MV)

    baseline_width_v = FEATURE_BASELINE_FRACTION * span_v
    baseline_width_v = max(FEATURE_BASELINE_MIN_MV / 1000.0, baseline_width_v)
    baseline_width_v = min(FEATURE_BASELINE_MAX_MV / 1000.0, baseline_width_v)
    baseline_width_v = min(baseline_width_v, 0.40 * span_v)
    baseline_mask = progress <= baseline_width_v
    if baseline_mask.sum() < 20:
        baseline_mask[:min(len(v), 20)] = True

    base_slope, base_intercept, base_r2 = _robust_line_fit(
        v[baseline_mask], current[baseline_mask], sigma_clip=3.0, max_iter=5
    )
    if not np.isfinite(base_slope):
        raise ValueError('基线拟合失败')

    baseline = base_slope * v + base_intercept
    raw_reaction = direction * (current - baseline)
    reaction = direction * (smooth_current - baseline)

    base_residual = raw_reaction[baseline_mask]
    residual_center = float(np.median(base_residual))
    residual_mad = float(np.median(np.abs(base_residual - residual_center)))
    noise_sigma = 1.4826 * residual_mad
    if not np.isfinite(noise_sigma) or noise_sigma <= np.finfo(float).eps:
        noise_sigma = float(np.std(base_residual))
    if not np.isfinite(noise_sigma) or noise_sigma <= np.finfo(float).eps:
        noise_sigma = max(float(np.ptp(base_residual)) / 6.0, np.finfo(float).eps)

    onset_threshold = residual_center + FEATURE_ONSET_SIGMA * noise_sigma

    # 峰位候选：排除起始基线区，减少 OCP 瞬态/量程切换对全局极值的干扰。
    transformed_smooth = direction * smooth_current
    search_idx = np.where(progress >= baseline_width_v)[0]
    if len(search_idx) < 5:
        search_idx = np.arange(len(v))
    local_peak_pos = int(np.nanargmax(transformed_smooth[search_idx]))
    peak_idx = int(search_idx[local_peak_pos])

    peak_signal = float(reaction[peak_idx])
    peak_v = float(v[peak_idx])
    peak_i = float(current[peak_idx])
    distance_to_end_mv = float(max(0.0, progress[-1] - progress[peak_idx]) * 1000.0)

    if not np.isfinite(peak_signal) or peak_signal <= max(3.0 * noise_sigma, onset_threshold):
        peak_status = QCStatus.FAILED.value
        peak_v = np.nan
        peak_i = np.nan
    elif distance_to_end_mv <= FEATURE_BOUNDARY_MV:
        peak_status = QCStatus.BOUNDARY.value
    else:
        post = transformed_smooth[peak_idx:]
        decline = float(transformed_smooth[peak_idx] - np.nanmin(post)) if len(post) else 0.0
        required_decline = max(
            3.0 * noise_sigma,
            0.05 * max(abs(transformed_smooth[peak_idx]), np.finfo(float).eps)
        )
        peak_status = QCStatus.OK.value if decline >= required_decline else QCStatus.REVIEW.value

    # 主 onset：找超过阈值并持续至少指定电压宽度的反应区。
    cond = (reaction > onset_threshold) & (progress >= baseline_width_v)
    groups = _contiguous_true_groups(cond)
    persist_v = FEATURE_ONSET_PERSIST_MV / 1000.0
    valid_groups = []
    for start, end in groups:
        if end <= start:
            continue
        if progress[end] - progress[start] >= persist_v:
            valid_groups.append((start, end))

    onset_idx = None
    if valid_groups:
        # 选择主峰之前、最靠近主峰的持续反应区；若峰失败则选最后一个有效区。
        if np.isfinite(peak_v):
            candidates = [(start, end) for start, end in valid_groups if start <= peak_idx]
            if candidates:
                onset_idx = candidates[-1][0]
        if onset_idx is None:
            onset_idx = valid_groups[-1][0]

    onset_primary = float(v[onset_idx]) if onset_idx is not None else np.nan

    tangent_peak_idx = peak_idx if np.isfinite(peak_v) else len(v) - 1
    onset_tangent, tangent_r2 = _tangent_onset(
        v, progress, reaction, baseline_width_v, tangent_peak_idx
    )
    tangent_valid = (
        np.isfinite(onset_tangent)
        and np.isfinite(tangent_r2)
        and tangent_r2 >= FEATURE_TANGENT_R2_MIN
    )

    # v1.8：不再生成“最终采用的 onset”。阈值法与切线法作为两套并行结果输出。
    threshold_qc = QCStatus.OK.value if np.isfinite(onset_primary) else QCStatus.FAILED.value
    if np.isfinite(onset_tangent) and np.isfinite(tangent_r2):
        tangent_qc = QCStatus.OK.value if tangent_r2 >= FEATURE_TANGENT_R2_MIN else QCStatus.REVIEW.value
    else:
        tangent_qc = QCStatus.FAILED.value

    if np.isfinite(onset_primary) and np.isfinite(onset_tangent):
        onset_difference_mv = abs(onset_primary - onset_tangent) * 1000.0
    else:
        onset_difference_mv = np.nan

    if direction_fraction >= 0.95:
        scan_qc = QCStatus.OK.value
    elif direction_fraction >= 0.80:
        scan_qc = QCStatus.REVIEW.value
    else:
        scan_qc = QCStatus.FAILED.value

    tangent_idx = None
    if np.isfinite(onset_tangent):
        tangent_idx = int(np.nanargmin(np.abs(v - onset_tangent)))

    verification = pd.DataFrame({
        'Vf': v,
        'Im_raw': current,
        'Im_smooth': smooth_current,
        'I_baseline': baseline,
        'Reaction_signal': reaction,
        'Onset_threshold': np.full(len(v), onset_threshold, dtype=float),
        'Is_Onset_Threshold': np.arange(len(v)) == onset_idx if onset_idx is not None else np.zeros(len(v), dtype=bool),
        'Is_Onset_Tangent': np.arange(len(v)) == tangent_idx if tangent_idx is not None else np.zeros(len(v), dtype=bool),
        'Is_Peak': np.arange(len(v)) == peak_idx if np.isfinite(peak_v) else np.zeros(len(v), dtype=bool),
    })

    return {
        'E_peak (V)': peak_v,
        'I_peak (A)': peak_i,
        'Peak_status': peak_status,
        'E_onset_threshold (V)': onset_primary,
        'Threshold_QC': threshold_qc,
        'E_onset_tangent (V)': onset_tangent if np.isfinite(onset_tangent) else np.nan,
        'Tangent_QC': tangent_qc,
        'Onset_tangent_R2': tangent_r2 if np.isfinite(tangent_r2) else np.nan,
        'Onset_difference (mV)': onset_difference_mv,
        'Scan_direction_fraction': direction_fraction,
        'Scan_QC': scan_qc,
        'Baseline_R2': base_r2,
        'Noise_sigma (A)': noise_sigma,
        'Smooth_window_points': int(smooth_points),
    }, verification


def analyze_cv_features(curves, mode):
    """分析全部有效原始 CURVE；Threshold 与 Tangent 两种 onset 方法独立输出。"""
    rows = []
    verification = {}

    def curve_number(name):
        m = re.search(r'(\d+)$', str(name))
        return int(m.group(1)) if m else 10**9

    for name in sorted(curves, key=curve_number):
        df = curves[name]
        try:
            clean = _clean_numeric_curve(df)
        except Exception:
            clean = pd.DataFrame()
        # Gamry 文件末尾可能带有仅 1 个点的占位 CURVE，不计为有效循环。
        if len(clean) < 20:
            log_warning(f'曲线 {name} 数据点不足 20，视为无效占位曲线并跳过')
            continue
        try:
            result, verify_df = analyze_curve_features(clean, mode)
            result['Curve'] = name
            rows.append(result)
            verification[name] = verify_df
        except Exception as exc:
            log_warning(f'曲线 {name} 特征电位分析失败：{exc}')
            rows.append({
                'Curve': name,
                'E_peak (V)': np.nan,
                'I_peak (A)': np.nan,
                'Peak_status': QCStatus.FAILED.value,
                'E_onset_threshold (V)': np.nan,
                'Threshold_QC': QCStatus.FAILED.value,
                'E_onset_tangent (V)': np.nan,
                'Tangent_QC': QCStatus.FAILED.value,
                'Onset_tangent_R2': np.nan,
                'Onset_difference (mV)': np.nan,
                'Scan_direction_fraction': np.nan,
                'Scan_QC': QCStatus.FAILED.value,
                'Baseline_R2': np.nan,
                'Noise_sigma (A)': np.nan,
                'Smooth_window_points': np.nan,
            })

    if not rows:
        log_warning('未生成任何特征电位结果')
        return pd.DataFrame(), verification

    feature_df = pd.DataFrame(rows)
    feature_df['_curve_no'] = feature_df['Curve'].map(curve_number)
    feature_df = feature_df.sort_values('_curve_no').drop(columns=['_curve_no']).reset_index(drop=True)

    # Reference 只定义“参考圈”，不要求某种 onset 方法必须有效；各方法分别计算位移。
    if (feature_df['Curve'] == 'CURVE1').any():
        ref_row = feature_df.loc[feature_df['Curve'] == 'CURVE1'].iloc[0]
    else:
        ref_row = feature_df.iloc[0]

    reference_curve = str(ref_row['Curve'])
    peak_ref = pd.to_numeric(pd.Series([ref_row.get('E_peak (V)')]), errors='coerce').iloc[0]
    threshold_ref = pd.to_numeric(pd.Series([ref_row.get('E_onset_threshold (V)')]), errors='coerce').iloc[0]
    tangent_ref = pd.to_numeric(pd.Series([ref_row.get('E_onset_tangent (V)')]), errors='coerce').iloc[0]

    feature_df['Peak_shift_vs_ref (mV)'] = (
        (pd.to_numeric(feature_df['E_peak (V)'], errors='coerce') - peak_ref) * 1000.0
        if np.isfinite(peak_ref) else np.nan
    )
    feature_df['Onset_threshold_shift_vs_ref (mV)'] = (
        (pd.to_numeric(feature_df['E_onset_threshold (V)'], errors='coerce') - threshold_ref) * 1000.0
        if np.isfinite(threshold_ref) else np.nan
    )
    feature_df['Onset_tangent_shift_vs_ref (mV)'] = (
        (pd.to_numeric(feature_df['E_onset_tangent (V)'], errors='coerce') - tangent_ref) * 1000.0
        if np.isfinite(tangent_ref) else np.nan
    )
    feature_df['Reference_curve'] = reference_curve

    if mode == 'max':
        rename_map = {
            'E_peak (V)': 'E_ox_peak (V)',
            'I_peak (A)': 'I_ox_peak (A)',
            'E_onset_threshold (V)': 'E_onset_ox_threshold (V)',
            'E_onset_tangent (V)': 'E_onset_ox_tangent (V)',
            'Peak_shift_vs_ref (mV)': 'Ox_peak_shift_vs_ref (mV)',
            'Onset_threshold_shift_vs_ref (mV)': 'Ox_onset_threshold_shift_vs_ref (mV)',
            'Onset_tangent_shift_vs_ref (mV)': 'Ox_onset_tangent_shift_vs_ref (mV)',
        }
    else:
        rename_map = {
            'E_peak (V)': 'E_red_peak (V)',
            'I_peak (A)': 'I_red_peak (A)',
            'E_onset_threshold (V)': 'E_onset_red_threshold (V)',
            'E_onset_tangent (V)': 'E_onset_red_tangent (V)',
            'Peak_shift_vs_ref (mV)': 'Red_peak_shift_vs_ref (mV)',
            'Onset_threshold_shift_vs_ref (mV)': 'Red_onset_threshold_shift_vs_ref (mV)',
            'Onset_tangent_shift_vs_ref (mV)': 'Red_onset_tangent_shift_vs_ref (mV)',
        }
    return feature_df.rename(columns=rename_map), verification
def generate_auto_indices(total_curves, target_count=5):
    """自动生成均匀分布的圈号，包含首尾"""
    if total_curves <= target_count:
        return list(range(1, total_curves+1))
    indices = []
    indices.append(1)
    if target_count > 2:
        step = (total_curves - 1) / (target_count - 1)
        for i in range(1, target_count - 1):
            idx = int(round(1 + i * step))
            if idx not in indices:
                indices.append(idx)
    indices.append(total_curves)
    indices = sorted(set(indices))
    return indices
