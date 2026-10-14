from __future__ import annotations

import re
import traceback
from enum import Enum
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional

import numpy as np
import pandas as pd
from matplotlib.lines import Line2D

from .qt_compat import *
from .styles import LIGHT_STYLE, DARK_STYLE, V19_LIGHT_STYLE, V19_DARK_STYLE
from .widgets import (
    MATPLOTLIB_FONT, ModernCheckBox, ModernRadioButton, NoWheelDoubleSpinBox,
    NoWheelSpinBox, NoWheelComboBox, apply_card_shadow, DropFileList, MplPanel,
    CycleSelectorDialog, ProcessingWorker, CopyableTableWidget,
)
from ..core.config import *
from ..core.formatting import *
from ..core.parsers import parse_txt_to_curves, parse_excel_to_curves
from ..core.analysis import _clean_numeric_curve, _extract_forward_scan, _smooth_current_by_voltage
from ..core.cv_plot_pipeline import prepare_cv_curve_for_plot, build_cv_marker_positions
from ..core.plot_helpers import build_onset_label_items
from ..settings_manager import SettingsManager, normalize_profile
from .preferences_dialog import PreferencesDialog

require_qt()

class CVQtMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Electrolyte CV Processor v2.0")
        self.resize(1580, 920)
        self.setMinimumSize(1220, 760)
        self.file_paths = []
        self.analysis_cache = {}
        self.raw_curve_cache = {}
        self.mode_cache = {}
        self.default_selection_cache = {}
        self.preview_selection_cache = {}
        self.current_preview_path = None
        self.current_focus_curve = None
        self.worker = None
        self.theme = "light"
        self.common_file_combos = []
        self.common_cycle_buttons = []
        self.common_mode_labels = []
        self.common_count_labels = []
        self.table_map = {}
        self.plot_map = {}
        self._building_common = False
        self._build_ui()
        self._build_menu()
        self._apply_defaults()
        self.statusBar().showMessage("就绪。请添加 .DTA / .txt / .xlsx 文件。")

    # ------------------------------------------------------------- helpers
    @staticmethod
    def curve_no(name):
        m = re.search(r"(\d+)$", str(name))
        return int(m.group(1)) if m else 10**9

    def mode_columns(self, mode):
        if mode == "max":
            return {
                "peak": "E_ox_peak (V)", "current": "I_ox_peak (A)",
                "threshold": "E_onset_ox_threshold (V)",
                "tangent": "E_onset_ox_tangent (V)",
                "peak_shift": "Ox_peak_shift_vs_ref (mV)",
                "threshold_shift": "Ox_onset_threshold_shift_vs_ref (mV)",
                "tangent_shift": "Ox_onset_tangent_shift_vs_ref (mV)",
                "charge": "Q_ox (C)",
                "name_cn": "氧化", "name_en": "Oxidation"
            }
        return {
            "peak": "E_red_peak (V)", "current": "I_red_peak (A)",
            "threshold": "E_onset_red_threshold (V)",
            "tangent": "E_onset_red_tangent (V)",
            "peak_shift": "Red_peak_shift_vs_ref (mV)",
            "threshold_shift": "Red_onset_threshold_shift_vs_ref (mV)",
            "tangent_shift": "Red_onset_tangent_shift_vs_ref (mV)",
            "charge": "Q_red (C)",
            "name_cn": "还原", "name_en": "Reduction"
        }

    @staticmethod
    def normalize_status(value):
        s = str(value) if value is not None and not pd.isna(value) else QCStatus.FAILED.value
        aliases = {
            "Peak": QCStatus.OK.value, "Shoulder": QCStatus.REVIEW.value,
            "Threshold_only": QCStatus.OK.value, "Tangent_fallback": QCStatus.REVIEW.value,
            "Not_found": QCStatus.FAILED.value, "Poor": QCStatus.FAILED.value,
            "None": QCStatus.FAILED.value, "nan": QCStatus.FAILED.value,
        }
        return aliases.get(s, s if s in STATUS_COLORS else QCStatus.REVIEW.value)

    @staticmethod
    def format_value(column, value):
        if value is None or pd.isna(value):
            return "N/A"
        try:
            fv = float(value)
            if not np.isfinite(fv):
                return "N/A"
            if "(A)" in column or "(C)" in column or "(A·V)" in column or "Noise_sigma" in column:
                return f"{fv:.3E}"
            if "(mV)" in column:
                return f"{fv:+.1f}" if fv != 0 else "0.0"
            if "R2" in column or "fraction" in column:
                return f"{fv:.3f}"
            if "points" in column:
                return str(int(round(fv)))
            return f"{fv:.4f}"
        except Exception:
            return str(value)

    def _style_status_item(self, item, status):
        st = self.normalize_status(status)
        color = QColor(STATUS_COLORS.get(st, "#555555"))
        item.setForeground(QBrush(color))
        font = item.font(); font.setBold(True); item.setFont(font)
        if self.theme == "dark":
            bg_map = {
                QCStatus.FAILED.value: "#3B2028",
                QCStatus.REVIEW.value: "#3A2E17",
                QCStatus.BOUNDARY.value: "#2D2750",
            }
        else:
            bg_map = {
                QCStatus.FAILED.value: "#FDECEC",
                QCStatus.REVIEW.value: "#FFF6E6",
                QCStatus.BOUNDARY.value: "#F2EEFF",
            }
        if st in bg_map:
            item.setBackground(QBrush(QColor(bg_map[st])))
        item.setToolTip({
            QCStatus.OK.value: "OK：当前指标满足默认质量要求。",
            QCStatus.REVIEW.value: "Review：结果已保留，但建议人工检查。",
            QCStatus.BOUNDARY.value: "Boundary：候选峰靠近扫描边界，可能未形成完整峰。",
            QCStatus.FAILED.value: "Failed：当前结果未达到可靠判定条件。",
        }.get(st, st))

    # ------------------------------------------------------------- UI build
    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(8, 7, 8, 7)
        root.setSpacing(5)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        root.addWidget(splitter)

        left_scroll = QScrollArea()
        left_scroll.setWidgetResizable(True)
        left_scroll.setMinimumWidth(300)
        left_scroll.setMaximumWidth(450)
        left_scroll.setFrameShape(QFrame.Shape.NoFrame)
        left = QWidget()
        left_scroll.setWidget(left)
        self.left_layout = QVBoxLayout(left)
        self.left_layout.setContentsMargins(2, 2, 5, 2)
        self.left_layout.setSpacing(8)
        self._build_left_panel()
        splitter.addWidget(left_scroll)

        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(False)
        self.tabs.currentChanged.connect(self._refresh_current_tab)
        self._build_tabs()
        splitter.addWidget(self.tabs)
        splitter.setSizes([340, 1200])
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)

    def _build_menu(self):
        file_menu = self.menuBar().addMenu("文件")
        act_add = QAction("添加文件...", self); act_add.triggered.connect(self._pick_files)
        act_out = QAction("选择输出目录...", self); act_out.triggered.connect(self._pick_output)
        act_exit = QAction("退出", self); act_exit.triggered.connect(self.close)
        file_menu.addAction(act_add); file_menu.addAction(act_out); file_menu.addSeparator(); file_menu.addAction(act_exit)
        analysis_menu = self.menuBar().addMenu("分析")
        act_run = QAction("开始处理", self); act_run.triggered.connect(self._start_analysis)
        analysis_menu.addAction(act_run)
        view_menu = self.menuBar().addMenu("视图")
        for idx, text in enumerate(["CV曲线", "峰电位", "起始电位", "位移", "QC"]):
            act = QAction(text, self)
            act.triggered.connect(lambda checked=False, i=idx: self.tabs.setCurrentIndex(i))
            view_menu.addAction(act)
        view_menu.addSeparator()
        theme_group = QActionGroup(self)
        theme_group.setExclusive(True)
        self.act_light_theme = QAction("浅色主题", self, checkable=True)
        self.act_dark_theme = QAction("深色主题", self, checkable=True)
        self.act_light_theme.setChecked(True)
        theme_group.addAction(self.act_light_theme); theme_group.addAction(self.act_dark_theme)
        self.act_light_theme.triggered.connect(lambda checked=True: self._set_theme("light") if checked else None)
        self.act_dark_theme.triggered.connect(lambda checked=True: self._set_theme("dark") if checked else None)
        view_menu.addAction(self.act_light_theme); view_menu.addAction(self.act_dark_theme)
        help_menu = self.menuBar().addMenu("帮助")
        act_about = QAction("关于", self); act_about.triggered.connect(self._about); help_menu.addAction(act_about)

    def _set_theme(self, theme):
        self.theme = "dark" if theme == "dark" else "light"
        app = QApplication.instance()
        if app is not None:
            app.setStyleSheet(DARK_STYLE if self.theme == "dark" else LIGHT_STYLE)
        if hasattr(self, "act_light_theme"):
            self.act_light_theme.blockSignals(True); self.act_dark_theme.blockSignals(True)
            self.act_light_theme.setChecked(self.theme == "light")
            self.act_dark_theme.setChecked(self.theme == "dark")
            self.act_light_theme.blockSignals(False); self.act_dark_theme.blockSignals(False)
        panels = list(getattr(self, "plot_map", {}).values())
        if hasattr(self, "charge_plot"):
            panels.append(self.charge_plot)
        for panel in panels:
            try:
                panel.set_theme(self.theme)
            except Exception:
                pass
        self._refresh_current_tab()

    def _build_left_panel(self):
        files_group = QGroupBox("文件（拖拽或添加）")
        fl = QVBoxLayout(files_group); fl.setContentsMargins(10, 14, 10, 10)
        self.file_list = DropFileList(); self.file_list.setMinimumHeight(150); self.file_list.filesDropped.connect(self._add_files)
        fl.addWidget(self.file_list)
        row = QHBoxLayout()
        add_btn = QPushButton("添加文件"); clear_btn = QPushButton("清空")
        add_btn.clicked.connect(self._pick_files); clear_btn.clicked.connect(self._clear_files)
        row.addWidget(add_btn); row.addWidget(clear_btn); fl.addLayout(row)
        apply_card_shadow(files_group)
        self.left_layout.addWidget(files_group)

        out_group = QGroupBox("输出设置")
        og = QGridLayout(out_group); og.setContentsMargins(10, 14, 10, 10)
        self.output_edit = QLineEdit(); self.output_edit.setPlaceholderText("留空时输出至原文件夹")
        browse = QPushButton("浏览..."); default = QPushButton("默认")
        browse.clicked.connect(self._pick_output); default.clicked.connect(lambda: self.output_edit.clear())
        og.addWidget(QLabel("输出路径:"), 0, 0); og.addWidget(self.output_edit, 0, 1); og.addWidget(browse, 0, 2); og.addWidget(default, 1, 2)
        hint = QLabel("留空时输出至原文件夹"); hint.setProperty("muted", True); og.addWidget(hint, 1, 1)
        apply_card_shadow(out_group)
        self.left_layout.addWidget(out_group)

        mode_group = QGroupBox("处理模式")
        ml = QHBoxLayout(mode_group); ml.setContentsMargins(10, 14, 10, 10)
        self.max_radio = ModernRadioButton("筛选正值 (max)"); self.min_radio = ModernRadioButton("筛选负值 (min)")
        self.max_radio.setChecked(True); self.max_radio.toggled.connect(self._mode_changed)
        ml.addWidget(self.max_radio); ml.addWidget(self.min_radio); ml.addStretch(1)
        apply_card_shadow(mode_group)
        self.left_layout.addWidget(mode_group)

        voltage_group = QGroupBox("扫描范围")
        vg = QGridLayout(voltage_group); vg.setContentsMargins(10, 14, 10, 9)
        self.start_spin = QDoubleSpinBox(); self.start_spin.setRange(-20, 20); self.start_spin.setDecimals(4); self.start_spin.setValue(2.7)
        self.end_spin = QDoubleSpinBox(); self.end_spin.setRange(-20, 20); self.end_spin.setDecimals(4); self.end_spin.setValue(4.5)
        self.direction_hint = QLabel(); self.direction_hint.setProperty("muted", True)
        vg.addWidget(QLabel("起始电压 (V):"), 0, 0); vg.addWidget(self.start_spin, 0, 1)
        vg.addWidget(QLabel("终止电压 (V):"), 0, 2); vg.addWidget(self.end_spin, 0, 3)
        vg.addWidget(self.direction_hint, 1, 0, 1, 4)
        apply_card_shadow(voltage_group)
        self.left_layout.addWidget(voltage_group)

        scan_group = QGroupBox("扫描参数")
        sg = QGridLayout(scan_group); sg.setContentsMargins(10, 14, 10, 10)
        self.scan_spin = QDoubleSpinBox(); self.scan_spin.setRange(0.0001, 10000); self.scan_spin.setDecimals(4); self.scan_spin.setValue(5.0); self.scan_spin.setSuffix(" mV/s")
        self.precision_spin = QDoubleSpinBox(); self.precision_spin.setRange(0.1, 100); self.precision_spin.setDecimals(2); self.precision_spin.setValue(5.0); self.precision_spin.setSuffix(" mV")
        b2 = QPushButton("2"); b5 = QPushButton("5"); b2.setMaximumWidth(46); b5.setMaximumWidth(46)
        b2.clicked.connect(lambda: self.scan_spin.setValue(2.0)); b5.clicked.connect(lambda: self.scan_spin.setValue(5.0))
        sg.addWidget(QLabel("扫描速率:"), 0, 0); sg.addWidget(self.scan_spin, 0, 1); sg.addWidget(b2, 0, 2); sg.addWidget(b5, 0, 3)
        sg.addWidget(QLabel("切分精度:"), 1, 0); sg.addWidget(self.precision_spin, 1, 1)
        apply_card_shadow(scan_group)
        self.left_layout.addWidget(scan_group)

        sel_group = QGroupBox("输出圈数")
        sl = QGridLayout(sel_group); sl.setContentsMargins(10, 14, 10, 10)
        self.auto_radio = ModernRadioButton("自动"); self.manual_radio = ModernRadioButton("手动"); self.auto_radio.setChecked(True)
        self.auto_target_spin = QSpinBox(); self.auto_target_spin.setRange(1, 100); self.auto_target_spin.setValue(5)
        self.preset_combo = QComboBox(); self.preset_combo.addItems(list(PRESET_SCHEMES.keys())); self.preset_combo.setCurrentText("二十圈选点")
        self.manual_edit = QLineEdit("1, 5, 10, 15, 20")
        self.auto_radio.toggled.connect(self._selection_mode_changed); self.preset_combo.currentTextChanged.connect(self._preset_changed)
        sl.addWidget(self.auto_radio, 0, 0); sl.addWidget(QLabel("目标圈数:"), 0, 1); sl.addWidget(self.auto_target_spin, 0, 2)
        sl.addWidget(self.manual_radio, 1, 0); sl.addWidget(self.preset_combo, 1, 1); sl.addWidget(self.manual_edit, 1, 2)
        apply_card_shadow(sel_group)
        self.left_layout.addWidget(sel_group)

        options = QHBoxLayout()
        self.cut_check = ModernCheckBox("仅输出指定圈数"); self.cut_check.setChecked(True)
        self.verify_check = ModernCheckBox("生成验证文件")
        options.addWidget(self.cut_check); options.addWidget(self.verify_check); options.addStretch(1)
        self.left_layout.addLayout(options)

        self.run_btn = QPushButton("开始处理"); self.run_btn.setProperty("primary", True); self.run_btn.setMinimumHeight(38); self.run_btn.clicked.connect(self._start_analysis)
        run_row = QHBoxLayout(); run_row.addStretch(1); run_row.addWidget(self.run_btn); self.left_layout.addLayout(run_row)

        log_group = QGroupBox("运行日志")
        ll = QVBoxLayout(log_group); ll.setContentsMargins(8, 14, 8, 8)
        self.log_edit = QPlainTextEdit(); self.log_edit.setReadOnly(True); self.log_edit.setMinimumHeight(135)
        ll.addWidget(self.log_edit)
        self.left_layout.addWidget(log_group, 1)

    def _build_tabs(self):
        self.cv_tab = QWidget(); self.peak_tab = QWidget(); self.onset_tab = QWidget(); self.shift_tab = QWidget(); self.qc_tab = QWidget()
        self.tabs.addTab(self.cv_tab, "CV曲线"); self.tabs.addTab(self.peak_tab, "峰电位"); self.tabs.addTab(self.onset_tab, "起始电位"); self.tabs.addTab(self.shift_tab, "位移"); self.tabs.addTab(self.qc_tab, "QC")
        self._build_cv_tab(); self._build_peak_tab(); self._build_onset_tab(); self._build_shift_tab(); self._build_qc_tab()

    def _make_common_header(self, layout):
        row1 = QHBoxLayout()
        row1.addWidget(QLabel("当前文件:"))
        combo = QComboBox(); combo.setMinimumWidth(350); combo.currentIndexChanged.connect(lambda idx, c=combo: self._common_file_changed(c))
        self.common_file_combos.append(combo); row1.addWidget(combo, 1)
        mode_label = QLabel("模式：氧化 / Max"); count_label = QLabel("有效循环：0")
        mode_label.setProperty("muted", True); count_label.setProperty("muted", True)
        self.common_mode_labels.append(mode_label); self.common_count_labels.append(count_label)
        row1.addWidget(mode_label); row1.addSpacing(12); row1.addWidget(count_label)
        layout.addLayout(row1)
        row2 = QHBoxLayout(); row2.addWidget(QLabel("显示圈数:"))
        cycle_btn = QPushButton("未选择圈数"); cycle_btn.setMinimumWidth(320); cycle_btn.clicked.connect(self._open_cycle_selector)
        self.common_cycle_buttons.append(cycle_btn); row2.addWidget(cycle_btn, 1)
        b_all = QPushButton("全选"); b_clear = QPushButton("清空"); b_def = QPushButton("恢复默认")
        b_all.clicked.connect(self._select_all_preview); b_clear.clicked.connect(self._clear_preview); b_def.clicked.connect(self._restore_default_preview)
        row2.addWidget(b_all); row2.addWidget(b_clear); row2.addWidget(b_def)
        layout.addLayout(row2)
        line = QFrame(); line.setFrameShape(QFrame.Shape.HLine); line.setStyleSheet("color:#555;"); layout.addWidget(line)

    def _build_cv_tab(self):
        lay = QVBoxLayout(self.cv_tab)
        lay.setContentsMargins(10, 10, 10, 10)
        lay.setSpacing(7)
        self._make_common_header(lay)

        ctrl = QHBoxLayout()
        ctrl.setSpacing(8)
        ctrl.addWidget(QLabel("曲线:"))
        self.cv_raw = ModernRadioButton("原始数据")
        self.cv_smooth = ModernRadioButton("平滑数据")
        self.cv_both = ModernRadioButton("原始+平滑")
        self.cv_curve_group = QButtonGroup(self)
        self.cv_curve_group.setExclusive(True)
        for w in (self.cv_raw, self.cv_smooth, self.cv_both):
            self.cv_curve_group.addButton(w)
            w.toggled.connect(self._refresh_cv)
        self.cv_raw.setChecked(True)
        ctrl.addWidget(self.cv_raw); ctrl.addWidget(self.cv_smooth); ctrl.addWidget(self.cv_both)

        ctrl.addSpacing(16)
        ctrl.addWidget(QLabel("扫描:"))
        self.cv_analysis = ModernRadioButton("分析扫描支")
        self.cv_full = ModernRadioButton("完整 CV")
        self.cv_scan_group = QButtonGroup(self)
        self.cv_scan_group.setExclusive(True)
        for w in (self.cv_analysis, self.cv_full):
            self.cv_scan_group.addButton(w)
            w.toggled.connect(self._refresh_cv)
        self.cv_analysis.setChecked(True)
        ctrl.addWidget(self.cv_analysis); ctrl.addWidget(self.cv_full)

        ctrl.addSpacing(16)
        ctrl.addWidget(QLabel("标记:"))
        self.cv_peak = ModernCheckBox("峰电位")
        self.cv_onset = ModernCheckBox("起始电位")
        self.cv_legend = ModernCheckBox("图例")
        for w in (self.cv_peak, self.cv_onset, self.cv_legend):
            w.setChecked(True)
            w.stateChanged.connect(self._refresh_cv)
            ctrl.addWidget(w)
        ctrl.addStretch(1)
        lay.addLayout(ctrl)

        split = QSplitter(Qt.Orientation.Vertical)
        self.cv_plot = MplPanel(empty_text="添加 CV 文件后可在此查看多圈曲线")
        self.cv_plot.curveClicked.connect(self._plot_curve_clicked)
        self.cv_plot.hoverStatus.connect(self.statusBar().showMessage)
        self.charge_plot = MplPanel(empty_text="完成分析后显示库伦电荷", compact=True)
        self.charge_plot.toolbar.hide()
        self.charge_plot.curveClicked.connect(self._plot_curve_clicked)
        self.charge_plot.hoverStatus.connect(self.statusBar().showMessage)
        split.addWidget(self.cv_plot)
        split.addWidget(self.charge_plot)
        split.setStretchFactor(0, 7)
        split.setStretchFactor(1, 3)
        split.setSizes([570, 230])
        self.plot_map["cv"] = self.cv_plot
        lay.addWidget(split, 1)


    def _make_plot_table_tab(self, page, control_builder, key, table_ratio=30):
        lay = QVBoxLayout(page); lay.setContentsMargins(8, 8, 8, 8); lay.setSpacing(5); self._make_common_header(lay)
        control_builder(lay)
        split = QSplitter(Qt.Orientation.Vertical)
        plot = MplPanel(); plot.curveClicked.connect(self._plot_curve_clicked); plot.hoverStatus.connect(self.statusBar().showMessage)
        table = self._new_table(); table.itemSelectionChanged.connect(lambda k=key, t=table: self._table_selected(k, t)); table.itemDoubleClicked.connect(lambda item, k=key, t=table: self._table_double_clicked(k, t))
        split.addWidget(plot); split.addWidget(table); split.setStretchFactor(0, 1); split.setStretchFactor(1, 0); 
        if table_ratio >= 34:
            split.setSizes([470, 250])
        elif table_ratio <= 28:
            split.setSizes([520, 200])
        else:
            split.setSizes([500, 220])
        lay.addWidget(split, 1); self.plot_map[key] = plot; self.table_map[key] = table
        return plot, table

    def _build_peak_tab(self):
        def controls(lay):
            row = QHBoxLayout(); row.addWidget(QLabel("显示指标:")); self.peak_pot = ModernRadioButton("峰电位"); self.peak_cur = ModernRadioButton("峰电流"); self.peak_pot.setChecked(True)
            self.peak_labels = ModernCheckBox("显示数据标签")
            for w in (self.peak_pot, self.peak_cur): w.toggled.connect(self._refresh_peak)
            self.peak_labels.stateChanged.connect(self._refresh_peak); row.addWidget(self.peak_pot); row.addWidget(self.peak_cur); row.addSpacing(12); row.addWidget(self.peak_labels); row.addStretch(1); lay.addLayout(row)
        self.peak_plot, self.peak_table = self._make_plot_table_tab(self.peak_tab, controls, "peak", 34)

    def _build_onset_tab(self):
        def controls(lay):
            row = QHBoxLayout()
            row.addWidget(QLabel("显示方法:"))
            self.onset_thr = ModernCheckBox("阈值法")
            self.onset_tan = ModernCheckBox("切线法")
            self.onset_labels = ModernCheckBox("显示数据标签")
            self.onset_thr.setChecked(True)
            self.onset_tan.setChecked(True)
            for w in (self.onset_thr, self.onset_tan, self.onset_labels):
                w.stateChanged.connect(self._refresh_onset)
                row.addWidget(w)
            row.addStretch(1)
            lay.addLayout(row)
        self.onset_plot, self.onset_table = self._make_plot_table_tab(self.onset_tab, controls, "onset", 34)


    def _build_shift_tab(self):
        def controls(lay):
            row = QHBoxLayout()
            row.addWidget(QLabel("参考圈:"))
            self.ref_combo = QComboBox()
            self.ref_combo.setMinimumWidth(120)
            self.ref_combo.currentTextChanged.connect(self._reference_changed)
            row.addWidget(self.ref_combo)
            row.addSpacing(14)
            row.addWidget(QLabel("显示:"))
            self.shift_peak = ModernCheckBox("峰电位位移")
            self.shift_threshold = ModernCheckBox("阈值法 Onset 位移")
            self.shift_tangent = ModernCheckBox("切线法 Onset 位移")
            self.shift_zero = ModernCheckBox("ΔE=0 参考线")
            self.shift_labels = ModernCheckBox("数据标签")
            for w in (self.shift_peak, self.shift_threshold, self.shift_tangent, self.shift_zero):
                w.setChecked(True)
            for w in (self.shift_peak, self.shift_threshold, self.shift_tangent, self.shift_zero, self.shift_labels):
                w.stateChanged.connect(self._refresh_shift)
                row.addWidget(w)
            row.addStretch(1)
            lay.addLayout(row)
        self.shift_plot, self.shift_table = self._make_plot_table_tab(self.shift_tab, controls, "shift", 34)


    def _build_qc_tab(self):
        lay = QVBoxLayout(self.qc_tab)
        lay.setContentsMargins(10, 10, 10, 10)
        lay.setSpacing(8)
        self._make_common_header(lay)

        cards = QHBoxLayout()
        self.qc_peak_summary = QLabel("峰识别\n暂无结果")
        self.qc_threshold_summary = QLabel("阈值法 Onset\n暂无结果")
        self.qc_tangent_summary = QLabel("切线法 Onset\n暂无结果")
        self.qc_scan_summary = QLabel("扫描方向\n暂无结果")
        for lab in (self.qc_peak_summary, self.qc_threshold_summary, self.qc_tangent_summary, self.qc_scan_summary):
            lab.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lab.setMinimumHeight(78)
            lab.setProperty("summary", True)
            cards.addWidget(lab)
        lay.addLayout(cards)

        filt = QHBoxLayout()
        filt.addWidget(QLabel("显示状态:"))
        self.qc_filters = {}
        for st in (QCStatus.OK.value, QCStatus.REVIEW.value, QCStatus.BOUNDARY.value, QCStatus.FAILED.value):
            cb = ModernCheckBox(st)
            cb.setChecked(True)
            cb.stateChanged.connect(self._refresh_qc)
            self.qc_filters[st] = cb
            filt.addWidget(cb)
        self.qc_only_abnormal = ModernCheckBox("仅显示需要检查")
        self.qc_only_abnormal.stateChanged.connect(self._refresh_qc)
        filt.addWidget(self.qc_only_abnormal)
        reset = QPushButton("恢复全部")
        reset.clicked.connect(self._reset_qc)
        filt.addWidget(reset)
        filt.addStretch(1)
        lay.addLayout(filt)

        self.qc_table = self._new_table()
        self.qc_table.itemSelectionChanged.connect(lambda: self._table_selected("qc", self.qc_table))
        self.qc_table.itemDoubleClicked.connect(lambda item: self._table_double_clicked("qc", self.qc_table))
        self.table_map["qc"] = self.qc_table
        lay.addWidget(self.qc_table, 1)


    def _new_table(self):
        t = CopyableTableWidget()
        t.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        t.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        # Extended row selection enables Ctrl+C / multi-row copy without breaking
        # the existing single-click focus and double-click diagnostic interactions.
        t.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        t.setAlternatingRowColors(True)
        t.verticalHeader().setVisible(False)
        t.verticalHeader().setDefaultSectionSize(40)
        t.horizontalHeader().setMinimumHeight(72)
        t.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)
        t.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        t.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        t.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        t.setShowGrid(True)
        t.setToolTip("支持 Ctrl+C 复制所选行；右键可复制全部或含表头数据。")
        return t

    def _apply_defaults(self):
        self._mode_changed(); self._selection_mode_changed()

    # ------------------------------------------------------------- file / params
    def _pick_files(self):
        paths, _ = QFileDialog.getOpenFileNames(self, "选择 CV 数据文件", "", "CV data (*.DTA *.dta *.txt *.xlsx *.xls);;All files (*.*)")
        if paths: self._add_files(paths)

    def _add_files(self, paths):
        added = 0
        for p in paths:
            p = str(Path(p))
            if Path(p).suffix.lower() not in SUPPORTED_EXTENSIONS or p in self.file_paths: continue
            self.file_paths.append(p); self.file_list.addItem(p); added += 1
        if added: self._log("INFO", f"已添加 {added} 个文件。")

    def _clear_files(self):
        self.file_paths.clear(); self.file_list.clear(); self._log("INFO", "已清空输入文件列表。")

    def _pick_output(self):
        p = QFileDialog.getExistingDirectory(self, "选择输出目录", self.output_edit.text() or str(Path.cwd()))
        if p: self.output_edit.setText(p)

    def _mode_changed(self):
        is_max = self.max_radio.isChecked()
        if is_max:
            self.start_spin.setValue(2.7); self.end_spin.setValue(4.5); self.direction_hint.setText("正扫：终止电压 > 起始电压；特征分析使用原始去程扫描支")
        else:
            self.start_spin.setValue(3.0); self.end_spin.setValue(0.01); self.direction_hint.setText("负扫：终止电压 < 起始电压；特征分析使用原始去程扫描支")

    def _selection_mode_changed(self):
        auto = self.auto_radio.isChecked(); self.auto_target_spin.setEnabled(auto); self.preset_combo.setEnabled(not auto); self.manual_edit.setEnabled(not auto)

    def _preset_changed(self, text):
        vals = PRESET_SCHEMES.get(text)
        if vals is not None: self.manual_edit.setText(", ".join(map(str, vals)))

    def _manual_indices(self):
        nums = []
        for token in re.split(r"[,，;；\s]+", self.manual_edit.text().strip()):
            if token:
                try: nums.append(int(token))
                except ValueError: pass
        return sorted(set(n for n in nums if n > 0))

    def _validate_params(self):
        if not self.file_paths: return False, "请至少添加一个输入文件。"
        mode = "max" if self.max_radio.isChecked() else "min"
        sv, ev = self.start_spin.value(), self.end_spin.value()
        if mode == "max" and ev <= sv: return False, "Max 模式要求终止电压高于起始电压。"
        if mode == "min" and ev >= sv: return False, "Min 模式要求终止电压低于起始电压。"
        if self.manual_radio.isChecked() and not self._manual_indices(): return False, "手动模式没有有效圈号。"
        return True, ""

    # ------------------------------------------------------------- processing
    def _start_analysis(self):
        ok, msg = self._validate_params()
        if not ok:
            QMessageBox.warning(self, "参数检查", msg); return
        params = {
            "mode": "max" if self.max_radio.isChecked() else "min",
            "scan_rate_mv": self.scan_spin.value(), "precision_mv": self.precision_spin.value(),
            "start_voltage": self.start_spin.value(), "end_voltage": self.end_spin.value(),
            "save_verification": self.verify_check.isChecked(),
            "selection_mode": "auto" if self.auto_radio.isChecked() else "manual",
            "auto_target": self.auto_target_spin.value(), "manual_indices": self._manual_indices(),
            "apply_cut_to_all": self.cut_check.isChecked(), "output_dir": self.output_edit.text().strip() or None,
        }
        self.run_btn.setEnabled(False); self.log_edit.clear(); self.statusBar().showMessage("正在处理，请稍候...")
        self.worker = ProcessingWorker(self.file_paths, params, self); self.worker.log.connect(self._log); self.worker.finishedData.connect(self._analysis_finished); self.worker.failedFatal.connect(self._fatal_worker_error); self.worker.start()

    def _log(self, level, msg):
        prefix = f"[{level}]"
        self.log_edit.appendPlainText(f"{prefix} {msg}")
        self.statusBar().showMessage(str(msg))

    def _show_toast(self, text, kind="success", duration=3000):
        try:
            old = getattr(self, "_toast_label", None)
            if old is not None:
                old.hide(); old.deleteLater()
            label = QLabel(text, self)
            self._toast_label = label
            if self.theme == "dark":
                bg = "#163226" if kind == "success" else "#3A2E17"
                fg = "#D1FAE5" if kind == "success" else "#FDE68A"
                border = "#2B6B4B" if kind == "success" else "#8A6422"
            else:
                bg = "#ECFDF5" if kind == "success" else "#FFF7E6"
                fg = "#166534" if kind == "success" else "#92400E"
                border = "#A7F3D0" if kind == "success" else "#FCD34D"
            label.setStyleSheet(
                f"QLabel{{background:{bg};color:{fg};border:1px solid {border};"
                "border-radius:10px;padding:10px 14px;font-weight:600;}"
            )
            label.adjustSize()
            label.move(max(16, self.width() - label.width() - 26),
                       max(16, self.height() - label.height() - 54))
            label.raise_(); label.show()
            QTimer.singleShot(duration, lambda: label.hide() if label is self._toast_label else None)
        except Exception:
            pass

    def _fatal_worker_error(self, text):
        self.run_btn.setEnabled(True); QMessageBox.critical(self, "分析失败", text)

    def _analysis_finished(self, results, errors):
        self.run_btn.setEnabled(True)
        for path, info in results.items():
            self.analysis_cache[path] = info["df_all"].copy(); self.mode_cache[path] = info["mode"]
            defaults = [str(x) for x in info["df_filtered"].get("Curve", pd.Series([], dtype=str)).tolist()]
            self.default_selection_cache[path] = defaults; self.preview_selection_cache[path] = set(defaults)
        if results:
            self._sync_file_combos(list(results.keys()))
            first = next(iter(results)); self._activate_preview(first)
            self._log("INFO", f"处理完成：成功 {len(results)} 个，失败 {len(errors)} 个。")
        if errors:
            text = "\n".join(f"{Path(p).name}：{e}" for p, e in errors.items())
            QMessageBox.warning(self, "部分文件处理失败", text)
        elif results:
            self._show_toast(f"分析完成 · {len(results)} 个文件已保存", "success", 3200)

    # ------------------------------------------------------------- common header / selection
    def _sync_file_combos(self, paths):
        self._building_common = True
        try:
            for combo in self.common_file_combos:
                combo.clear()
                for p in paths: combo.addItem(Path(p).name, p)
        finally: self._building_common = False

    def _common_file_changed(self, combo):
        if self._building_common: return
        p = combo.currentData()
        if p: self._activate_preview(p)

    def _activate_preview(self, path):
        if path not in self.analysis_cache: return
        self.current_preview_path = path; self.current_focus_curve = None
        self._building_common = True
        try:
            for combo in self.common_file_combos:
                idx = combo.findData(path)
                if idx >= 0: combo.setCurrentIndex(idx)
        finally: self._building_common = False
        self._refresh_common_labels(); self._refresh_reference_combo(); self._refresh_current_tab()

    def _refresh_common_labels(self):
        # During construction the left controls can emit valueChanged before
        # _build_global_header() has created these widgets. Treat that phase
        # as non-refreshable rather than raising AttributeError.
        required = (
            "result_mode_label", "result_count_label", "result_state_label",
            "cycle_select_btn", "run_status_label",
        )
        if not all(hasattr(self, name) for name in required):
            return
        p = self.current_preview_path
        if not p: return
        mode = self.mode_cache.get(p, "max"); count = len(self.analysis_cache.get(p, [])); sm = ScanMode.MAX if mode == "max" else ScanMode.MIN
        for lab in self.common_mode_labels: lab.setText(f"模式：{sm.display}")
        for lab in self.common_count_labels: lab.setText(f"有效循环：{count}")
        selected = sorted(self.preview_selection_cache.get(p, set()), key=self.curve_no)
        text = ", ".join(c.replace("CURVE", "") for c in selected) if selected else "未选择圈数"
        for btn in self.common_cycle_buttons: btn.setText(text)

    def _valid_curve_names(self):
        p = self.current_preview_path
        if not p or p not in self.analysis_cache: return []
        return sorted([str(x) for x in self.analysis_cache[p]["Curve"].dropna().tolist()], key=self.curve_no)

    def _open_cycle_selector(self):
        names = self._valid_curve_names()
        if not names: QMessageBox.information(self, "选择显示圈数", "请先完成分析。") ; return
        dlg = CycleSelectorDialog(names, self.preview_selection_cache.get(self.current_preview_path, set()), self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self.preview_selection_cache[self.current_preview_path] = set(dlg.selected_curves()); self._refresh_common_labels(); self._refresh_current_tab()

    def _select_all_preview(self):
        if self.current_preview_path: self.preview_selection_cache[self.current_preview_path] = set(self._valid_curve_names()); self._refresh_common_labels(); self._refresh_current_tab()
    def _clear_preview(self):
        if self.current_preview_path: self.preview_selection_cache[self.current_preview_path] = set(); self._refresh_common_labels(); self._refresh_current_tab()
    def _restore_default_preview(self):
        if self.current_preview_path: self.preview_selection_cache[self.current_preview_path] = set(self.default_selection_cache.get(self.current_preview_path, [])); self._refresh_common_labels(); self._refresh_current_tab()

    def _selected_df(self):
        p = self.current_preview_path
        if not p or p not in self.analysis_cache: return pd.DataFrame()
        selected = self.preview_selection_cache.get(p, set())
        df = self.analysis_cache[p]
        return df[df["Curve"].isin(selected)].copy().sort_values("Curve", key=lambda s: s.map(self.curve_no)) if selected else df.iloc[0:0].copy()

    # ------------------------------------------------------------- raw data
    def _load_raw_curves(self, path=None, force_retry=False):
        """Return raw CV curves for preview, retrying failed/empty cache entries.

        Successful analysis injects the exact curves parsed by processor.py into
        ``raw_curve_cache``. Disk parsing remains only as a recoverable fallback.
        Empty/failed parses are never persisted as a successful cache entry.
        """
        p = path or self.current_preview_path
        if not p:
            return {}

        cached = self.raw_curve_cache.get(p)
        if cached and not force_retry:
            return cached

        # Older builds could permanently cache ``{}`` after one preview failure.
        # Treat that value as a miss so later refresh/re-analysis can recover.
        if p in self.raw_curve_cache and not cached:
            self.raw_curve_cache.pop(p, None)

        try:
            ext = Path(p).suffix.lower()
            curves = parse_txt_to_curves(p) if ext in (".txt", ".dta") else parse_excel_to_curves(p)
            curves = curves or {}
            if curves:
                self.raw_curve_cache[p] = curves
                self._log(
                    "INFO",
                    f"CV原始曲线读取成功：{Path(p).name}，共 {len(curves)} 条；"
                    f"CURVE={', '.join(sorted(map(str, curves.keys()), key=self.curve_no))}",
                )
                return curves
            self._log("WARNING", f"CV原始曲线读取完成但为空：{Path(p).name}；后续刷新将允许重试。")
            return {}
        except Exception as exc:
            self.raw_curve_cache.pop(p, None)
            self._log("ERROR", f"CV原始曲线读取失败：{Path(p).name}：{exc}；后续刷新将允许重试。")
            return {}

    # ------------------------------------------------------------- plotting
    def _refresh_current_tab(self, *args):
        idx = self.tabs.currentIndex()
        [self._refresh_cv, self._refresh_peak, self._refresh_onset, self._refresh_shift, self._refresh_qc][idx]()

    def _refresh_cv(self, *args):
        panel = self.cv_plot
        charge_panel = self.charge_plot
        p = self.current_preview_path
        dfres = self._selected_df()
        if not p or dfres.empty:
            panel.show_empty("请先完成分析并选择显示圈数")
            charge_panel.show_empty("完成分析后显示库伦电荷")
            return

        curves = self._load_raw_curves()
        mode = self.mode_cache.get(p, "max")
        cols = self.mode_columns(mode)
        ax = panel.prepare("CV 曲线\nCV Curves", "电位 / Potential (V)", "电流 / Current (A)")
        selected = sorted(self.preview_selection_cache.get(p, set()), key=self.curve_no)
        gradient = matplotlib.colors.LinearSegmentedColormap.from_list(
            "cv_blue_purple", ["#6EC8FF", "#4C8DFF", "#5165D6", "#8A5CF6"]
        )
        denom = max(len(selected) - 1, 1)

        for i, curve in enumerate(selected):
            if curve not in curves:
                continue
            raw = _clean_numeric_curve(curves[curve])
            if raw.empty:
                continue
            try:
                marker_df, _ = _extract_forward_scan(raw, mode)
            except Exception:
                marker_df = raw
            drawdf = marker_df if self.cv_analysis.isChecked() else raw
            v = drawdf["Vf"].to_numpy(float)
            im = drawdf["Im"].to_numpy(float)
            color = gradient(i / denom)
            smooth, _ = _smooth_current_by_voltage(v, im, FEATURE_SMOOTH_MV)

            if self.cv_raw.isChecked() or self.cv_both.isChecked():
                line, = ax.plot(
                    v, im, lw=2.0 if curve != self.current_focus_curve else 2.8,
                    color=color, alpha=0.94, label=curve if self.cv_legend.isChecked() else None,
                    antialiased=True
                )
                def tt(event, c=curve, vv=v, ii=im, m=mode):
                    if event.xdata is None:
                        return c
                    idx = int(np.argmin(np.abs(vv - event.xdata)))
                    return format_cv_tooltip(c, vv[idx], ii[idx], m)
                panel.register(line, curve, curve, f"当前：{curve}", tooltip_fn=tt)
            if self.cv_smooth.isChecked() or self.cv_both.isChecked():
                ax.plot(
                    v, smooth, lw=2.0, color=color, alpha=0.82,
                    linestyle="--" if self.cv_both.isChecked() else "-", antialiased=True
                )

            row = dfres[dfres["Curve"] == curve]
            if row.empty:
                continue
            row = row.iloc[0]

            mv = marker_df["Vf"].to_numpy(float)
            mi = marker_df["Im"].to_numpy(float)
            def marker_current(potential):
                if not _valid_number(potential) or len(mv) == 0:
                    return np.nan
                idx = int(np.nanargmin(np.abs(mv - float(potential))))
                return float(mi[idx])

            if self.cv_peak.isChecked() and _valid_number(row.get(cols["peak"])):
                pv = float(row[cols["peak"]])
                pi = float(row.get(cols["current"], marker_current(pv)))
                st = self.normalize_status(row.get("Peak_status"))
                sc = ax.scatter([pv], [pi], marker="^", s=72, color=color,
                                edgecolors=STATUS_COLORS.get(st, "#64748B"), linewidths=1.8, zorder=6)
                panel.register(sc, curve, format_peak_tooltip(curve, pv, pi, st, mode),
                               f"{curve}｜Peak {pv:.4f} V")

            if self.cv_onset.isChecked():
                tqc = self.normalize_status(row.get("Threshold_QC"))
                gqc = self.normalize_status(row.get("Tangent_QC"))
                tooltip = format_onset_tooltip(
                    curve, row.get(cols["threshold"]), row.get(cols["tangent"]),
                    row.get("Onset_difference (mV)"), tqc, gqc
                )
                if _valid_number(row.get(cols["threshold"])):
                    ov = float(row[cols["threshold"]]); oi = marker_current(ov)
                    sc = ax.scatter([ov], [oi], marker="o", s=62, color=color,
                                    edgecolors=STATUS_COLORS.get(tqc, "#64748B"), linewidths=1.8, zorder=6)
                    panel.register(sc, curve, tooltip, f"{curve}｜Threshold onset {ov:.4f} V｜QC {tqc}")
                if _valid_number(row.get(cols["tangent"])):
                    ov = float(row[cols["tangent"]]); oi = marker_current(ov)
                    sc = ax.scatter([ov], [oi], marker="D", s=58, facecolors="white",
                                    edgecolors=STATUS_COLORS.get(gqc, color), linewidths=1.8, zorder=6)
                    panel.register(sc, curve, tooltip, f"{curve}｜Tangent onset {ov:.4f} V｜QC {gqc}")

        if self.cv_legend.isChecked() and selected:
            leg = ax.legend(fontsize=9, framealpha=0.82, loc="upper left")
            if leg is not None:
                leg.get_frame().set_facecolor(panel._colors["tooltip_bg"])
                leg.get_frame().set_edgecolor(panel._colors["spine"])
                for t in leg.get_texts():
                    t.set_color(panel._colors["text"])
                    t.set_fontfamily(MATPLOTLIB_FONT)
        panel.draw()

        # Charge bar chart: Qox in Max mode / Qred in Min mode.
        charge_name_cn = "氧化库伦电荷" if mode == "max" else "还原库伦电荷"
        charge_name_en = "Oxidation Charge" if mode == "max" else "Reduction Charge"
        cax = charge_panel.prepare(
            f"{charge_name_cn}\n{charge_name_en}",
            "循环圈数 / Cycle", cols["charge"]
        )
        x = np.array([self.curve_no(c) for c in dfres["Curve"]], float)
        q = pd.to_numeric(dfres.get(cols["charge"], pd.Series(np.nan, index=dfres.index)), errors="coerce").to_numpy(float)
        valid = np.isfinite(q)
        if valid.any():
            colors = [gradient(i / max(len(x)-1, 1)) for i in range(len(x))]
            bars = cax.bar(x[valid], q[valid], width=0.62,
                           color=[colors[i] for i in np.where(valid)[0]],
                           edgecolor="none", alpha=0.92)
            cax.set_xticks(x)
            for rect, (_, row) in zip(bars, dfres.loc[valid].iterrows()):
                curve = str(row["Curve"])
                value = row.get(cols["charge"])
                charge_panel.register(
                    rect, curve,
                    f"{curve}\n{charge_name_en} / {charge_name_cn}：{float(value):.3E} C",
                    f"{curve}｜{cols['charge']} {float(value):.3E} C"
                )
            cax.ticklabel_format(axis="y", style="sci", scilimits=(-3, 3))
            charge_panel.draw()
        else:
            charge_panel.show_empty("当前所选循环没有可用的库伦电荷结果")


    def _refresh_peak(self, *args):
        df = self._selected_df(); panel = self.peak_plot
        if df.empty:
            panel.show_empty("请先完成分析并选择显示圈数")
            self._fill_table(self.peak_table, pd.DataFrame(), [])
            return
        mode = self.mode_cache.get(self.current_preview_path, "max")
        cols = self.mode_columns(mode)
        metric_col = cols["peak"] if self.peak_pot.isChecked() else cols["current"]
        ylabel = "峰电位 / Peak Potential (V)" if self.peak_pot.isChecked() else "峰电流 / Peak Current (A)"
        ax = panel.prepare(f"{cols['name_cn']}峰随循环变化\n{cols['name_en']} Peak vs. Cycle", "循环圈数 / Cycle", ylabel)
        x = np.array([self.curve_no(c) for c in df["Curve"]], float)
        y = pd.to_numeric(df[metric_col], errors="coerce").to_numpy(float)
        ax.plot(x, y, color="#2A7DE1", lw=2.0, antialiased=True)
        label_items = []
        for xi, yi, (_, row) in zip(x, y, df.iterrows()):
            curve = str(row["Curve"]); st = self.normalize_status(row.get("Peak_status"))
            if not np.isfinite(yi):
                continue
            sc = ax.scatter([xi], [yi], s=62 if curve == self.current_focus_curve else 46,
                            color="#2A7DE1", edgecolors=STATUS_COLORS.get(st, "#64748B"),
                            linewidths=1.6, zorder=5)
            panel.register(sc, curve,
                           format_peak_tooltip(curve, row.get(cols["peak"]), row.get(cols["current"]), st, mode),
                           f"{curve}｜Peak {fmt_potential(row.get(cols['peak']))}")
            if self.peak_labels.isChecked():
                label_items.append({"x": xi, "y": yi, "text": self.format_value(metric_col, yi),
                                    "color": "#2A7DE1", "preferred": "up"})
        ax.set_xticks(x)
        if label_items:
            panel.add_smart_labels(label_items, fontsize=8.3)
        panel.draw()
        self._fill_table(self.peak_table, df, ["Curve", cols["peak"], cols["current"]], ["Peak_status"])

    def _refresh_onset(self, *args):
        df = self._selected_df(); panel = self.onset_plot
        if df.empty:
            panel.show_empty("请先完成分析并选择显示圈数")
            self._fill_table(self.onset_table, pd.DataFrame(), [])
            return
        mode = self.mode_cache.get(self.current_preview_path, "max")
        cols = self.mode_columns(mode)
        ax = panel.prepare(
            f"起始{cols['name_cn']}电位随循环变化\n{cols['name_en']} Onset Potential vs. Cycle",
            "循环圈数 / Cycle", "起始电位 / Onset Potential (V)"
        )
        x = np.array([self.curve_no(c) for c in df["Curve"]], float)
        series = []
        if self.onset_thr.isChecked():
            series.append(("Threshold", cols["threshold"], "-", "o", "#2A7DE1", "Threshold_QC"))
        if self.onset_tan.isChecked():
            series.append(("Tangent", cols["tangent"], "--", "D", "#00B4A0", "Tangent_QC"))

        for label, col, ls, marker, color, qc_col in series:
            y = pd.to_numeric(df[col], errors="coerce").to_numpy(float)
            ax.plot(x, y, ls=ls, lw=2.0, color=color, label=label, antialiased=True)
            for xi, yi, (_, row) in zip(x, y, df.iterrows()):
                if not np.isfinite(yi):
                    continue
                curve = str(row["Curve"]); qc = self.normalize_status(row.get(qc_col))
                sc = ax.scatter([xi], [yi], marker=marker,
                                s=68 if curve == self.current_focus_curve else 52,
                                color=color if label == "Threshold" else "white",
                                edgecolors=STATUS_COLORS.get(qc, color), linewidths=1.7, zorder=5)
                panel.register(
                    sc, curve,
                    format_onset_tooltip(curve, row.get(cols["threshold"]), row.get(cols["tangent"]),
                                         row.get("Onset_difference (mV)"),
                                         self.normalize_status(row.get("Threshold_QC")),
                                         self.normalize_status(row.get("Tangent_QC"))),
                    f"{curve}｜{label} onset {yi:.4f} V｜QC {qc}"
                )

        # Data labels are laid out once after all series are known.  When both
        # onset methods round to the same displayed value, render one combined
        # label; otherwise place Threshold above and Tangent below the point.
        if self.onset_labels.isChecked():
            thr_values = pd.to_numeric(df[cols["threshold"]], errors="coerce").to_numpy(float)
            tan_values = pd.to_numeric(df[cols["tangent"]], errors="coerce").to_numpy(float)
            label_items = build_onset_label_items(
                x, thr_values, tan_values,
                show_threshold=self.onset_thr.isChecked(),
                show_tangent=self.onset_tan.isChecked(),
                precision=4,
            )
            for item in label_items:
                if item.get("kind") == "threshold":
                    item["color"] = "#2A7DE1"
                elif item.get("kind") == "tangent":
                    item["color"] = "#00B4A0"
                else:
                    item["color"] = panel._colors["text"]
            panel.add_smart_labels(label_items, fontsize=8.1)

        ax.set_xticks(x)
        panel.apply_legend(enabled=bool(series))
        panel.draw()
        self._fill_table(self.onset_table, df, ["Curve", cols["threshold"], cols["tangent"]])

    def _refresh_reference_combo(self):
        if not hasattr(self, "ref_combo"): return
        names = self._valid_curve_names(); current = self.ref_combo.currentText(); self.ref_combo.blockSignals(True); self.ref_combo.clear(); self.ref_combo.addItems(names)
        if current in names: self.ref_combo.setCurrentText(current)
        elif "CURVE1" in names: self.ref_combo.setCurrentText("CURVE1")
        elif names: self.ref_combo.setCurrentIndex(0)
        self.ref_combo.blockSignals(False)

    def _reference_changed(self, text):
        if text: self.statusBar().showMessage(TEXT["reference_changed"].format(reference=text)); self._refresh_shift()

    def _dynamic_shift_df(self):
        df = self._selected_df()
        full = self.analysis_cache.get(self.current_preview_path, pd.DataFrame())
        if df.empty or full.empty:
            return df
        mode = self.mode_cache.get(self.current_preview_path, "max")
        cols = self.mode_columns(mode)
        refname = self.ref_combo.currentText()
        ref = full[full["Curve"] == refname]
        if ref.empty:
            return df
        ref = ref.iloc[0]
        out = df.copy()
        out["Reference_curve"] = refname

        refs = {
            cols["peak"]: cols["peak_shift"],
            cols["threshold"]: cols["threshold_shift"],
            cols["tangent"]: cols["tangent_shift"],
        }
        for source_col, shift_col in refs.items():
            rv = pd.to_numeric(pd.Series([ref.get(source_col)]), errors="coerce").iloc[0]
            out[shift_col] = (
                (pd.to_numeric(out[source_col], errors="coerce") - rv) * 1000.0
                if np.isfinite(rv) else np.nan
            )
        return out

    def _refresh_shift(self, *args):
        self._refresh_reference_combo()
        df = self._dynamic_shift_df(); panel = self.shift_plot
        if df.empty:
            panel.show_empty("请先完成分析并选择显示圈数")
            self._fill_table(self.shift_table, pd.DataFrame(), [])
            return
        mode = self.mode_cache.get(self.current_preview_path, "max")
        cols = self.mode_columns(mode); ref = self.ref_combo.currentText()
        ax = panel.prepare("电位位移随循环变化\nPotential Shift vs. Cycle",
                           "循环圈数 / Cycle", "电位位移 / Potential Shift (mV)")
        x = np.array([self.curve_no(c) for c in df["Curve"]], float)
        if self.shift_zero.isChecked():
            ax.axhline(0, ls="--", lw=1.0, color=panel._colors["muted"], alpha=0.75)
        label_items = []

        if self.shift_peak.isChecked():
            y = pd.to_numeric(df[cols["peak_shift"]], errors="coerce").to_numpy(float)
            valid = np.isfinite(y)
            bars = ax.bar(x[valid], y[valid], width=0.55, color="#9CC7F6", edgecolor="#2A7DE1",
                          linewidth=0.8, alpha=0.78, label="Peak shift")
            for rect, (_, row), yi in zip(bars, df.loc[valid].iterrows(), y[valid]):
                curve = str(row["Curve"])
                panel.register(rect, curve,
                               format_shift_tooltip(curve, ref, row.get(cols["peak_shift"]),
                                                    row.get(cols["threshold_shift"]), row.get(cols["tangent_shift"])),
                               f"{curve}｜Peak {fmt_shift(row.get(cols['peak_shift']))}")
                if self.shift_labels.isChecked():
                    label_items.append({"x": rect.get_x()+rect.get_width()/2.0, "y": float(yi),
                                        "text": f"峰 {float(yi):+.1f}", "color": "#2A7DE1",
                                        "preferred": "up" if yi >= 0 else "down"})

        line_specs = [
            (self.shift_threshold.isChecked(), "Threshold onset shift", cols["threshold_shift"], "o", "#2A7DE1", "阈", "up"),
            (self.shift_tangent.isChecked(), "Tangent onset shift", cols["tangent_shift"], "D", "#00B4A0", "切", "down"),
        ]
        for enabled, label, col, marker, color, prefix, preferred in line_specs:
            if not enabled: continue
            y = pd.to_numeric(df[col], errors="coerce").to_numpy(float)
            ax.plot(x, y, lw=2.0, marker=marker, markersize=5.5, color=color, label=label, antialiased=True)
            for xi, yi, (_, row) in zip(x, y, df.iterrows()):
                if not np.isfinite(yi): continue
                curve = str(row["Curve"])
                sc = ax.scatter([xi], [yi], marker=marker, s=54, color=color, zorder=5)
                panel.register(sc, curve,
                               format_shift_tooltip(curve, ref, row.get(cols["peak_shift"]),
                                                    row.get(cols["threshold_shift"]), row.get(cols["tangent_shift"])),
                               f"{curve}｜{label} {fmt_shift(row.get(col))}")
                if self.shift_labels.isChecked():
                    label_items.append({"x": xi, "y": yi, "text": f"{prefix} {yi:+.1f}",
                                        "color": color, "preferred": preferred})
        ax.set_xticks(x)
        if label_items:
            panel.add_smart_labels(label_items, fontsize=8.0)
        panel.apply_legend(enabled=True)
        panel.draw()
        self._fill_table(self.shift_table, df,
                         ["Curve", "Reference_curve", cols["peak_shift"], cols["threshold_shift"], cols["tangent_shift"]])

    def _refresh_qc(self, *args):
        df = self._selected_df()
        if df.empty:
            self.qc_peak_summary.setText("峰识别\n暂无结果")
            self.qc_threshold_summary.setText("阈值法 Onset\n暂无结果")
            self.qc_tangent_summary.setText("切线法 Onset\n暂无结果")
            self.qc_scan_summary.setText("扫描方向\n暂无结果")
            self._fill_table(self.qc_table, pd.DataFrame(), [])
            return

        work = df.copy()
        status_cols = ("Peak_status", "Threshold_QC", "Tangent_QC", "Scan_QC")
        for col in status_cols:
            if col in work.columns:
                work[col] = work[col].map(self.normalize_status)

        def summary(label, series):
            parts = []
            for st in (QCStatus.OK.value, QCStatus.REVIEW.value, QCStatus.BOUNDARY.value, QCStatus.FAILED.value):
                n = int((series == st).sum())
                if n:
                    parts.append(f"{st} {n}")
            return label + "\n" + (" | ".join(parts) if parts else "暂无结果")

        self.qc_peak_summary.setText(summary("峰识别", work["Peak_status"]))
        self.qc_threshold_summary.setText(summary("阈值法 Onset", work["Threshold_QC"]))
        self.qc_tangent_summary.setText(summary("切线法 Onset", work["Tangent_QC"]))
        self.qc_scan_summary.setText(summary("扫描方向", work["Scan_QC"]))

        statuses = work[list(status_cols)]
        if self.qc_only_abnormal.isChecked():
            mask = (statuses != QCStatus.OK.value).any(axis=1)
        else:
            enabled = {st for st, cb in self.qc_filters.items() if cb.isChecked()}
            mask = statuses.apply(lambda r: any(x in enabled for x in r), axis=1) if enabled else np.zeros(len(work), dtype=bool)

        view = work.loc[mask].copy()
        cols = [
            "Curve", "Peak_status", "Threshold_QC", "Tangent_QC", "Scan_QC",
            "Scan_direction_fraction", "Onset_difference (mV)", "Onset_tangent_R2",
            "Baseline_R2", "Noise_sigma (A)", "Smooth_window_points"
        ]
        self._fill_table(self.qc_table, view, cols, ["Peak_status", "Threshold_QC", "Tangent_QC", "Scan_QC"])


    def _reset_qc(self):
        for cb in self.qc_filters.values(): cb.setChecked(True)
        self.qc_only_abnormal.setChecked(False); self._refresh_qc()

    # ------------------------------------------------------------- tables
    def _fill_table(self, table, df, columns, status_columns=None):
        status_columns = status_columns or []
        columns = [c for c in columns if c in df.columns] if not df.empty else columns
        table.clear()
        table.setRowCount(0)
        table.setColumnCount(len(columns))
        if not columns:
            return

        headers = [f"{EN_HEADERS.get(c,c)}\n{CN_HEADERS.get(c,c)}" for c in columns]
        table.setHorizontalHeaderLabels(headers)
        table.horizontalHeader().setMinimumHeight(72)
        table.setRowCount(len(df))

        for r, (_, row) in enumerate(df.iterrows()):
            table.setRowHeight(r, 40)
            for c, col in enumerate(columns):
                item = QTableWidgetItem(self.format_value(col, row.get(col)))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                if col in status_columns:
                    self._style_status_item(item, row.get(col))
                if col in QC_TOOLTIPS:
                    item.setToolTip(QC_TOOLTIPS[col])
                table.setItem(r, c, item)

        header = table.horizontalHeader()
        header.setStretchLastSection(False)
        # 结果页列较少时让数据列自动填满整个视口，杜绝右侧“黑色空块”。
        if len(columns) <= 5:
            for i, col in enumerate(columns):
                if col in ("Curve", "Reference_curve"):
                    header.setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)
                else:
                    header.setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)
            header.setStretchLastSection(True)
        else:
            for i, col in enumerate(columns):
                header.setSectionResizeMode(i, QHeaderView.ResizeMode.Interactive)
                if col == "Curve":
                    table.setColumnWidth(i, 125)
                elif col in ("Peak_status", "Threshold_QC", "Tangent_QC", "Scan_QC"):
                    table.setColumnWidth(i, 145)
                elif "fraction" in col:
                    table.setColumnWidth(i, 190)
                elif "threshold" in col.lower() or "tangent" in col.lower():
                    table.setColumnWidth(i, 210)
                elif "difference" in col.lower():
                    table.setColumnWidth(i, 185)
                else:
                    table.setColumnWidth(i, 165)
            # 多列表保持水平滚动；少列表分支上方已在设置列模式后启用最后一列拉伸。
            header.setStretchLastSection(False)


    # ------------------------------------------------------------- linkage
    def _plot_curve_clicked(self, curve, double_click):
        self.current_focus_curve = curve
        if curve not in self.preview_selection_cache.get(self.current_preview_path, set()): self.preview_selection_cache[self.current_preview_path].add(curve); self._refresh_common_labels()
        if double_click:
            self.tabs.setCurrentWidget(self.cv_tab); self.cv_peak.setChecked(True); self.cv_onset.setChecked(True); self.statusBar().showMessage(TEXT["curve_located"].format(curve=curve)); self._refresh_cv()
        else:
            self._refresh_current_tab()

    def _table_selected(self, key, table):
        rows = table.selectionModel().selectedRows()
        if not rows or table.columnCount()==0: return
        curve = table.item(rows[0].row(),0).text() if table.item(rows[0].row(),0) else ""
        if curve.startswith("CURVE"): self.current_focus_curve=curve; self.statusBar().showMessage(f"已选中 {curve}")

    def _table_double_clicked(self, key, table):
        rows=table.selectionModel().selectedRows()
        if not rows: return
        curve=table.item(rows[0].row(),0).text() if table.item(rows[0].row(),0) else ""
        if curve.startswith("CURVE"):
            self.current_focus_curve=curve; self.preview_selection_cache.setdefault(self.current_preview_path,set()).add(curve); self.tabs.setCurrentWidget(self.cv_tab); self.cv_peak.setChecked(True); self.cv_onset.setChecked(True); self._refresh_common_labels(); self._refresh_cv(); self.statusBar().showMessage(TEXT["curve_located"].format(curve=curve))

    def _about(self):
        QMessageBox.information(self, "关于", "Electrolyte CV Processor v2.0\n\n界面基于 PySide6 / Qt 重构，风格参考 BatteryCVAnalyzer。\n保留积分、Peak、双方法 Onset、Shift、QC 与 4-Sheet Excel 输出。")


class AnalysisStatus(str, Enum):
    NOT_ANALYZED = "not_analyzed"
    READY = "ready"
    OUTDATED = "outdated"
    PROCESSING = "processing"
    FAILED = "failed"


@dataclass
class FileState:
    path: str
    status: AnalysisStatus = AnalysisStatus.NOT_ANALYZED
    parameter_snapshot: Optional[dict] = None
    draft_params: Optional[dict] = None
    selected_cycles: set = field(default_factory=set)
    default_cycles: list = field(default_factory=list)
    reference_curve: Optional[str] = None
    last_error: Optional[str] = None


class CVQtMainWindowV19(CVQtMainWindow):
    """v2.0: six-tab UI + per-file state + outdated/diagnostic contexts."""

    def __init__(self):
        QMainWindow.__init__(self)
        self.setWindowTitle("Electrolyte CV Processor v2.0")
        self.resize(1600, 920)
        self.setMinimumSize(1220, 760)

        self.file_paths = []
        self.file_states = {}
        self.analysis_cache = {}
        self.raw_curve_cache = {}
        self._last_cv_refresh_signature = None
        self.mode_cache = {}
        self.default_selection_cache = {}
        self.preview_selection_cache = {}
        self.parameter_snapshot_cache = {}

        self.current_preview_path = None
        self.current_focus_curve = None
        self.temporary_curve = None
        self.diagnostic_context = None
        self.worker = None
        self._active_params = None
        self._loading_params = False
        self._processing = False
        self._warning_count = 0
        self._error_count = 0

        self.theme = "light"
        self.common_file_combos = []
        self.common_cycle_buttons = []
        self.common_mode_labels = []
        self.common_count_labels = []
        self.table_map = {}
        self.plot_map = {}
        self._building_common = False
        self.settings = QSettings("OpenAI", "ElectrolyteCVProcessor")
        self.settings_manager = SettingsManager(self.settings)
        # Guard against construction-time valueChanged/toggled signals.  The
        # left parameter panel is built before the global result labels, so a
        # spin-box signal must not refresh labels until the full UI exists.
        self._ui_ready = False

        self._build_ui()
        self._build_menu()
        self._ui_ready = True
        self._apply_defaults()
        self.statusBar().showMessage("就绪。请添加 CV 数据文件。")

    # ------------------------- state helpers -------------------------
    def _ensure_file_state(self, path):
        if path not in self.file_states:
            self.file_states[path] = FileState(path=path, draft_params=self._analysis_parameter_values())
        return self.file_states[path]

    def _analysis_parameter_values(self):
        if not hasattr(self, "max_radio"):
            return {
                "mode": DEFAULT_MODE,
                "start_voltage": DEFAULT_VOLTAGE[DEFAULT_MODE]["start"],
                "end_voltage": DEFAULT_VOLTAGE[DEFAULT_MODE]["end"],
                "scan_rate_mv": float(DEFAULT_SCAN_RATE_MV),
                "precision_mv": float(DEFAULT_PRECISION_MV),
            }
        return {
            "mode": "max" if self.max_radio.isChecked() else "min",
            "start_voltage": round(float(self.start_spin.value()), 6),
            "end_voltage": round(float(self.end_spin.value()), 6),
            "scan_rate_mv": round(float(self.scan_spin.value()), 6),
            "precision_mv": round(float(self.precision_spin.value()), 6),
        }

    @staticmethod
    def _same_params(a, b):
        if not a or not b:
            return False
        keys = ("mode", "start_voltage", "end_voltage", "scan_rate_mv", "precision_mv")
        for key in keys:
            av, bv = a.get(key), b.get(key)
            if key == "mode":
                if av != bv:
                    return False
            else:
                try:
                    if abs(float(av) - float(bv)) > 1e-9:
                        return False
                except Exception:
                    return False
        return True

    def _store_current_draft(self):
        p = self.current_preview_path
        if p and p in self.file_states and not self._loading_params:
            self.file_states[p].draft_params = self._analysis_parameter_values()
            self._update_file_status(p)

    def _update_file_status(self, path):
        st = self._ensure_file_state(path)
        if st.status == AnalysisStatus.PROCESSING:
            return st.status
        if st.status == AnalysisStatus.FAILED:
            # A retained successful cache remains inspectable but the latest attempt is still failed.
            return st.status
        if path not in self.analysis_cache:
            st.status = AnalysisStatus.NOT_ANALYZED
        elif st.parameter_snapshot and st.draft_params and not self._same_params(st.parameter_snapshot, st.draft_params):
            st.status = AnalysisStatus.OUTDATED
        else:
            st.status = AnalysisStatus.READY
        return st.status

    def _status_text(self, path):
        if not path:
            return "未选择文件", "idle"
        st = self._ensure_file_state(path)
        status = self._update_file_status(path)
        mapping = {
            AnalysisStatus.NOT_ANALYZED: ("尚未分析", "idle"),
            AnalysisStatus.READY: ("结果已就绪", "ready"),
            AnalysisStatus.OUTDATED: ("参数已修改 · 当前结果已过期", "outdated"),
            AnalysisStatus.PROCESSING: ("正在处理", "processing"),
            AnalysisStatus.FAILED: ("最近一次分析失败", "failed"),
        }
        return mapping[status]

    def _empty_message(self):
        p = self.current_preview_path
        if not p:
            return "请选择文件"
        st = self._ensure_file_state(p)
        if p not in self.analysis_cache:
            if st.status == AnalysisStatus.FAILED:
                return "当前文件最近一次分析失败\n请查看运行日志后重新处理"
            return "尚未分析当前文件\n点击左侧“开始处理”生成分析结果"
        if st.status == AnalysisStatus.OUTDATED:
            return "当前参数已修改，图表仍显示上一次分析结果"
        return "当前没有可显示的数据"

    def _load_params_to_controls(self, params):
        if not params:
            return
        self._loading_params = True
        try:
            is_max = params.get("mode", "max") == "max"
            self.max_radio.setChecked(is_max)
            self.min_radio.setChecked(not is_max)
            self.start_spin.setValue(float(params.get("start_voltage", 2.7 if is_max else 3.0)))
            self.end_spin.setValue(float(params.get("end_voltage", 4.5 if is_max else 0.01)))
            self.scan_spin.setValue(float(params.get("scan_rate_mv", DEFAULT_SCAN_RATE_MV)))
            self.precision_spin.setValue(float(params.get("precision_mv", DEFAULT_PRECISION_MV)))
            self._update_direction_hint()
        finally:
            self._loading_params = False

    def _parameters_changed(self, *args):
        if not getattr(self, "_ui_ready", False):
            return
        if self._loading_params or self._processing:
            return
        p = self.current_preview_path
        if p:
            st = self._ensure_file_state(p)
            st.draft_params = self._analysis_parameter_values()
            if st.status != AnalysisStatus.FAILED:
                self._update_file_status(p)
        self._refresh_common_labels()

    # ------------------------- UI build -------------------------
    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(8, 7, 8, 7)
        root.setSpacing(5)

        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
        root.addWidget(self.main_splitter)

        self.left_scroll = QScrollArea()
        self.left_scroll.setWidgetResizable(True)
        # The parameter pane is vertically scrollable only.  Horizontal scrolling
        # hid the left edges of labels after DPI/layout changes and is not part of
        # the intended workflow.  Child widgets below are made width-flexible so
        # this does not merely hide clipped content.
        self.left_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.left_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.left_scroll.setMinimumWidth(360)
        self.left_scroll.setMaximumWidth(440)
        self.left_scroll.setFrameShape(QFrame.Shape.NoFrame)
        left = QWidget()
        left.setMinimumWidth(0)
        left.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.left_scroll.setWidget(left)
        # A stale horizontal value can survive in QScrollArea even after the bar
        # is hidden; force the logical origin back to the left edge.
        self.left_scroll.horizontalScrollBar().setValue(0)
        self.left_layout = QVBoxLayout(left)
        self.left_layout.setContentsMargins(3, 3, 3, 3)
        self.left_layout.setSpacing(7)
        self._build_left_panel()
        self.main_splitter.addWidget(self.left_scroll)

        right = QWidget()
        rlay = QVBoxLayout(right)
        rlay.setContentsMargins(4, 2, 2, 2)
        rlay.setSpacing(6)
        self._build_global_header(rlay)
        self.tabs = QTabWidget()
        # IMPORTANT: build all pages before connecting currentChanged.
        # QTabWidget emits currentChanged while the first tab is being added;
        # connecting too early calls _refresh_cv() before self.cv_plot exists.
        self._build_tabs()
        self.tabs.currentChanged.connect(self._refresh_current_tab)
        rlay.addWidget(self.tabs, 1)
        self.main_splitter.addWidget(right)
        self.main_splitter.setStretchFactor(0, 0)
        self.main_splitter.setStretchFactor(1, 1)
        self.main_splitter.setSizes([400, 1200])
        saved = self.settings.value("splitter_state")
        if saved:
            try:
                self.main_splitter.restoreState(saved)
            except Exception:
                pass
        # Preserve user splitter state when reasonable, but do not let an old
        # narrow state from an earlier UI version recreate the overflow problem.
        QTimer.singleShot(0, self._sanitize_main_splitter_width)

    def _sanitize_main_splitter_width(self):
        """Clamp restored left-pane width to the usable V19 range.

        QSettings may contain splitter geometry saved by an older build.  Keep
        valid user choices, but repair values that make the parameter panel too
        narrow (or unnecessarily wide) for the current DPI-aware controls.
        """
        try:
            sizes = self.main_splitter.sizes()
            if len(sizes) < 2:
                return
            total = sum(sizes)
            if total <= 0:
                return
            left_width = sizes[0]
            min_reasonable = 380
            max_reasonable = min(430, max(min_reasonable, total - 720))
            clamped = min(max(left_width, min_reasonable), max_reasonable)
            if clamped != left_width:
                self.main_splitter.setSizes([clamped, max(1, total - clamped)])
            # There is intentionally no horizontal navigation in the left pane.
            self.left_scroll.horizontalScrollBar().setValue(0)
        except Exception:
            pass

    def _build_menu(self):
        file_menu = self.menuBar().addMenu("文件")
        act_add = QAction("添加文件...", self); act_add.triggered.connect(self._pick_files)
        act_out = QAction("选择输出目录...", self); act_out.triggered.connect(self._pick_output)
        act_exit = QAction("退出", self); act_exit.triggered.connect(self.close)
        file_menu.addAction(act_add); file_menu.addAction(act_out); file_menu.addSeparator(); file_menu.addAction(act_exit)

        analysis_menu = self.menuBar().addMenu("分析")
        act_run = QAction("开始处理", self); act_run.triggered.connect(self._start_analysis)
        analysis_menu.addAction(act_run)

        view_menu = self.menuBar().addMenu("视图")
        for idx, text in enumerate(["CV曲线", "库伦电荷", "峰电位", "起始电位", "位移", "QC"]):
            act = QAction(text, self)
            act.triggered.connect(lambda checked=False, i=idx: self.tabs.setCurrentIndex(i))
            view_menu.addAction(act)
        view_menu.addSeparator()
        theme_group = QActionGroup(self); theme_group.setExclusive(True)
        self.act_light_theme = QAction("浅色主题", self, checkable=True)
        self.act_dark_theme = QAction("深色主题", self, checkable=True)
        theme_group.addAction(self.act_light_theme); theme_group.addAction(self.act_dark_theme)
        self.act_light_theme.triggered.connect(lambda checked=True: self._set_theme("light") if checked else None)
        self.act_dark_theme.triggered.connect(lambda checked=True: self._set_theme("dark") if checked else None)
        view_menu.addAction(self.act_light_theme); view_menu.addAction(self.act_dark_theme)

        settings_menu = self.menuBar().addMenu("设置")
        act_preferences = QAction("首选项...", self); act_preferences.triggered.connect(self._open_preferences)
        act_save_defaults = QAction("将当前配置保存为默认", self); act_save_defaults.triggered.connect(self._save_current_as_default)
        act_restore_defaults = QAction("恢复软件默认设置...", self); act_restore_defaults.triggered.connect(self._restore_software_defaults)
        settings_menu.addAction(act_preferences); settings_menu.addAction(act_save_defaults); settings_menu.addSeparator(); settings_menu.addAction(act_restore_defaults)

        help_menu = self.menuBar().addMenu("帮助")
        act_about = QAction("关于", self); act_about.triggered.connect(self._about); help_menu.addAction(act_about)

    @staticmethod
    def _tab_id_from_index(index):
        ids = ("cv", "charge", "peak", "onset", "shift", "qc")
        return ids[index] if 0 <= int(index) < len(ids) else "cv"

    @staticmethod
    def _tab_index_from_id(tab_id):
        ids = ("cv", "charge", "peak", "onset", "shift", "qc")
        try:
            return ids.index(str(tab_id))
        except ValueError:
            return 0

    def _capture_preference_profile(self, base_profile=None):
        base = normalize_profile(base_profile or self.settings_manager.load_defaults())
        profile = {**base}
        profile["analysis"] = {
            "mode": "max" if self.max_radio.isChecked() else "min",
            "start_voltage": float(self.start_spin.value()),
            "end_voltage": float(self.end_spin.value()),
            "scan_rate_mv": float(self.scan_spin.value()),
            "precision_mv": float(self.precision_spin.value()),
        }
        profile["output"] = {
            "selection_mode": "auto" if self.auto_radio.isChecked() else "manual",
            "auto_target": int(self.auto_target_spin.value()),
            "preset": self.preset_combo.currentText(),
            "manual_cycles": self.manual_edit.text().strip(),
            "cut_only": self.cut_check.isChecked(),
            "verify_file": self.verify_check.isChecked(),
            "original_dir": self.output_original_check.isChecked(),
            "custom_dir": self.output_edit.text().strip(),
        }
        profile["display"] = {
            "cv": {
                "curve": "raw" if self.cv_raw.isChecked() else ("smooth" if self.cv_smooth.isChecked() else "both"),
                "scan": "analysis" if self.cv_analysis.isChecked() else "full",
                "peak": self.cv_peak.isChecked(),
                "threshold_onset": self.cv_threshold.isChecked(),
                "tangent_onset": self.cv_tangent.isChecked(),
                "legend": self.cv_legend.isChecked(),
            },
            "charge": {"style": "bar" if self.charge_bar.isChecked() else "line", "labels": self.charge_labels.isChecked(), "table": self.charge_show_table.isChecked()},
            "peak": {"metric": "potential" if self.peak_pot.isChecked() else "current", "labels": self.peak_labels.isChecked(), "table": self.peak_show_table.isChecked()},
            "onset": {"threshold": self.onset_thr.isChecked(), "tangent": self.onset_tan.isChecked(), "labels": self.onset_labels.isChecked(), "table": self.onset_show_table.isChecked()},
            "shift": {"peak": self.shift_peak.isChecked(), "threshold": self.shift_threshold.isChecked(), "tangent": self.shift_tangent.isChecked(), "zero_line": self.shift_zero.isChecked(), "labels": self.shift_labels.isChecked(), "table": self.shift_show_table.isChecked()},
            "qc": {
                "status_ok": self.qc_filters[QCStatus.OK.value].isChecked(),
                "status_review": self.qc_filters[QCStatus.REVIEW.value].isChecked(),
                "status_boundary": self.qc_filters[QCStatus.BOUNDARY.value].isChecked(),
                "status_failed": self.qc_filters[QCStatus.FAILED.value].isChecked(),
                "only_abnormal": self.qc_only_abnormal.isChecked(),
            },
        }
        profile["default_tab"] = self._tab_id_from_index(self.tabs.currentIndex())
        profile["theme"] = self.theme
        profile["log_expanded"] = self.log_toggle_btn.isChecked()
        return normalize_profile(profile)

    def _apply_preference_profile(self, profile):
        p = normalize_profile(profile)
        old_loading = self._loading_params
        self._loading_params = True
        try:
            a = p["analysis"]
            is_max = a["mode"] == "max"
            # Set mode while loading is guarded so _mode_changed cannot overwrite custom voltages.
            self.max_radio.setChecked(is_max); self.min_radio.setChecked(not is_max)
            self.start_spin.setValue(float(a["start_voltage"])); self.end_spin.setValue(float(a["end_voltage"]))
            self.scan_spin.setValue(float(a["scan_rate_mv"])); self.precision_spin.setValue(float(a["precision_mv"]))
            self._update_direction_hint()

            o = p["output"]
            is_auto = o["selection_mode"] == "auto"
            self.auto_radio.setChecked(is_auto); self.manual_radio.setChecked(not is_auto)
            self.auto_target_spin.setValue(int(o["auto_target"])); self.preset_combo.setCurrentText(str(o["preset"])); self.manual_edit.setText(str(o["manual_cycles"]))
            self.cut_check.setChecked(bool(o["cut_only"])); self.verify_check.setChecked(bool(o["verify_file"]))
            self.output_original_check.setChecked(bool(o["original_dir"]))
            if not o["original_dir"]:
                self.output_edit.setText(str(o["custom_dir"]))
            self._selection_mode_changed(); self._output_mode_changed(True)

            d = p["display"]; cv = d["cv"]
            self.cv_raw.setChecked(cv["curve"] == "raw"); self.cv_smooth.setChecked(cv["curve"] == "smooth"); self.cv_both.setChecked(cv["curve"] == "both")
            self.cv_analysis.setChecked(cv["scan"] == "analysis"); self.cv_full.setChecked(cv["scan"] == "full")
            self.cv_peak.setChecked(bool(cv["peak"])); self.cv_threshold.setChecked(bool(cv["threshold_onset"])); self.cv_tangent.setChecked(bool(cv["tangent_onset"])); self.cv_legend.setChecked(bool(cv["legend"]))
            c=d["charge"]; self.charge_bar.setChecked(c["style"] == "bar"); self.charge_line.setChecked(c["style"] == "line"); self.charge_labels.setChecked(c["labels"]); self.charge_show_table.setChecked(c["table"]); self.charge_table.setVisible(c["table"])
            c=d["peak"]; self.peak_pot.setChecked(c["metric"] == "potential"); self.peak_cur.setChecked(c["metric"] == "current"); self.peak_labels.setChecked(c["labels"]); self.peak_show_table.setChecked(c["table"]); self.peak_table.setVisible(c["table"])
            c=d["onset"]; self.onset_thr.setChecked(c["threshold"]); self.onset_tan.setChecked(c["tangent"]); self.onset_labels.setChecked(c["labels"]); self.onset_show_table.setChecked(c["table"]); self.onset_table.setVisible(c["table"])
            c=d["shift"]; self.shift_peak.setChecked(c["peak"]); self.shift_threshold.setChecked(c["threshold"]); self.shift_tangent.setChecked(c["tangent"]); self.shift_zero.setChecked(c["zero_line"]); self.shift_labels.setChecked(c["labels"]); self.shift_show_table.setChecked(c["table"]); self.shift_table.setVisible(c["table"])
            c=d["qc"]; self.qc_filters[QCStatus.OK.value].setChecked(c["status_ok"]); self.qc_filters[QCStatus.REVIEW.value].setChecked(c["status_review"]); self.qc_filters[QCStatus.BOUNDARY.value].setChecked(c["status_boundary"]); self.qc_filters[QCStatus.FAILED.value].setChecked(c["status_failed"]); self.qc_only_abnormal.setChecked(c["only_abnormal"])
            self._set_log_expanded(bool(p["log_expanded"]))
            self.tabs.setCurrentIndex(self._tab_index_from_id(p["default_tab"]))
            self._set_theme(p["theme"])
        finally:
            self._loading_params = old_loading
        self._refresh_common_labels(); self._refresh_current_tab()

    def _apply_defaults(self):
        # Global defaults/last-session state never restores files, results, focus curves, or diagnostics.
        self._apply_preference_profile(self.settings_manager.startup_profile())

    def _open_preferences(self):
        dialog = PreferencesDialog(self.settings_manager.load_defaults(), self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            saved = self.settings_manager.save_defaults(dialog.profile())
            self._apply_preference_profile(saved)
            self.statusBar().showMessage("首选项已保存并应用。")

    def _save_current_as_default(self):
        defaults = self.settings_manager.load_defaults()
        profile = self._capture_preference_profile(defaults)
        # The startup-behavior selector lives in Preferences; this action saves current controls only.
        profile["startup_behavior"] = defaults["startup_behavior"]
        self.settings_manager.save_defaults(profile)
        self.statusBar().showMessage("当前配置已保存为默认。")

    def _restore_software_defaults(self):
        answer = QMessageBox.question(self, "恢复软件默认设置", "确认恢复软件默认设置？这不会删除任何数据文件。")
        if answer != QMessageBox.StandardButton.Yes:
            return
        profile = self.settings_manager.restore_software_defaults()
        self._apply_preference_profile(profile)
        self.statusBar().showMessage("已恢复软件默认设置。")

    def _set_theme(self, theme):
        self.theme = "dark" if theme == "dark" else "light"
        app = QApplication.instance()
        if app is not None:
            app.setStyleSheet(V19_DARK_STYLE if self.theme == "dark" else V19_LIGHT_STYLE)
        if hasattr(self, "act_light_theme"):
            self.act_light_theme.blockSignals(True); self.act_dark_theme.blockSignals(True)
            self.act_light_theme.setChecked(self.theme == "light")
            self.act_dark_theme.setChecked(self.theme == "dark")
            self.act_light_theme.blockSignals(False); self.act_dark_theme.blockSignals(False)
        for panel in list(self.plot_map.values()):
            try:
                panel.set_theme(self.theme)
            except Exception:
                pass
        self.settings.setValue("theme", self.theme)
        self._refresh_common_labels()
        self._refresh_current_tab()

    @staticmethod
    def _mark_secondary(button):
        button.setProperty("secondary", True)
        return button

    @staticmethod
    def _mark_tertiary(button):
        button.setProperty("tertiary", True)
        return button

    def _build_left_panel(self):
        # Card 1: files + paths
        file_card = QGroupBox("文件与路径")
        file_card.setMinimumWidth(0); file_card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        fl = QVBoxLayout(file_card); fl.setContentsMargins(10, 13, 10, 9); fl.setSpacing(6)
        fl.addWidget(QLabel("输入文件"))
        self.file_list = DropFileList(); self.file_list.setMinimumHeight(88); self.file_list.filesDropped.connect(self._add_files)
        fl.addWidget(self.file_list)
        frow = QHBoxLayout()
        add_btn = self._mark_secondary(QPushButton("添加文件"))
        remove_btn = self._mark_tertiary(QPushButton("移除所选"))
        clear_btn = self._mark_tertiary(QPushButton("清空"))
        add_btn.clicked.connect(self._pick_files); remove_btn.clicked.connect(self._remove_selected_files); clear_btn.clicked.connect(self._clear_files)
        frow.addWidget(add_btn); frow.addWidget(remove_btn); frow.addWidget(clear_btn)
        fl.addLayout(frow)
        fl.addSpacing(2); fl.addWidget(QLabel("输出目录"))
        orow = QHBoxLayout()
        self.output_edit = QLineEdit(); self.output_edit.setMinimumWidth(0); self.output_edit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed); self.output_edit.setPlaceholderText("选择自定义输出目录")
        self.output_browse_btn = self._mark_secondary(QPushButton("浏览")); self.output_browse_btn.clicked.connect(self._pick_output)
        orow.addWidget(self.output_edit, 1); orow.addWidget(self.output_browse_btn)
        fl.addLayout(orow)
        self.output_original_check = ModernCheckBox("输出至原文件目录")
        self.output_original_check.setChecked(True)
        self.output_original_check.toggled.connect(self._output_mode_changed)
        fl.addWidget(self.output_original_check)
        apply_card_shadow(file_card); self.left_layout.addWidget(file_card)

        # Card 2: analysis parameters
        param_card = QGroupBox("分析参数")
        param_card.setMinimumWidth(0); param_card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        pg = QGridLayout(param_card); pg.setContentsMargins(10, 13, 10, 9); pg.setHorizontalSpacing(8); pg.setVerticalSpacing(6)
        pg.setColumnStretch(0, 1); pg.setColumnStretch(1, 1)
        pg.addWidget(QLabel("分析模式"), 0, 0, 1, 2)
        self.max_radio = ModernRadioButton("氧化 / Max"); self.min_radio = ModernRadioButton("还原 / Min")
        self.mode_button_group = QButtonGroup(self); self.mode_button_group.setExclusive(True)
        self.mode_button_group.addButton(self.max_radio); self.mode_button_group.addButton(self.min_radio)
        self.max_radio.setChecked(True)
        self.max_radio.toggled.connect(self._mode_changed); self.min_radio.toggled.connect(self._mode_changed)
        pg.addWidget(self.max_radio, 1, 0); pg.addWidget(self.min_radio, 1, 1)

        start_label = QLabel("起始电压"); start_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        end_label = QLabel("终止电压"); end_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        pg.addWidget(start_label, 2, 0); pg.addWidget(end_label, 2, 1)
        self.start_spin = NoWheelDoubleSpinBox(); self.end_spin = NoWheelDoubleSpinBox()
        for sp in (self.start_spin, self.end_spin):
            sp.setMinimumWidth(0)
            sp.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            sp.setRange(-20, 20); sp.setDecimals(4); sp.setSingleStep(0.01); sp.setSuffix(" V")
            sp.valueChanged.connect(self._parameters_changed)
        self.start_spin.setValue(2.7); self.end_spin.setValue(4.5)
        pg.addWidget(self.start_spin, 3, 0); pg.addWidget(self.end_spin, 3, 1)

        scan_label = QLabel("扫描速率"); scan_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        precision_label = QLabel("切分精度"); precision_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        pg.addWidget(scan_label, 4, 0); pg.addWidget(precision_label, 4, 1)
        self.scan_spin = NoWheelDoubleSpinBox(); self.scan_spin.setMinimumWidth(0); self.scan_spin.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed); self.scan_spin.setRange(0.0001, 10000); self.scan_spin.setDecimals(4); self.scan_spin.setSuffix(" mV/s")
        self.precision_spin = NoWheelDoubleSpinBox(); self.precision_spin.setMinimumWidth(0); self.precision_spin.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed); self.precision_spin.setRange(0.1, 100); self.precision_spin.setDecimals(2); self.precision_spin.setSuffix(" mV")
        self.scan_spin.setValue(5.0); self.precision_spin.setValue(5.0)
        self.scan_spin.valueChanged.connect(self._parameters_changed); self.precision_spin.valueChanged.connect(self._parameters_changed)
        pg.addWidget(self.scan_spin, 5, 0); pg.addWidget(self.precision_spin, 5, 1)
        self.direction_hint = QLabel(); self.direction_hint.setProperty("muted", True); self.direction_hint.setWordWrap(True)
        pg.addWidget(self.direction_hint, 6, 0, 1, 2)
        apply_card_shadow(param_card); self.left_layout.addWidget(param_card)

        # Card 3: output selection
        out_card = QGroupBox("结果输出")
        out_card.setMinimumWidth(0); out_card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        ol = QGridLayout(out_card); ol.setContentsMargins(10, 13, 10, 9); ol.setHorizontalSpacing(8); ol.setVerticalSpacing(6)
        ol.setColumnStretch(0, 0); ol.setColumnStretch(1, 1)
        self.auto_radio = ModernRadioButton("自动"); self.manual_radio = ModernRadioButton("手动")
        self.output_mode_group = QButtonGroup(self); self.output_mode_group.setExclusive(True)
        self.output_mode_group.addButton(self.auto_radio); self.output_mode_group.addButton(self.manual_radio)
        # v1.9.3 默认采用手动输出，并保留“二十圈选点”预设。
        self.manual_radio.setChecked(True); self.auto_radio.toggled.connect(self._selection_mode_changed)
        ol.addWidget(QLabel("输出循环"), 0, 0, 1, 2); ol.addWidget(self.auto_radio, 1, 0); ol.addWidget(self.manual_radio, 1, 1)
        self.auto_target_spin = NoWheelSpinBox(); self.auto_target_spin.setMinimumWidth(0); self.auto_target_spin.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed); self.auto_target_spin.setRange(1, 100); self.auto_target_spin.setValue(5)
        self.preset_combo = NoWheelComboBox(); self.preset_combo.setMinimumWidth(0); self.preset_combo.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed); self.preset_combo.addItems(list(PRESET_SCHEMES.keys())); self.preset_combo.setCurrentText("二十圈选点")
        self.manual_edit = QLineEdit("1, 5, 10, 15, 20"); self.manual_edit.setMinimumWidth(0); self.manual_edit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.preset_combo.currentTextChanged.connect(self._preset_changed)
        ol.addWidget(QLabel("目标圈数"), 2, 0); ol.addWidget(self.auto_target_spin, 2, 1)
        ol.addWidget(QLabel("预设"), 3, 0); ol.addWidget(self.preset_combo, 3, 1)
        ol.addWidget(QLabel("圈数"), 4, 0); ol.addWidget(self.manual_edit, 4, 1)
        self.cut_check = ModernCheckBox("仅输出指定圈"); self.cut_check.setChecked(True)
        self.verify_check = ModernCheckBox("生成验证文件")
        ol.addWidget(self.cut_check, 5, 0, 1, 2); ol.addWidget(self.verify_check, 6, 0, 1, 2)
        apply_card_shadow(out_card); self.left_layout.addWidget(out_card)

        # Card 4: execution + collapsible log
        run_card = QGroupBox("执行与状态")
        run_card.setMinimumWidth(0); run_card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        rl = QVBoxLayout(run_card); rl.setContentsMargins(10, 13, 10, 9); rl.setSpacing(6)
        self.run_btn = QPushButton("开始处理"); self.run_btn.setProperty("primary", True); self.run_btn.setMinimumHeight(40); self.run_btn.clicked.connect(self._start_analysis)
        rl.addWidget(self.run_btn)
        self.run_status_label = QLabel("状态：就绪"); self.run_status_label.setProperty("muted", True); rl.addWidget(self.run_status_label)
        loghead = QHBoxLayout(); self.log_title_label = QLabel("运行日志")
        self.log_toggle_btn = QToolButton(); self.log_toggle_btn.setText("展开日志 ▾"); self.log_toggle_btn.setCheckable(True); self.log_toggle_btn.setChecked(False); self.log_toggle_btn.setProperty("logtoggle", True); self.log_toggle_btn.clicked.connect(self._toggle_log)
        loghead.addWidget(self.log_title_label); loghead.addStretch(1); loghead.addWidget(self.log_toggle_btn); rl.addLayout(loghead)
        self.log_edit = QPlainTextEdit(); self.log_edit.setReadOnly(True); self.log_edit.setMinimumHeight(125); self.log_edit.setVisible(False)
        self.log_edit.appendPlainText('[INFO] 就绪，拖拽文件或点击“添加文件”开始。')
        rl.addWidget(self.log_edit)
        apply_card_shadow(run_card); self.left_layout.addWidget(run_card)
        self.left_layout.addStretch(1)
        self._output_mode_changed(True); self._update_direction_hint(); self._selection_mode_changed()

    def _build_global_header(self, layout):
        top = QHBoxLayout(); top.setSpacing(8)
        top.addWidget(QLabel("当前文件"))
        self.current_file_combo = QComboBox(); self.current_file_combo.setMinimumWidth(330); self.current_file_combo.currentIndexChanged.connect(lambda idx: self._common_file_changed(self.current_file_combo))
        self.common_file_combos = [self.current_file_combo]; top.addWidget(self.current_file_combo, 1)
        self.result_mode_label = QLabel("模式：—"); self.result_mode_label.setProperty("muted", True)
        self.result_count_label = QLabel("有效循环：0"); self.result_count_label.setProperty("muted", True)
        self.result_state_label = QLabel("尚未分析"); self.result_state_label.setProperty("state", "idle")
        self.common_mode_labels = [self.result_mode_label]; self.common_count_labels = [self.result_count_label]
        top.addWidget(self.result_mode_label); top.addWidget(self.result_count_label); top.addWidget(self.result_state_label)
        layout.addLayout(top)

        cyc = QHBoxLayout(); cyc.setSpacing(7); cyc.addWidget(QLabel("显示圈数"))
        self.cycle_select_btn = self._mark_secondary(QPushButton("未选择圈数")); self.cycle_select_btn.clicked.connect(self._open_cycle_selector)
        self.common_cycle_buttons = [self.cycle_select_btn]; cyc.addWidget(self.cycle_select_btn, 1)
        b_all = self._mark_tertiary(QPushButton("全选")); b_clear = self._mark_tertiary(QPushButton("清空")); b_def = self._mark_tertiary(QPushButton("恢复默认"))
        b_all.clicked.connect(self._select_all_preview); b_clear.clicked.connect(self._clear_preview); b_def.clicked.connect(self._restore_default_preview)
        cyc.addWidget(b_all); cyc.addWidget(b_clear); cyc.addWidget(b_def); layout.addLayout(cyc)

    def _build_tabs(self):
        self.cv_tab = QWidget(); self.charge_tab = QWidget(); self.peak_tab = QWidget(); self.onset_tab = QWidget(); self.shift_tab = QWidget(); self.qc_tab = QWidget()
        self.tabs.addTab(self.cv_tab, "CV曲线"); self.tabs.addTab(self.charge_tab, "库伦电荷"); self.tabs.addTab(self.peak_tab, "峰电位"); self.tabs.addTab(self.onset_tab, "起始电位"); self.tabs.addTab(self.shift_tab, "位移"); self.tabs.addTab(self.qc_tab, "QC")
        self._build_cv_tab(); self._build_charge_tab(); self._build_peak_tab(); self._build_onset_tab(); self._build_shift_tab(); self._build_qc_tab()

    def _build_cv_tab(self):
        lay = QVBoxLayout(self.cv_tab); lay.setContentsMargins(10, 8, 10, 10); lay.setSpacing(7)

        self.diagnostic_banner = QFrame(); self.diagnostic_banner.setProperty("diagnostic", True); self.diagnostic_banner.hide()
        brow = QHBoxLayout(self.diagnostic_banner); brow.setContentsMargins(10, 6, 8, 6)
        self.diagnostic_label = QLabel("诊断模式")
        exit_btn = self._mark_tertiary(QPushButton("退出诊断")); exit_btn.clicked.connect(self._exit_diagnostic)
        brow.addWidget(self.diagnostic_label); brow.addStretch(1); brow.addWidget(exit_btn); lay.addWidget(self.diagnostic_banner)

        ctrl = QHBoxLayout(); ctrl.setSpacing(8); ctrl.addWidget(QLabel("曲线"))
        self.cv_raw = ModernRadioButton("原始数据"); self.cv_smooth = ModernRadioButton("平滑数据"); self.cv_both = ModernRadioButton("原始+平滑")
        self.cv_curve_group = QButtonGroup(self); self.cv_curve_group.setExclusive(True)
        # Set defaults before wiring refresh signals. setChecked(True) emits
        # toggled(), and the plot widget is not constructed until below.
        for w in (self.cv_raw, self.cv_smooth, self.cv_both):
            self.cv_curve_group.addButton(w); ctrl.addWidget(w)
        self.cv_raw.setChecked(True)
        ctrl.addSpacing(14); ctrl.addWidget(QLabel("扫描"))
        self.cv_analysis = ModernRadioButton("分析扫描支"); self.cv_full = ModernRadioButton("完整 CV")
        self.cv_scan_group = QButtonGroup(self); self.cv_scan_group.setExclusive(True)
        for w in (self.cv_analysis, self.cv_full):
            self.cv_scan_group.addButton(w); ctrl.addWidget(w)
        self.cv_analysis.setChecked(True)
        ctrl.addSpacing(14); ctrl.addWidget(QLabel("标记"))
        self.cv_peak = ModernCheckBox("峰电位"); self.cv_threshold = ModernCheckBox("阈值法 Onset"); self.cv_tangent = ModernCheckBox("切线法 Onset"); self.cv_legend = ModernCheckBox("图例")
        self.cv_peak.setChecked(True); self.cv_threshold.setChecked(True); self.cv_tangent.setChecked(False); self.cv_legend.setChecked(True)
        for w in (self.cv_peak, self.cv_threshold, self.cv_tangent, self.cv_legend): ctrl.addWidget(w)
        ctrl.addStretch(1); lay.addLayout(ctrl)
        self.cv_plot = MplPanel(empty_text="选择并分析 CV 文件后可在此查看多圈曲线")
        self.cv_plot.curveClicked.connect(self._plot_curve_clicked); self.cv_plot.hoverStatus.connect(self.statusBar().showMessage)
        self.plot_map["cv"] = self.cv_plot; lay.addWidget(self.cv_plot, 1)
        # Now that every CV-tab control and the plot exist, refresh signals are safe.
        for w in (self.cv_raw, self.cv_smooth, self.cv_both, self.cv_analysis, self.cv_full):
            w.toggled.connect(self._refresh_cv)
        for w in (self.cv_peak, self.cv_threshold, self.cv_tangent, self.cv_legend):
            w.stateChanged.connect(self._refresh_cv)

    def _make_plot_table_tab(self, page, control_builder, key, table_ratio=30):
        lay = QVBoxLayout(page); lay.setContentsMargins(8, 8, 8, 8); lay.setSpacing(6)
        control_builder(lay)
        split = QSplitter(Qt.Orientation.Vertical)
        plot = MplPanel(); plot.curveClicked.connect(self._plot_curve_clicked); plot.hoverStatus.connect(self.statusBar().showMessage)
        table = self._new_table(); table.itemSelectionChanged.connect(lambda k=key, t=table: self._table_selected(k, t)); table.itemDoubleClicked.connect(lambda item, k=key, t=table: self._table_double_clicked(k, t))
        split.addWidget(plot); split.addWidget(table); split.setStretchFactor(0, 1); split.setStretchFactor(1, 0)
        split.setSizes([520, 210] if table_ratio <= 30 else [480, 250])
        lay.addWidget(split, 1); self.plot_map[key] = plot; self.table_map[key] = table
        return plot, table

    def _build_charge_tab(self):
        def controls(lay):
            row = QHBoxLayout(); row.addWidget(QLabel("显示方式"))
            self.charge_bar = ModernRadioButton("柱状图"); self.charge_line = ModernRadioButton("趋势线")
            self.charge_group = QButtonGroup(self); self.charge_group.setExclusive(True); self.charge_group.addButton(self.charge_bar); self.charge_group.addButton(self.charge_line)
            self.charge_bar.setChecked(True)
            self.charge_labels = ModernCheckBox("显示数据标签"); self.charge_show_table = ModernCheckBox("显示数据表"); self.charge_show_table.setChecked(True)
            for w in (self.charge_bar, self.charge_line): w.toggled.connect(self._refresh_charge)
            self.charge_labels.stateChanged.connect(self._refresh_charge); self.charge_show_table.stateChanged.connect(lambda: self.charge_table.setVisible(self.charge_show_table.isChecked()))
            row.addWidget(self.charge_bar); row.addWidget(self.charge_line); row.addSpacing(12); row.addWidget(self.charge_labels); row.addWidget(self.charge_show_table); row.addStretch(1); lay.addLayout(row)
        self.charge_plot, self.charge_table = self._make_plot_table_tab(self.charge_tab, controls, "charge", 28)

    def _build_peak_tab(self):
        def controls(lay):
            row = QHBoxLayout(); row.addWidget(QLabel("显示指标"))
            self.peak_pot = ModernRadioButton("峰电位"); self.peak_cur = ModernRadioButton("峰电流")
            self.peak_group = QButtonGroup(self); self.peak_group.setExclusive(True); self.peak_group.addButton(self.peak_pot); self.peak_group.addButton(self.peak_cur); self.peak_pot.setChecked(True)
            self.peak_labels = ModernCheckBox("显示数据标签"); self.peak_show_table = ModernCheckBox("显示数据表"); self.peak_show_table.setChecked(True)
            for w in (self.peak_pot, self.peak_cur): w.toggled.connect(self._refresh_peak)
            self.peak_labels.stateChanged.connect(self._refresh_peak); self.peak_show_table.stateChanged.connect(lambda: self.peak_table.setVisible(self.peak_show_table.isChecked()))
            row.addWidget(self.peak_pot); row.addWidget(self.peak_cur); row.addSpacing(12); row.addWidget(self.peak_labels); row.addWidget(self.peak_show_table); row.addStretch(1); lay.addLayout(row)
        self.peak_plot, self.peak_table = self._make_plot_table_tab(self.peak_tab, controls, "peak", 32)

    def _build_onset_tab(self):
        def controls(lay):
            row = QHBoxLayout(); row.addWidget(QLabel("显示方法"))
            self.onset_thr = ModernCheckBox("阈值法 Threshold"); self.onset_tan = ModernCheckBox("切线法 Tangent"); self.onset_labels = ModernCheckBox("显示数据标签"); self.onset_show_table = ModernCheckBox("显示数据表")
            self.onset_thr.setChecked(True); self.onset_tan.setChecked(True); self.onset_show_table.setChecked(True)
            for w in (self.onset_thr, self.onset_tan, self.onset_labels): w.stateChanged.connect(self._refresh_onset)
            self.onset_show_table.stateChanged.connect(lambda: self.onset_table.setVisible(self.onset_show_table.isChecked()))
            row.addWidget(self.onset_thr); row.addWidget(self.onset_tan); row.addSpacing(12); row.addWidget(self.onset_labels); row.addWidget(self.onset_show_table); row.addStretch(1); lay.addLayout(row)
        self.onset_plot, self.onset_table = self._make_plot_table_tab(self.onset_tab, controls, "onset", 32)

    def _build_shift_tab(self):
        def controls(lay):
            row = QHBoxLayout(); row.addWidget(QLabel("参考圈")); self.ref_combo = QComboBox(); self.ref_combo.setMinimumWidth(120); self.ref_combo.currentTextChanged.connect(self._reference_changed); row.addWidget(self.ref_combo)
            row.addSpacing(12); row.addWidget(QLabel("显示"))
            self.shift_peak = ModernCheckBox("峰电位位移"); self.shift_threshold = ModernCheckBox("Threshold Onset 位移"); self.shift_tangent = ModernCheckBox("Tangent Onset 位移"); self.shift_zero = ModernCheckBox("ΔE=0 参考线"); self.shift_labels = ModernCheckBox("数据标签"); self.shift_show_table = ModernCheckBox("显示数据表")
            for w in (self.shift_peak, self.shift_threshold, self.shift_tangent, self.shift_zero, self.shift_show_table): w.setChecked(True)
            for w in (self.shift_peak, self.shift_threshold, self.shift_tangent, self.shift_zero, self.shift_labels): w.stateChanged.connect(self._refresh_shift)
            self.shift_show_table.stateChanged.connect(lambda: self.shift_table.setVisible(self.shift_show_table.isChecked()))
            for w in (self.shift_peak, self.shift_threshold, self.shift_tangent, self.shift_zero, self.shift_labels, self.shift_show_table): row.addWidget(w)
            row.addStretch(1); lay.addLayout(row)
        self.shift_plot, self.shift_table = self._make_plot_table_tab(self.shift_tab, controls, "shift", 32)

    def _build_qc_tab(self):
        lay = QVBoxLayout(self.qc_tab); lay.setContentsMargins(10, 8, 10, 10); lay.setSpacing(8)
        cards = QHBoxLayout()
        self.qc_peak_summary = QLabel("峰识别\n暂无结果"); self.qc_threshold_summary = QLabel("阈值法 Onset\n暂无结果"); self.qc_tangent_summary = QLabel("切线法 Onset\n暂无结果"); self.qc_scan_summary = QLabel("扫描方向\n暂无结果")
        for lab in (self.qc_peak_summary, self.qc_threshold_summary, self.qc_tangent_summary, self.qc_scan_summary): lab.setAlignment(Qt.AlignmentFlag.AlignCenter); lab.setMinimumHeight(76); lab.setProperty("summary", True); cards.addWidget(lab)
        lay.addLayout(cards)
        filt = QHBoxLayout(); filt.addWidget(QLabel("显示状态")); self.qc_filters = {}
        for status in (QCStatus.OK.value, QCStatus.REVIEW.value, QCStatus.BOUNDARY.value, QCStatus.FAILED.value):
            cb = ModernCheckBox(status); cb.setChecked(True); cb.stateChanged.connect(self._refresh_qc); self.qc_filters[status] = cb; filt.addWidget(cb)
        self.qc_only_abnormal = ModernCheckBox("仅显示需要检查"); self.qc_only_abnormal.stateChanged.connect(self._refresh_qc); filt.addWidget(self.qc_only_abnormal)
        reset = self._mark_tertiary(QPushButton("恢复全部")); reset.clicked.connect(self._reset_qc); filt.addWidget(reset); filt.addStretch(1); lay.addLayout(filt)
        self.qc_table = self._new_table(); self.qc_table.itemSelectionChanged.connect(lambda: self._table_selected("qc", self.qc_table)); self.qc_table.itemDoubleClicked.connect(lambda item: self._table_double_clicked("qc", self.qc_table)); self.table_map["qc"] = self.qc_table; lay.addWidget(self.qc_table, 1)

    # ------------------------- left interactions -------------------------
    def _output_mode_changed(self, checked):
        custom = not self.output_original_check.isChecked()
        self.output_edit.setEnabled(custom); self.output_browse_btn.setEnabled(custom)
        if not custom:
            self.output_edit.clear()

    def _remove_selected_files(self):
        if self._processing:
            return
        selected = {item.text() for item in self.file_list.selectedItems()}
        if not selected:
            return
        for p in list(selected):
            if p in self.file_paths: self.file_paths.remove(p)
            self.file_states.pop(p, None); self.analysis_cache.pop(p, None); self.mode_cache.pop(p, None); self.raw_curve_cache.pop(p, None)
        for i in reversed(range(self.file_list.count())):
            if self.file_list.item(i).text() in selected: self.file_list.takeItem(i)
        self._sync_file_combos(self.file_paths)
        if self.current_preview_path in selected:
            self.current_preview_path = self.file_paths[0] if self.file_paths else None
            if self.current_preview_path: self._activate_preview(self.current_preview_path, store_previous=False)
            else: self._refresh_common_labels(); self._refresh_current_tab()

    def _toggle_log(self, checked=None):
        expanded = self.log_toggle_btn.isChecked()
        self.log_edit.setVisible(expanded)
        self.log_toggle_btn.setText("收起日志 ▴" if expanded else "展开日志 ▾")

    def _set_log_expanded(self, expanded):
        self.log_toggle_btn.setChecked(bool(expanded)); self._toggle_log()

    def _update_log_header(self):
        total = self._warning_count + self._error_count
        self.log_title_label.setText(f"运行日志 ({total})" if total else "运行日志")

    def _update_direction_hint(self):
        if self.max_radio.isChecked(): self.direction_hint.setText("正扫：终止电压 > 起始电压")
        else: self.direction_hint.setText("负扫：终止电压 < 起始电压")

    def _mode_changed(self, checked=True):
        if not checked:
            return
        if not self._loading_params:
            if self.max_radio.isChecked(): self.start_spin.setValue(2.7); self.end_spin.setValue(4.5)
            else: self.start_spin.setValue(3.0); self.end_spin.setValue(0.01)
        self._update_direction_hint(); self._parameters_changed()

    def _pick_output(self):
        p = QFileDialog.getExistingDirectory(self, "选择输出目录", self.output_edit.text() or str(Path.cwd()))
        if p:
            self.output_original_check.setChecked(False); self.output_edit.setText(p)

    def _add_files(self, paths):
        if self._processing:
            return
        added = []
        for p in paths:
            p = str(Path(p))
            if Path(p).suffix.lower() not in SUPPORTED_EXTENSIONS or p in self.file_paths:
                continue
            self.file_paths.append(p); self.file_list.addItem(p); self.file_states[p] = FileState(path=p, draft_params=self._analysis_parameter_values()); added.append(p)
        if added:
            self._sync_file_combos(self.file_paths)
            if not self.current_preview_path:
                self._activate_preview(added[0], store_previous=False)
            self._log("INFO", f"已添加 {len(added)} 个文件。")

    def _clear_files(self):
        if self._processing:
            return
        self.file_paths.clear(); self.file_states.clear(); self.analysis_cache.clear(); self.mode_cache.clear(); self.raw_curve_cache.clear(); self.default_selection_cache.clear(); self.preview_selection_cache.clear()
        self.file_list.clear(); self.current_preview_path = None; self.current_focus_curve = None; self.temporary_curve = None; self.diagnostic_context = None
        self._sync_file_combos([]); self._refresh_common_labels(); self._refresh_current_tab(); self._log("INFO", "已清空输入文件列表。")

    # ------------------------- processing -------------------------
    def _start_analysis(self):
        ok, msg = self._validate_params()
        if not ok:
            QMessageBox.warning(self, "参数检查", msg); return
        params = {
            "mode": "max" if self.max_radio.isChecked() else "min",
            "scan_rate_mv": self.scan_spin.value(), "precision_mv": self.precision_spin.value(),
            "start_voltage": self.start_spin.value(), "end_voltage": self.end_spin.value(),
            "save_verification": self.verify_check.isChecked(),
            "selection_mode": "auto" if self.auto_radio.isChecked() else "manual",
            "auto_target": self.auto_target_spin.value(), "manual_indices": self._manual_indices(),
            "apply_cut_to_all": self.cut_check.isChecked(),
            "output_dir": None if self.output_original_check.isChecked() else (self.output_edit.text().strip() or None),
        }
        self._active_params = dict(params)
        snapshot = {k: params[k] for k in ("mode", "start_voltage", "end_voltage", "scan_rate_mv", "precision_mv")}
        for p in self.file_paths:
            st = self._ensure_file_state(p); st.status = AnalysisStatus.PROCESSING; st.draft_params = dict(snapshot)
        self._processing = True; self._set_processing_ui(True); self._warning_count = 0; self._error_count = 0; self._update_log_header(); self.log_edit.clear(); self.run_status_label.setText("状态：正在处理")
        self.statusBar().showMessage("正在处理，请稍候..."); self._refresh_common_labels()
        self.worker = ProcessingWorker(self.file_paths, params, self); self.worker.log.connect(self._log); self.worker.finishedData.connect(self._analysis_finished); self.worker.failedFatal.connect(self._fatal_worker_error); self.worker.start()

    def _set_processing_ui(self, processing):
        self.run_btn.setEnabled(not processing)
        for w in (self.file_list, self.current_file_combo, self.max_radio, self.min_radio, self.start_spin, self.end_spin, self.scan_spin, self.precision_spin):
            w.setEnabled(not processing)

    def _log(self, level, msg):
        self.log_edit.appendPlainText(f"[{level}] {msg}")
        if level == "WARNING": self._warning_count += 1
        if level == "ERROR": self._error_count += 1; self._set_log_expanded(True)
        self._update_log_header(); self.statusBar().showMessage(str(msg))

    def _fatal_worker_error(self, text):
        self._processing = False; self._set_processing_ui(False); self.run_status_label.setText("状态：分析失败"); self._set_log_expanded(True)
        for p in self.file_paths:
            st = self._ensure_file_state(p)
            if st.status == AnalysisStatus.PROCESSING: st.status = AnalysisStatus.FAILED; st.last_error = text
        self._refresh_common_labels(); QMessageBox.critical(self, "分析失败", text)

    def _analysis_finished(self, results, errors):
        self._processing = False; self._set_processing_ui(False)
        snapshot = {k: self._active_params[k] for k in ("mode", "start_voltage", "end_voltage", "scan_rate_mv", "precision_mv")} if self._active_params else self._analysis_parameter_values()
        for path, info in results.items():
            self.analysis_cache[path] = info["df_all"].copy(); self.mode_cache[path] = info["mode"]
            # Reuse the exact raw CURVE mapping parsed during successful analysis.
            # This removes the CV tab's normal-path dependency on a second disk parse
            # and overwrites any stale/empty preview cache from an earlier attempt.
            raw_curves = info.get("raw_curves") or {}
            if raw_curves:
                self.raw_curve_cache[path] = raw_curves
            else:
                self.raw_curve_cache.pop(path, None)
            defaults = [str(x) for x in info["df_filtered"].get("Curve", pd.Series([], dtype=str)).tolist()]
            self.default_selection_cache[path] = defaults; self.preview_selection_cache[path] = set(defaults)
            st = self._ensure_file_state(path); st.parameter_snapshot = dict(snapshot); st.draft_params = dict(snapshot); st.default_cycles = list(defaults); st.selected_cycles = set(defaults); st.status = AnalysisStatus.READY; st.last_error = None
            if not st.reference_curve or st.reference_curve not in set(info["df_all"].get("Curve", [])):
                st.reference_curve = "CURVE1" if "CURVE1" in set(info["df_all"].get("Curve", [])) else (str(info["df_all"].iloc[0]["Curve"]) if len(info["df_all"]) else None)
        for path, err in errors.items():
            st = self._ensure_file_state(path); st.status = AnalysisStatus.FAILED; st.last_error = str(err)
        self._sync_file_combos(self.file_paths)
        if results:
            preferred = self.current_preview_path if self.current_preview_path in results else next(iter(results))
            self._activate_preview(preferred, store_previous=False)
        self.run_status_label.setText(f"状态：完成 · 成功 {len(results)} · 失败 {len(errors)}")
        self._refresh_common_labels(); self._refresh_current_tab()
        if errors:
            text = "\n".join(f"{Path(p).name}：{e}" for p, e in errors.items()); QMessageBox.warning(self, "部分文件处理失败", text)
        elif results:
            self._show_toast(f"分析完成 · {len(results)} 个文件已保存", "success", 3200)

    # ------------------------- file context / display cycles -------------------------
    def _sync_file_combos(self, paths=None):
        paths = list(self.file_paths if paths is None else paths)
        self._building_common = True
        try:
            for combo in self.common_file_combos:
                current = self.current_preview_path
                combo.clear()
                for p in paths: combo.addItem(Path(p).name, p)
                if current:
                    idx = combo.findData(current)
                    if idx >= 0: combo.setCurrentIndex(idx)
        finally:
            self._building_common = False

    def _common_file_changed(self, combo):
        if self._building_common or self._processing:
            return
        p = combo.currentData()
        if p and p != self.current_preview_path:
            self._activate_preview(p)

    def _activate_preview(self, path, store_previous=True):
        if path not in self.file_paths:
            return
        if store_previous:
            self._store_current_draft()
        self._exit_diagnostic(refresh=False)
        self.current_preview_path = path; self.current_focus_curve = None; self.temporary_curve = None
        st = self._ensure_file_state(path)
        params = st.draft_params or st.parameter_snapshot
        if params:
            self._load_params_to_controls(params)
        self._building_common = True
        try:
            idx = self.current_file_combo.findData(path)
            if idx >= 0: self.current_file_combo.setCurrentIndex(idx)
        finally:
            self._building_common = False
        self._refresh_common_labels(); self._refresh_reference_combo(); self._refresh_current_tab()

    def _refresh_common_labels(self):
        p = self.current_preview_path
        if not p:
            self.result_mode_label.setText("模式：—"); self.result_count_label.setText("有效循环：0"); self.result_state_label.setText("尚未分析"); self.result_state_label.setProperty("state", "idle"); self.result_state_label.style().unpolish(self.result_state_label); self.result_state_label.style().polish(self.result_state_label); self.cycle_select_btn.setText("未选择圈数"); return
        st = self._ensure_file_state(p); status = self._update_file_status(p)
        if p in self.analysis_cache:
            mode = self.mode_cache.get(p, "max"); sm = ScanMode.MAX if mode == "max" else ScanMode.MIN; self.result_mode_label.setText(f"结果模式：{sm.display}"); self.result_count_label.setText(f"有效循环：{len(self.analysis_cache[p])}")
        else:
            draft_mode = (st.draft_params or self._analysis_parameter_values()).get("mode", "max"); sm = ScanMode.MAX if draft_mode == "max" else ScanMode.MIN; self.result_mode_label.setText(f"计划模式：{sm.display}"); self.result_count_label.setText("有效循环：0")
        text, prop = self._status_text(p); self.result_state_label.setText(text); self.result_state_label.setProperty("state", prop); self.result_state_label.style().unpolish(self.result_state_label); self.result_state_label.style().polish(self.result_state_label)
        formal = sorted(st.selected_cycles, key=self.curve_no)
        txt = ", ".join(c.replace("CURVE", "") for c in formal) if formal else "未选择圈数"
        if self.temporary_curve and self.temporary_curve not in st.selected_cycles: txt += f"  + 临时：{self.temporary_curve.replace('CURVE','')}"
        self.cycle_select_btn.setText(txt)
        if status == AnalysisStatus.OUTDATED:
            self.run_status_label.setText("状态：参数已修改，右侧仍显示上一次分析结果")
        elif status == AnalysisStatus.READY:
            self.run_status_label.setText("状态：结果已就绪")
        elif status == AnalysisStatus.NOT_ANALYZED:
            self.run_status_label.setText("状态：尚未分析")
        elif status == AnalysisStatus.FAILED:
            self.run_status_label.setText("状态：最近一次分析失败")

    def _valid_curve_names(self):
        p = self.current_preview_path
        if not p or p not in self.analysis_cache: return []
        return sorted([str(x) for x in self.analysis_cache[p]["Curve"].dropna().tolist()], key=self.curve_no)

    def _open_cycle_selector(self):
        names = self._valid_curve_names()
        if not names: QMessageBox.information(self, "选择显示圈数", "当前文件尚未产生可选循环。") ; return
        st = self._ensure_file_state(self.current_preview_path); dlg = CycleSelectorDialog(names, st.selected_cycles, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self._exit_diagnostic(refresh=False); st.selected_cycles = set(dlg.selected_curves()); self.preview_selection_cache[self.current_preview_path] = set(st.selected_cycles); self._refresh_common_labels(); self._refresh_current_tab()

    def _select_all_preview(self):
        if self.current_preview_path and self.current_preview_path in self.analysis_cache:
            self._exit_diagnostic(refresh=False); st = self._ensure_file_state(self.current_preview_path); st.selected_cycles = set(self._valid_curve_names()); self.preview_selection_cache[self.current_preview_path] = set(st.selected_cycles); self._refresh_common_labels(); self._refresh_current_tab()

    def _clear_preview(self):
        if self.current_preview_path and self.current_preview_path in self.analysis_cache:
            self._exit_diagnostic(refresh=False); st = self._ensure_file_state(self.current_preview_path); st.selected_cycles = set(); self.preview_selection_cache[self.current_preview_path] = set(); self._refresh_common_labels(); self._refresh_current_tab()

    def _restore_default_preview(self):
        if self.current_preview_path and self.current_preview_path in self.analysis_cache:
            self._exit_diagnostic(refresh=False); st = self._ensure_file_state(self.current_preview_path); st.selected_cycles = set(st.default_cycles); self.preview_selection_cache[self.current_preview_path] = set(st.selected_cycles); self._refresh_common_labels(); self._refresh_current_tab()

    def _effective_selected_curves(self):
        p = self.current_preview_path
        if not p: return set()
        selected = set(self._ensure_file_state(p).selected_cycles)
        if self.temporary_curve: selected.add(self.temporary_curve)
        return selected

    def _selected_df(self):
        p = self.current_preview_path
        if not p or p not in self.analysis_cache: return pd.DataFrame()
        selected = self._effective_selected_curves(); df = self.analysis_cache[p]
        return df[df["Curve"].isin(selected)].copy().sort_values("Curve", key=lambda s: s.map(self.curve_no)) if selected else df.iloc[0:0].copy()

    # ------------------------- refresh -------------------------
    def _refresh_current_tab(self, *args):
        # During construction QTabWidget/control signals may fire before all
        # page widgets exist. Ignore those early refreshes.
        if not hasattr(self, "tabs"):
            return
        funcs = [self._refresh_cv, self._refresh_charge, self._refresh_peak, self._refresh_onset, self._refresh_shift, self._refresh_qc]
        idx = self.tabs.currentIndex()
        if 0 <= idx < len(funcs):
            funcs[idx]()

    def _refresh_cv(self, *args):
        """Refresh CV curves and feature markers using analysis-branch marker coordinates."""
        if not hasattr(self, "cv_plot"):
            return
        panel = self.cv_plot; p = self.current_preview_path
        try:
            dfres = self._selected_df()
            if not p or p not in self.analysis_cache:
                panel.show_empty(self._empty_message()); return
            if dfres.empty:
                panel.show_empty("当前没有选择显示圈数"); return

            curves = self._load_raw_curves(p)
            mode = self.mode_cache.get(p, "max"); cols = self.mode_columns(mode)
            selected = sorted(self._effective_selected_curves(), key=self.curve_no)
            raw_keys = sorted(map(str, curves.keys()), key=self.curve_no) if curves else []
            missing = [c for c in selected if c not in curves]
            signature = (
                p, tuple(selected), tuple(raw_keys), mode,
                self.cv_full.isChecked(), self.cv_raw.isChecked(), self.cv_smooth.isChecked(), self.cv_both.isChecked(),
                self.cv_peak.isChecked(), self.cv_threshold.isChecked(), self.cv_tangent.isChecked(), self.cv_legend.isChecked(),
            )
            if signature != self._last_cv_refresh_signature:
                self._last_cv_refresh_signature = signature
                self._log("INFO", f"CV刷新：当前文件 {Path(p).name}")
                self._log("INFO", f"CV刷新：选择曲线 {', '.join(selected) or '无'}；原始缓存 {len(raw_keys)} 条")
                self._log("INFO", f"CV标记：Peak={self.cv_peak.isChecked()}，Threshold={self.cv_threshold.isChecked()}，Tangent={self.cv_tangent.isChecked()}，Legend={self.cv_legend.isChecked()}")
                if missing: self._log("WARNING", f"CV刷新：原始数据缺失：{', '.join(missing)}")
            if not curves:
                panel.show_empty("原始 CV 曲线读取失败或未解析到有效 CURVE\n请查看左侧运行日志"); return

            ax = panel.prepare("CV 曲线\nCV Curves", "电位 / Potential (V)", "电流 / Current (A)")
            gradient = matplotlib.colormaps.get_cmap("cool")
            color_map = {c: gradient(0.12 + 0.76*i/max(len(selected)-1,1)) for i,c in enumerate(selected)}
            result_map = {str(r["Curve"]): r for _, r in dfres.iterrows()}
            plotted_curve_count = 0; skipped = []; marker_counts = {"peak":0,"threshold":0,"tangent":0}
            smooth_needed = self.cv_smooth.isChecked() or self.cv_both.isChecked()

            for curve in selected:
                try:
                    if curve not in curves:
                        skipped.append(f"{curve}: raw missing"); continue
                    raw_curve = curves[curve]
                    prepared = prepare_cv_curve_for_plot(raw_curve, mode, full_scan=self.cv_full.isChecked(), smooth=smooth_needed)
                    v = prepared["v"]; i_raw = prepared["i_raw"]; i_smooth = prepared["i_smooth"]
                    if prepared.get("scan_warning"): self._log("WARNING", f"{curve}：{prepared['scan_warning']}")
                    color = color_map[curve]; focus = curve == self.current_focus_curve; curve_plotted = False

                    if self.cv_raw.isChecked() or self.cv_both.isChecked():
                        ln, = ax.plot(v, i_raw, color=color, lw=2.7 if focus else 1.9,
                                      alpha=0.98 if focus else 0.86, label=curve, antialiased=True)
                        panel.register(ln, curve, curve, f"已选中 {curve}",
                                       tooltip_fn=lambda ev, cc=curve, mm=mode:
                                           format_cv_tooltip(cc, ev.xdata, ev.ydata, mm)
                                           if ev.xdata is not None and ev.ydata is not None else cc)
                        curve_plotted = True
                    if smooth_needed and i_smooth is not None and len(i_smooth)==len(v):
                        label = curve if self.cv_smooth.isChecked() else "_nolegend_"
                        ln, = ax.plot(v, i_smooth, color=color, lw=2.4 if focus else 1.7,
                                      ls="--" if self.cv_both.isChecked() else "-", alpha=0.9, label=label)
                        panel.register(ln, curve, curve, f"已选中 {curve}"); curve_plotted = True
                    elif self.cv_smooth.isChecked():
                        skipped.append(f"{curve}: 平滑结果不可用")
                    if curve_plotted: plotted_curve_count += 1

                    row = result_map.get(curve)
                    if row is None: continue
                    specs = build_cv_marker_positions(
                        raw_curve, row, mode, cols,
                        show_peak=self.cv_peak.isChecked(),
                        show_threshold=self.cv_threshold.isChecked(),
                        show_tangent=self.cv_tangent.isChecked(),
                    )
                    for spec in specs:
                        kind = spec["kind"]; mx=float(spec["x"]); my=float(spec["y"])
                        if kind == "peak":
                            status = self.normalize_status(row.get("Peak_status")); marker="^"; size=96; face="#F59E0B"
                            tooltip = format_peak_tooltip(curve, mx, my, status, mode)
                            status_text = f"{curve}｜Peak {mx:.4f} V"
                        elif kind == "threshold":
                            status = self.normalize_status(row.get("Threshold_QC")); marker="o"; size=82; face="#2A7DE1"
                            tooltip = format_onset_tooltip(curve, row.get(cols["threshold"]), row.get(cols["tangent"]), row.get("Onset_difference (mV)"), self.normalize_status(row.get("Threshold_QC")), self.normalize_status(row.get("Tangent_QC")))
                            status_text = f"{curve}｜Threshold onset {mx:.4f} V｜QC {status}"
                        else:
                            status = self.normalize_status(row.get("Tangent_QC")); marker="D"; size=78; face="#00B4A0"
                            tooltip = format_onset_tooltip(curve, row.get(cols["threshold"]), row.get(cols["tangent"]), row.get("Onset_difference (mV)"), self.normalize_status(row.get("Threshold_QC")), self.normalize_status(row.get("Tangent_QC")))
                            status_text = f"{curve}｜Tangent onset {mx:.4f} V｜QC {status}"
                        edge = STATUS_COLORS.get(status, "#334155")
                        sc = ax.scatter([mx],[my],marker=marker,s=size,facecolors=face,edgecolors=edge,
                                        linewidths=2.1,zorder=9,alpha=0.98)
                        panel.register(sc,curve,tooltip,status_text); marker_counts[kind]+=1
                except Exception as exc:
                    skipped.append(f"{curve}: {exc}"); self._log("ERROR", f"CV绘图 {curve} 失败：{exc}")

            if skipped: self._log("WARNING", "CV刷新：跳过/降级：" + "；".join(skipped))
            if plotted_curve_count == 0:
                self._log("ERROR", f"CV刷新：成功绘制 0 条。selected={selected}; raw_keys={raw_keys}; missing={missing}")
                panel.show_empty("未找到可绘制的原始 CV 曲线\n请检查运行日志中的 selected / raw_keys / missing"); return

            extra_h=[]; extra_l=[]
            if self.cv_both.isChecked():
                extra_h.extend([Line2D([0],[0],color=panel._colors["text"],lw=2.0,ls="-"),
                                Line2D([0],[0],color=panel._colors["text"],lw=2.0,ls="--")])
                extra_l.extend(["实线：原始数据","虚线：平滑数据"])
            if self.cv_peak.isChecked():
                extra_h.append(Line2D([0],[0],marker="^",ls="",markerfacecolor="#F59E0B",markeredgecolor="#64748B",markersize=7)); extra_l.append("峰电位")
            if self.cv_threshold.isChecked():
                extra_h.append(Line2D([0],[0],marker="o",ls="",markerfacecolor="#2A7DE1",markeredgecolor="#64748B",markersize=6.5)); extra_l.append("阈值法 Onset")
            if self.cv_tangent.isChecked():
                extra_h.append(Line2D([0],[0],marker="D",ls="",markerfacecolor="#00B4A0",markeredgecolor="#64748B",markersize=6)); extra_l.append("切线法 Onset")
            panel.apply_legend(enabled=self.cv_legend.isChecked(), extra_handles=extra_h, extra_labels=extra_l)
            panel.draw()
            self._log("INFO", f"CV刷新：成功绘制 {plotted_curve_count} 条；标记 Peak={marker_counts['peak']}、Threshold={marker_counts['threshold']}、Tangent={marker_counts['tangent']}。")
        except Exception as exc:
            self._log("ERROR", f"CV绘图失败：{exc}")
            self.log_edit.appendPlainText(traceback.format_exc(limit=5))
            panel.show_empty("CV 绘图发生异常\n请查看左侧运行日志")

    def _refresh_charge(self, *args):
        df = self._selected_df(); panel = self.charge_plot
        if df.empty:
            panel.show_empty(self._empty_message() if self.current_preview_path not in self.analysis_cache else "当前没有选择显示圈数")
            self._fill_table(self.charge_table, pd.DataFrame(), [])
            return
        mode=self.mode_cache.get(self.current_preview_path,"max"); cols=self.mode_columns(mode)
        cn="氧化库伦电荷" if mode=="max" else "还原库伦电荷"; en="Oxidation Charge" if mode=="max" else "Reduction Charge"
        ax=panel.prepare(f"{cn}随循环变化\n{en} vs. Cycle","循环圈数 / Cycle",cols["charge"])
        x=np.array([self.curve_no(c) for c in df["Curve"]],float)
        q=pd.to_numeric(df[cols["charge"]],errors="coerce").to_numpy(float); valid=np.isfinite(q)
        colors=[matplotlib.colormaps.get_cmap("cool")(0.18+0.7*i/max(len(x)-1,1)) for i in range(len(x))]
        label_items=[]
        if self.charge_bar.isChecked():
            bars=ax.bar(x[valid],q[valid],width=.62,color=[colors[i] for i in np.where(valid)[0]],edgecolor="none",alpha=.92)
            for rect,(_,row),val in zip(bars,df.loc[valid].iterrows(),q[valid]):
                curve=str(row["Curve"]); val=float(val)
                panel.register(rect,curve,f"{curve}\n{cn}：{val:.3E} C",f"{curve}｜{val:.3E} C")
                if self.charge_labels.isChecked():
                    label_items.append({"x":rect.get_x()+rect.get_width()/2.0,"y":val,"text":f"{val:.2E}","color":panel._colors["text"],"preferred":"up" if val>=0 else "down"})
        else:
            ax.plot(x,q,lw=2.1,marker="o",color="#2A7DE1",antialiased=True)
            for xi,yi,(_,row) in zip(x,q,df.iterrows()):
                if not np.isfinite(yi): continue
                curve=str(row["Curve"]); sc=ax.scatter([xi],[yi],s=55,color="#2A7DE1",zorder=5)
                panel.register(sc,curve,f"{curve}\n{cn}：{yi:.3E} C",f"{curve}｜{yi:.3E} C")
                if self.charge_labels.isChecked():
                    label_items.append({"x":xi,"y":yi,"text":f"{yi:.2E}","color":"#2A7DE1","preferred":"up"})
        ax.set_xticks(x)
        if label_items: panel.add_smart_labels(label_items,fontsize=8.1)
        panel.draw(); self._fill_table(self.charge_table,df,["Curve",cols["charge"]])

    def _refresh_reference_combo(self):
        if not hasattr(self,"ref_combo"): return
        names=self._valid_curve_names(); st=self._ensure_file_state(self.current_preview_path) if self.current_preview_path else None; desired=st.reference_curve if st else None
        self.ref_combo.blockSignals(True); self.ref_combo.clear(); self.ref_combo.addItems(names)
        if desired in names: self.ref_combo.setCurrentText(desired)
        elif "CURVE1" in names: self.ref_combo.setCurrentText("CURVE1")
        elif names: self.ref_combo.setCurrentIndex(0)
        if st and self.ref_combo.currentText(): st.reference_curve=self.ref_combo.currentText()
        self.ref_combo.blockSignals(False)

    def _reference_changed(self, text):
        if text and self.current_preview_path:
            self._ensure_file_state(self.current_preview_path).reference_curve=text; self.statusBar().showMessage(TEXT["reference_changed"].format(reference=text)); self._refresh_shift()

    # ------------------------- diagnostic linkage -------------------------
    def _enter_diagnostic(self, curve, source="QC"):
        if not self.current_preview_path or self.current_preview_path not in self.analysis_cache:
            return
        if self.diagnostic_context is None:
            self.diagnostic_context = {
                "peak": self.cv_peak.isChecked(), "threshold": self.cv_threshold.isChecked(), "tangent": self.cv_tangent.isChecked(),
                "focus": self.current_focus_curve,
            }
        self.temporary_curve = curve if curve not in self._ensure_file_state(self.current_preview_path).selected_cycles else None
        self.current_focus_curve = curve
        rowdf=self.analysis_cache[self.current_preview_path]; match=rowdf[rowdf["Curve"]==curve]
        reason=[]
        if not match.empty:
            row=match.iloc[0]; pst=self.normalize_status(row.get("Peak_status")); tst=self.normalize_status(row.get("Threshold_QC")); gst=self.normalize_status(row.get("Tangent_QC"))
            if pst!=QCStatus.OK.value: self.cv_peak.setChecked(True); reason.append(f"Peak {pst}")
            if tst!=QCStatus.OK.value: self.cv_threshold.setChecked(True); reason.append(f"Threshold {tst}")
            if gst!=QCStatus.OK.value: self.cv_tangent.setChecked(True); reason.append(f"Tangent {gst}")
        if not reason: self.cv_peak.setChecked(True); self.cv_threshold.setChecked(True); reason=[source]
        self.diagnostic_label.setText(f"正在检查 {curve} · {' / '.join(reason)}")
        self.diagnostic_banner.show(); self.tabs.setCurrentWidget(self.cv_tab); self._refresh_common_labels(); self._refresh_cv(); self.statusBar().showMessage(f"已进入 {curve} 诊断视图")

    def _exit_diagnostic(self, refresh=True):
        if self.diagnostic_context:
            ctx=self.diagnostic_context
            if hasattr(self,"cv_peak"): self.cv_peak.setChecked(ctx.get("peak",True)); self.cv_threshold.setChecked(ctx.get("threshold",True)); self.cv_tangent.setChecked(ctx.get("tangent",False))
            self.current_focus_curve=ctx.get("focus")
        self.diagnostic_context=None; self.temporary_curve=None
        if hasattr(self,"diagnostic_banner"): self.diagnostic_banner.hide()
        if refresh:
            self._refresh_common_labels(); self._refresh_current_tab()

    def _plot_curve_clicked(self, curve, double_click):
        self.current_focus_curve=curve
        if double_click: self._enter_diagnostic(curve,"图表定位")
        else: self._refresh_current_tab(); self.statusBar().showMessage(f"已选中 {curve}")

    def _table_double_clicked(self, key, table):
        row = table.currentRow()
        if row < 0: return
        item=table.item(row,0); curve=item.text() if item else ""
        if curve.startswith("CURVE"):
            self._enter_diagnostic(curve,"QC" if key=="qc" else "结果定位")

    def _table_selected(self, key, table):
        row = table.currentRow()
        if row < 0 or table.columnCount()==0: return
        item=table.item(row,0); curve=item.text() if item else ""
        if curve.startswith("CURVE"): self.current_focus_curve=curve; self.statusBar().showMessage(f"已选中 {curve}")

    # ------------------------- misc -------------------------
    def _about(self):
        QMessageBox.information(self,"关于","Electrolyte CV Processor v2.0\n\n科研 CV 分析、双方法 Onset、可复制结果表、中文图表工具栏与可拖动自适应图例。")

    def closeEvent(self, event):
        try:
            self.settings.setValue("splitter_state", self.main_splitter.saveState())
            self.settings.setValue("theme", self.theme)
            # Save only non-file UI state. File list/results/selection/focus are intentionally excluded.
            defaults = self.settings_manager.load_defaults()
            session = self._capture_preference_profile(defaults)
            session["startup_behavior"] = defaults["startup_behavior"]
            self.settings_manager.save_last_session(session)
        except Exception:
            pass
        super().closeEvent(event)
