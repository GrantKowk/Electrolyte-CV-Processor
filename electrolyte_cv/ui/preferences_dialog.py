from __future__ import annotations

import copy

from .qt_compat import *
from ..core.config import PRESET_SCHEMES, QCStatus
from ..settings_manager import normalize_profile

require_qt()

TAB_LABELS = {
    "cv": "CV曲线",
    "charge": "库仑电荷",
    "peak": "峰电位",
    "onset": "起始电位",
    "shift": "位移",
    "qc": "QC",
}


class PreferencesDialog(QDialog):
    """User-editable global defaults. It never stores file/data-session state."""

    def __init__(self, profile, parent=None):
        super().__init__(parent)
        self.setWindowTitle("首选项")
        self.resize(720, 650)
        self._base = normalize_profile(profile)
        root = QVBoxLayout(self)
        self.tabs = QTabWidget()
        root.addWidget(self.tabs, 1)
        self._build_startup_tab()
        self._build_analysis_tab()
        self._build_output_tab()
        self._build_display_tab()
        buttons = QHBoxLayout()
        buttons.addStretch(1)
        cancel = QPushButton("取消"); ok = QPushButton("确定"); ok.setDefault(True)
        cancel.clicked.connect(self.reject); ok.clicked.connect(self.accept)
        buttons.addWidget(cancel); buttons.addWidget(ok); root.addLayout(buttons)
        self._load(self._base)

    def _page(self, title):
        page = QWidget(); lay = QVBoxLayout(page); lay.setContentsMargins(16, 14, 16, 14); lay.setSpacing(12)
        self.tabs.addTab(page, title)
        return lay

    @staticmethod
    def _group(title, layout):
        box = QGroupBox(title); form = QFormLayout(box); form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        layout.addWidget(box); return form

    def _build_startup_tab(self):
        lay = self._page("启动与界面")
        form = self._group("启动", lay)
        self.startup_behavior = QComboBox(); self.startup_behavior.addItem("使用我保存的默认配置", "defaults"); self.startup_behavior.addItem("恢复上次退出状态", "last_session")
        self.default_tab = QComboBox()
        for key, label in TAB_LABELS.items(): self.default_tab.addItem(label, key)
        self.theme_combo = QComboBox(); self.theme_combo.addItem("浅色主题", "light"); self.theme_combo.addItem("深色主题", "dark")
        self.log_expanded = QCheckBox("启动时展开运行日志")
        form.addRow("启动行为", self.startup_behavior); form.addRow("默认启动页", self.default_tab); form.addRow("主题", self.theme_combo); form.addRow("运行日志", self.log_expanded)
        lay.addStretch(1)

    def _build_analysis_tab(self):
        lay = self._page("分析参数")
        form = self._group("默认分析参数", lay)
        self.mode_combo = QComboBox(); self.mode_combo.addItem("氧化 / Max", "max"); self.mode_combo.addItem("还原 / Min", "min")
        self.start_voltage = QDoubleSpinBox(); self.end_voltage = QDoubleSpinBox()
        for sp in (self.start_voltage, self.end_voltage): sp.setRange(-20, 20); sp.setDecimals(4); sp.setSingleStep(0.01); sp.setSuffix(" V")
        self.scan_rate = QDoubleSpinBox(); self.scan_rate.setRange(0.0001, 10000); self.scan_rate.setDecimals(4); self.scan_rate.setSuffix(" mV/s")
        self.precision = QDoubleSpinBox(); self.precision.setRange(0.1, 100); self.precision.setDecimals(2); self.precision.setSuffix(" mV")
        form.addRow("分析模式", self.mode_combo); form.addRow("起始电压", self.start_voltage); form.addRow("终止电压", self.end_voltage); form.addRow("扫描速率", self.scan_rate); form.addRow("切分精度", self.precision)
        lay.addStretch(1)

    def _build_output_tab(self):
        lay = self._page("结果输出")
        form = self._group("默认结果输出", lay)
        self.selection_mode = QComboBox(); self.selection_mode.addItem("自动", "auto"); self.selection_mode.addItem("手动", "manual")
        self.auto_target = QSpinBox(); self.auto_target.setRange(1, 100)
        self.preset = QComboBox(); self.preset.addItems(list(PRESET_SCHEMES.keys()))
        self.manual_cycles = QLineEdit()
        self.cut_only = QCheckBox("仅输出指定圈"); self.verify_file = QCheckBox("生成验证文件")
        self.original_dir = QCheckBox("输出至原文件目录")
        path_row = QWidget(); pr = QHBoxLayout(path_row); pr.setContentsMargins(0,0,0,0)
        self.custom_dir = QLineEdit(); browse = QPushButton("浏览..."); browse.clicked.connect(self._browse_dir); pr.addWidget(self.custom_dir,1); pr.addWidget(browse)
        form.addRow("输出循环", self.selection_mode); form.addRow("自动目标圈数", self.auto_target); form.addRow("预设", self.preset); form.addRow("手动圈数", self.manual_cycles); form.addRow("指定圈", self.cut_only); form.addRow("验证文件", self.verify_file); form.addRow("输出位置", self.original_dir); form.addRow("自定义目录", path_row)
        self.original_dir.toggled.connect(lambda checked: self.custom_dir.setEnabled(not checked))
        lay.addStretch(1)

    def _build_display_tab(self):
        lay = self._page("图像显示")
        scroll = QScrollArea(); scroll.setWidgetResizable(True); scroll.setFrameShape(QFrame.Shape.NoFrame)
        holder = QWidget(); v = QVBoxLayout(holder); v.setContentsMargins(0,0,8,0); v.setSpacing(10); scroll.setWidget(holder); lay.addWidget(scroll,1)

        cv = self._group("CV", v)
        self.cv_curve = QComboBox(); self.cv_curve.addItem("原始", "raw"); self.cv_curve.addItem("平滑", "smooth"); self.cv_curve.addItem("原始+平滑", "both")
        self.cv_scan = QComboBox(); self.cv_scan.addItem("分析扫描支", "analysis"); self.cv_scan.addItem("完整CV", "full")
        self.cv_peak = QCheckBox("峰电位"); self.cv_threshold = QCheckBox("Threshold Onset"); self.cv_tangent = QCheckBox("Tangent Onset"); self.cv_legend = QCheckBox("图例")
        cv.addRow("曲线", self.cv_curve); cv.addRow("扫描", self.cv_scan); cv.addRow(self.cv_peak); cv.addRow(self.cv_threshold); cv.addRow(self.cv_tangent); cv.addRow(self.cv_legend)

        charge = self._group("库仑电荷", v)
        self.charge_style = QComboBox(); self.charge_style.addItem("柱状图", "bar"); self.charge_style.addItem("趋势线", "line")
        self.charge_labels = QCheckBox("数据标签"); self.charge_table = QCheckBox("数据表")
        charge.addRow("显示方式", self.charge_style); charge.addRow(self.charge_labels); charge.addRow(self.charge_table)

        peak = self._group("峰电位", v)
        self.peak_metric = QComboBox(); self.peak_metric.addItem("峰电位", "potential"); self.peak_metric.addItem("峰电流", "current")
        self.peak_labels = QCheckBox("数据标签"); self.peak_table = QCheckBox("数据表")
        peak.addRow("显示指标", self.peak_metric); peak.addRow(self.peak_labels); peak.addRow(self.peak_table)

        onset = self._group("起始电位", v)
        self.onset_threshold = QCheckBox("Threshold"); self.onset_tangent = QCheckBox("Tangent"); self.onset_labels = QCheckBox("数据标签"); self.onset_table = QCheckBox("数据表")
        for w in (self.onset_threshold,self.onset_tangent,self.onset_labels,self.onset_table): onset.addRow(w)

        shift = self._group("位移", v)
        self.shift_peak = QCheckBox("峰电位位移"); self.shift_threshold = QCheckBox("Threshold Onset 位移"); self.shift_tangent = QCheckBox("Tangent Onset 位移"); self.shift_zero = QCheckBox("ΔE=0 参考线"); self.shift_labels = QCheckBox("数据标签"); self.shift_table = QCheckBox("数据表")
        for w in (self.shift_peak,self.shift_threshold,self.shift_tangent,self.shift_zero,self.shift_labels,self.shift_table): shift.addRow(w)

        qc = self._group("QC", v)
        self.qc_ok = QCheckBox(QCStatus.OK.value); self.qc_review = QCheckBox(QCStatus.REVIEW.value); self.qc_boundary = QCheckBox(QCStatus.BOUNDARY.value); self.qc_failed = QCheckBox(QCStatus.FAILED.value); self.qc_only = QCheckBox("仅显示需要检查/异常")
        for w in (self.qc_ok,self.qc_review,self.qc_boundary,self.qc_failed,self.qc_only): qc.addRow(w)
        v.addStretch(1)

    @staticmethod
    def _set_combo(combo, data):
        idx = combo.findData(data)
        if idx >= 0: combo.setCurrentIndex(idx)

    def _load(self, p):
        self._set_combo(self.startup_behavior, p["startup_behavior"]); self._set_combo(self.default_tab, p["default_tab"]); self._set_combo(self.theme_combo, p["theme"]); self.log_expanded.setChecked(bool(p["log_expanded"]))
        a=p["analysis"]; self._set_combo(self.mode_combo,a["mode"]); self.start_voltage.setValue(float(a["start_voltage"])); self.end_voltage.setValue(float(a["end_voltage"])); self.scan_rate.setValue(float(a["scan_rate_mv"])); self.precision.setValue(float(a["precision_mv"]))
        o=p["output"]; self._set_combo(self.selection_mode,o["selection_mode"]); self.auto_target.setValue(int(o["auto_target"])); self.preset.setCurrentText(str(o["preset"])); self.manual_cycles.setText(str(o["manual_cycles"])); self.cut_only.setChecked(bool(o["cut_only"])); self.verify_file.setChecked(bool(o["verify_file"])); self.original_dir.setChecked(bool(o["original_dir"])); self.custom_dir.setText(str(o["custom_dir"])); self.custom_dir.setEnabled(not self.original_dir.isChecked())
        d=p["display"]; c=d["cv"]; self._set_combo(self.cv_curve,c["curve"]); self._set_combo(self.cv_scan,c["scan"]); self.cv_peak.setChecked(c["peak"]); self.cv_threshold.setChecked(c["threshold_onset"]); self.cv_tangent.setChecked(c["tangent_onset"]); self.cv_legend.setChecked(c["legend"])
        c=d["charge"]; self._set_combo(self.charge_style,c["style"]); self.charge_labels.setChecked(c["labels"]); self.charge_table.setChecked(c["table"])
        c=d["peak"]; self._set_combo(self.peak_metric,c["metric"]); self.peak_labels.setChecked(c["labels"]); self.peak_table.setChecked(c["table"])
        c=d["onset"]; self.onset_threshold.setChecked(c["threshold"]); self.onset_tangent.setChecked(c["tangent"]); self.onset_labels.setChecked(c["labels"]); self.onset_table.setChecked(c["table"])
        c=d["shift"]; self.shift_peak.setChecked(c["peak"]); self.shift_threshold.setChecked(c["threshold"]); self.shift_tangent.setChecked(c["tangent"]); self.shift_zero.setChecked(c["zero_line"]); self.shift_labels.setChecked(c["labels"]); self.shift_table.setChecked(c["table"])
        c=d["qc"]; self.qc_ok.setChecked(c["status_ok"]); self.qc_review.setChecked(c["status_review"]); self.qc_boundary.setChecked(c["status_boundary"]); self.qc_failed.setChecked(c["status_failed"]); self.qc_only.setChecked(c["only_abnormal"])

    def _browse_dir(self):
        path = QFileDialog.getExistingDirectory(self, "选择默认输出目录", self.custom_dir.text())
        if path: self.custom_dir.setText(path)

    def profile(self):
        p=copy.deepcopy(self._base)
        p["startup_behavior"]=self.startup_behavior.currentData(); p["default_tab"]=self.default_tab.currentData(); p["theme"]=self.theme_combo.currentData(); p["log_expanded"]=self.log_expanded.isChecked()
        p["analysis"]={"mode":self.mode_combo.currentData(),"start_voltage":self.start_voltage.value(),"end_voltage":self.end_voltage.value(),"scan_rate_mv":self.scan_rate.value(),"precision_mv":self.precision.value()}
        p["output"]={"selection_mode":self.selection_mode.currentData(),"auto_target":self.auto_target.value(),"preset":self.preset.currentText(),"manual_cycles":self.manual_cycles.text().strip(),"cut_only":self.cut_only.isChecked(),"verify_file":self.verify_file.isChecked(),"original_dir":self.original_dir.isChecked(),"custom_dir":self.custom_dir.text().strip()}
        p["display"]={
            "cv":{"curve":self.cv_curve.currentData(),"scan":self.cv_scan.currentData(),"peak":self.cv_peak.isChecked(),"threshold_onset":self.cv_threshold.isChecked(),"tangent_onset":self.cv_tangent.isChecked(),"legend":self.cv_legend.isChecked()},
            "charge":{"style":self.charge_style.currentData(),"labels":self.charge_labels.isChecked(),"table":self.charge_table.isChecked()},
            "peak":{"metric":self.peak_metric.currentData(),"labels":self.peak_labels.isChecked(),"table":self.peak_table.isChecked()},
            "onset":{"threshold":self.onset_threshold.isChecked(),"tangent":self.onset_tangent.isChecked(),"labels":self.onset_labels.isChecked(),"table":self.onset_table.isChecked()},
            "shift":{"peak":self.shift_peak.isChecked(),"threshold":self.shift_threshold.isChecked(),"tangent":self.shift_tangent.isChecked(),"zero_line":self.shift_zero.isChecked(),"labels":self.shift_labels.isChecked(),"table":self.shift_table.isChecked()},
            "qc":{"status_ok":self.qc_ok.isChecked(),"status_review":self.qc_review.isChecked(),"status_boundary":self.qc_boundary.isChecked(),"status_failed":self.qc_failed.isChecked(),"only_abnormal":self.qc_only.isChecked()},
        }
        return normalize_profile(p)
