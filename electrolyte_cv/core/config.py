from __future__ import annotations

from enum import Enum

class QCStatus(str, Enum):
    OK = "OK"
    REVIEW = "Review"
    BOUNDARY = "Boundary"
    FAILED = "Failed"


class MessageLevel(str, Enum):
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"


class ScanMode(str, Enum):
    MAX = "max"
    MIN = "min"

    @property
    def cn(self):
        return "氧化" if self == ScanMode.MAX else "还原"

    @property
    def en(self):
        return "Oxidation" if self == ScanMode.MAX else "Reduction"

    @property
    def display(self):
        return f"{self.cn} / {'Max' if self == ScanMode.MAX else 'Min'}"


STATUS_COLORS = {
    QCStatus.OK.value: "#3A8F62",
    QCStatus.REVIEW.value: "#C58A26",
    QCStatus.BOUNDARY.value: "#7867C9",
    QCStatus.FAILED.value: "#C65050",
}

TEXT = {
    "reference_changed": "参考圈已更改为 {reference}，位移结果已重新计算。",
    "curve_located": "已定位到 {curve}，请检查峰值和起始电位标记。",
}

# ================== 配置常量 ==================
SUPPORTED_EXTENSIONS = ('.dta', '.txt', '.xlsx', '.xls')
DEFAULT_MODE = 'max'
DEFAULT_SCAN_RATE_MV = 5
DEFAULT_PRECISION_MV = 5

# 特征电位分析默认参数（以电压宽度而不是固定点数定义，适配不同采样密度）
FEATURE_SMOOTH_MV = 15.0
FEATURE_BASELINE_FRACTION = 0.20
FEATURE_BASELINE_MIN_MV = 150.0
FEATURE_BASELINE_MAX_MV = 450.0
FEATURE_ONSET_SIGMA = 5.0
FEATURE_ONSET_PERSIST_MV = 15.0
FEATURE_TANGENT_LOW_FRAC = 0.10
FEATURE_TANGENT_HIGH_FRAC = 0.40
FEATURE_TANGENT_R2_MIN = 0.98
FEATURE_ONSET_QC_TOL_MV = 50.0
FEATURE_BOUNDARY_MV = 30.0

# 不同模式下电压默认值 (单位: V)
DEFAULT_VOLTAGE = {
    'max': {'start': 2.7, 'end': 4.5},
    'min': {'start': 3.0, 'end': 0.01}
}

# 手动模式预设方案（圈号列表）
PRESET_SCHEMES = {
    "十圈选点": [1, 3, 5, 7, 10],
    "二十圈选点": [1, 5, 10, 15, 20],
    "五十圈选点": [1, 10, 20, 30, 40, 50],
    "自定义": None
}

EN_HEADERS = {
    'Curve': 'Curve',
    'Q1 (C)': 'Q1 (C)',
    'Q2 (C)': 'Q2 (C)',
    'Q_ox (C)': 'Q_ox (C)',
    'Q_red (C)': 'Q_red (C)',
    'A1 (A·V)': 'A1 (A·V)',
    'A2 (A·V)': 'A2 (A·V)',
    'A_total (A·V)': 'A_total (A·V)',
    'V_start_Part1': 'V_start_Part1 (V)',
    'V_end_Part1': 'V_end_Part1 (V)',
    'V_start_Part2': 'V_start_Part2 (V)',
    'V_end_Part2': 'V_end_Part2 (V)',
    'E_ox_peak (V)': 'E_ox_peak (V)',
    'I_ox_peak (A)': 'I_ox_peak (A)',
    'E_red_peak (V)': 'E_red_peak (V)',
    'I_red_peak (A)': 'I_red_peak (A)',
    'E_onset_ox_threshold (V)': 'E_onset_ox_threshold (V)',
    'E_onset_ox_tangent (V)': 'E_onset_ox_tangent (V)',
    'E_onset_red_threshold (V)': 'E_onset_red_threshold (V)',
    'E_onset_red_tangent (V)': 'E_onset_red_tangent (V)',
    'Ox_peak_shift_vs_ref (mV)': 'Ox_peak_shift_vs_ref (mV)',
    'Ox_onset_threshold_shift_vs_ref (mV)': 'Ox_onset_threshold_shift_vs_ref (mV)',
    'Ox_onset_tangent_shift_vs_ref (mV)': 'Ox_onset_tangent_shift_vs_ref (mV)',
    'Red_peak_shift_vs_ref (mV)': 'Red_peak_shift_vs_ref (mV)',
    'Red_onset_threshold_shift_vs_ref (mV)': 'Red_onset_threshold_shift_vs_ref (mV)',
    'Red_onset_tangent_shift_vs_ref (mV)': 'Red_onset_tangent_shift_vs_ref (mV)',
    'Reference_curve': 'Reference_curve',
    'Peak_status': 'Peak_status',
    'Threshold_QC': 'Threshold_QC',
    'Tangent_QC': 'Tangent_QC',
    'Scan_QC': 'Scan_QC',
    'Scan_direction_fraction': 'Scan_direction_fraction',
    'Onset_difference (mV)': 'Onset_difference (mV)',
    'Onset_tangent_R2': 'Onset_tangent_R2',
    'Baseline_R2': 'Baseline_R2',
    'Noise_sigma (A)': 'Noise_sigma (A)',
    'Smooth_window_points': 'Smooth_window_points',
}

CN_HEADERS = {
    'Curve': '曲线/循环编号',
    'Q1 (C)': '第一积分区电荷量 (C)',
    'Q2 (C)': '第二积分区电荷量 (C)',
    'Q_ox (C)': '总氧化电荷量 (C)',
    'Q_red (C)': '总还原电荷量 (C)',
    'A1 (A·V)': '第一积分区面积 (A·V)',
    'A2 (A·V)': '第二积分区面积 (A·V)',
    'A_total (A·V)': '总积分面积 (A·V)',
    'V_start_Part1': '第一积分区起始电位 (V)',
    'V_end_Part1': '第一积分区终止电位 (V)',
    'V_start_Part2': '第二积分区起始电位 (V)',
    'V_end_Part2': '第二积分区终止电位 (V)',
    'E_ox_peak (V)': '氧化峰电位 (V)',
    'I_ox_peak (A)': '氧化峰电流 (A)',
    'E_red_peak (V)': '还原峰电位 (V)',
    'I_red_peak (A)': '还原峰电流 (A)',
    'E_onset_ox_threshold (V)': '阈值法起始氧化电位 (V)',
    'E_onset_ox_tangent (V)': '切线法起始氧化电位 (V)',
    'E_onset_red_threshold (V)': '阈值法起始还原电位 (V)',
    'E_onset_red_tangent (V)': '切线法起始还原电位 (V)',
    'Ox_peak_shift_vs_ref (mV)': '氧化峰电位相对参考圈位移 (mV)',
    'Ox_onset_threshold_shift_vs_ref (mV)': '阈值法起始氧化电位相对参考圈位移 (mV)',
    'Ox_onset_tangent_shift_vs_ref (mV)': '切线法起始氧化电位相对参考圈位移 (mV)',
    'Red_peak_shift_vs_ref (mV)': '还原峰电位相对参考圈位移 (mV)',
    'Red_onset_threshold_shift_vs_ref (mV)': '阈值法起始还原电位相对参考圈位移 (mV)',
    'Red_onset_tangent_shift_vs_ref (mV)': '切线法起始还原电位相对参考圈位移 (mV)',
    'Reference_curve': '参考曲线/参考循环',
    'Peak_status': '峰识别状态',
    'Threshold_QC': '阈值法起始电位质量评价',
    'Tangent_QC': '切线法起始电位质量评价',
    'Scan_QC': '扫描方向质量评价',
    'Scan_direction_fraction': '扫描方向有效比例',
    'Onset_difference (mV)': '两种起始电位方法差值 (mV)',
    'Onset_tangent_R2': '起始电位切线拟合 R²',
    'Baseline_R2': '基线拟合 R²',
    'Noise_sigma (A)': '基线噪声水平 (A)',
    'Smooth_window_points': '实际平滑窗口点数',
}

QC_TOOLTIPS = {
    "Threshold_QC": "Threshold QC / 阈值法质量评价\n判断阈值法是否获得了可靠的起始电位。",
    "Tangent_QC": "Tangent QC / 切线法质量评价\n结合切线交点与拟合 R² 判断切线法结果质量。",
    "Scan_direction_fraction": "Scan direction fraction / 扫描方向有效比例\n表示目标扫描方向占提取扫描支的比例，越接近 1 越完整。",
    "Baseline_R2": "Baseline R² / 基线拟合决定系数\n用于评价起始电位分析中的基线拟合程度。",
    "Noise_sigma (A)": "Noise sigma / 基线噪声水平\n由基线残差的稳健统计量估计，用于构建起始电位阈值。",
    "Onset_difference (mV)": "Onset difference / 起始电位方法差值\n阈值法与切线法结果之间的差异。",
    "Onset_tangent_R2": "Tangent R² / 切线区拟合决定系数\n用于评价切线法的拟合质量。",
    "Smooth_window_points": "Smooth window points / 平滑窗口点数\n记录本圈特征识别时实际采用的平滑窗口长度。",
}
