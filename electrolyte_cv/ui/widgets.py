from __future__ import annotations

from ..i18n import tr

import traceback
from pathlib import Path
import numpy as np

from .qt_compat import *
from ..core.config import SUPPORTED_EXTENSIONS
from ..core.logging_utils import set_log_callback
from ..core.processor import process_cv_file
from ..core.plot_helpers import smart_label_layout, adaptive_legend_layout

require_qt()

def configure_matplotlib_fonts():
    """Choose a CJK-capable font on the current OS and apply it globally."""
    try:
        from matplotlib import rcParams
        from matplotlib import font_manager
        available = {f.name for f in font_manager.fontManager.ttflist}
        candidates = [
            "Microsoft YaHei", "Microsoft YaHei UI", "PingFang SC",
            "Noto Sans CJK SC", "Source Han Sans SC", "SimHei",
            "WenQuanYi Micro Hei", "Segoe UI", "Arial Unicode MS", "DejaVu Sans"
        ]
        chosen = next((name for name in candidates if name in available), "DejaVu Sans")
        rcParams["font.family"] = "sans-serif"
        rcParams["font.sans-serif"] = [chosen, "DejaVu Sans"]
        rcParams["axes.unicode_minus"] = False
        return chosen
    except Exception:
        return "DejaVu Sans"


MATPLOTLIB_FONT = configure_matplotlib_fonts()


# Shared geometry for custom indicator controls.  All numbers are logical Qt pixels;
# Qt 6 scales them with the application DPI while text width comes from QFontMetrics.
_INDICATOR_SIZE = 18.0
_INDICATOR_LEFT_MARGIN = 2.0
_INDICATOR_TEXT_SPACING = 7.0
_INDICATOR_RIGHT_PADDING = 8.0
_INDICATOR_VERTICAL_PADDING = 4.0
_INDICATOR_MIN_HEIGHT = 28


def _indicator_button_size(widget):
    """Return a DPI-aware size that exactly matches our custom paint geometry."""
    fm = widget.fontMetrics()
    text_width = fm.horizontalAdvance(widget.text())
    text_height = fm.height()
    width = int(round(
        _INDICATOR_LEFT_MARGIN
        + _INDICATOR_SIZE
        + _INDICATOR_TEXT_SPACING
        + text_width
        + _INDICATOR_RIGHT_PADDING
    ))
    height = max(
        _INDICATOR_MIN_HEIGHT,
        int(round(text_height + 2.0 * _INDICATOR_VERTICAL_PADDING)),
        int(round(_INDICATOR_SIZE + 2.0 * _INDICATOR_VERTICAL_PADDING)),
    )
    return QSize(width, height)


def _indicator_and_text_rects(widget):
    """Geometry shared by sizeHint/minimumSizeHint and paintEvent."""
    h = float(widget.height())
    indicator = QRectF(
        _INDICATOR_LEFT_MARGIN,
        (h - _INDICATOR_SIZE) / 2.0,
        _INDICATOR_SIZE,
        _INDICATOR_SIZE,
    )
    text_left = _INDICATOR_LEFT_MARGIN + _INDICATOR_SIZE + _INDICATOR_TEXT_SPACING
    text_width = max(0.0, float(widget.width()) - text_left - _INDICATOR_RIGHT_PADDING)
    text_rect = QRectF(text_left, 0.0, text_width, h)
    return indicator, text_rect


class ModernCheckBox(QCheckBox):
    """Custom checkbox with DPI-aware text sizing and a crisp theme-safe check mark."""

    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setAttribute(Qt.WidgetAttribute.WA_Hover, True)
        self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

    def sizeHint(self):
        return _indicator_button_size(self)

    def minimumSizeHint(self):
        # A real minimum is important here: shrinking below this width would clip
        # the final characters because paintEvent intentionally never elides text.
        return _indicator_button_size(self)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        box, text_rect = _indicator_and_text_rects(self)
        enabled = self.isEnabled()
        checked = self.isChecked()
        hover = self.underMouse()
        theme = getattr(self.window(), "theme", "light")
        dark = theme == "dark"

        if not enabled:
            border_color = QColor("#475569" if dark else "#CBD5E1")
        elif checked or hover:
            border_color = QColor("#4C8DFF" if dark else "#2A7DE1")
        else:
            border_color = QColor("#64748B" if dark else "#94A3B8")

        if checked:
            fill = QColor("#2A7DE1")
        elif not enabled:
            fill = QColor("#334155" if dark else "#E2E8F0")
        elif hover:
            fill = QColor("#243047" if dark else "#F8FAFC")
        else:
            fill = QColor("#1E293B" if dark else "#FFFFFF")

        painter.setPen(QPen(border_color, 1.5))
        painter.setBrush(QBrush(fill))
        painter.drawRoundedRect(box, 4.0, 4.0)

        if checked:
            check_pen = QPen(QColor("#FFFFFF"))
            check_pen.setWidthF(2.5)
            check_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            check_pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
            painter.setPen(check_pen)
            painter.drawLine(
                int(round(box.left() + 4.0)), int(round(box.center().y())),
                int(round(box.left() + 8.0)), int(round(box.bottom() - 4.0)),
            )
            painter.drawLine(
                int(round(box.left() + 8.0)), int(round(box.bottom() - 4.0)),
                int(round(box.right() - 3.0)), int(round(box.top() + 4.0)),
            )

        painter.setPen(
            self.palette().color(self.foregroundRole())
            if enabled else QColor("#94A3B8")
        )
        painter.setFont(self.font())
        painter.drawText(
            text_rect,
            Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
            self.text(),
        )


class ModernRadioButton(QRadioButton):
    """Custom radio button whose requested width is based on the real text metrics."""

    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setAttribute(Qt.WidgetAttribute.WA_Hover, True)
        self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

    def sizeHint(self):
        return _indicator_button_size(self)

    def minimumSizeHint(self):
        return _indicator_button_size(self)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        outer, text_rect = _indicator_and_text_rects(self)
        enabled = self.isEnabled()
        checked = self.isChecked()
        hover = self.underMouse()
        theme = getattr(self.window(), "theme", "light")
        dark = theme == "dark"

        if not enabled:
            border_color = QColor("#475569" if dark else "#CBD5E1")
        elif checked or hover:
            border_color = QColor("#4C8DFF" if dark else "#2A7DE1")
        else:
            border_color = QColor("#64748B" if dark else "#94A3B8")
        fill_color = QColor("#1E293B" if dark else "#FFFFFF")
        if not enabled:
            fill_color = QColor("#334155" if dark else "#F1F5F9")
        elif hover and not checked:
            fill_color = QColor("#243047" if dark else "#F8FAFC")

        pen = QPen(border_color)
        pen.setWidthF(1.8)
        painter.setPen(pen)
        painter.setBrush(QBrush(fill_color))
        painter.drawEllipse(outer)

        if checked:
            inset = 5.0
            inner = QRectF(
                outer.left() + inset,
                outer.top() + inset,
                outer.width() - 2.0 * inset,
                outer.height() - 2.0 * inset,
            )
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(QColor("#2A7DE1")))
            painter.drawEllipse(inner)

        painter.setPen(
            self.palette().color(self.foregroundRole())
            if enabled else QColor("#94A3B8")
        )
        painter.setFont(self.font())
        painter.drawText(
            text_rect,
            Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
            self.text(),
        )


_SPIN_BUTTON_WIDTH = 26.0


def _paint_spinbox_step_arrows(widget):
    """Paint clear chevrons over the QSS-styled step-button regions.

    Native Fusion arrows can be too faint on Windows, especially after QSS
    customises the button backgrounds.  Drawing only the glyphs keeps the
    normal QSpinBox editing/stepping behaviour and signal/slot semantics intact.
    """
    if widget.width() <= _SPIN_BUTTON_WIDTH or widget.height() <= 0:
        return

    painter = QPainter(widget)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    dark = getattr(widget.window(), "theme", "light") == "dark"
    if widget.isEnabled():
        color = QColor("#93C5FD" if dark else "#2563EB")
    else:
        color = QColor("#64748B" if dark else "#A8B4C3")

    pen = QPen(color)
    pen.setWidthF(1.8)
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    painter.setPen(pen)

    cx = float(widget.width()) - _SPIN_BUTTON_WIDTH / 2.0 - 1.0
    up_y = float(widget.height()) * 0.26
    down_y = float(widget.height()) * 0.74
    half = 3.5
    rise = 2.4

    # Up chevron
    painter.drawLine(
        int(round(cx - half)), int(round(up_y + rise)),
        int(round(cx)), int(round(up_y - rise)),
    )
    painter.drawLine(
        int(round(cx)), int(round(up_y - rise)),
        int(round(cx + half)), int(round(up_y + rise)),
    )
    # Down chevron
    painter.drawLine(
        int(round(cx - half)), int(round(down_y - rise)),
        int(round(cx)), int(round(down_y + rise)),
    )
    painter.drawLine(
        int(round(cx)), int(round(down_y + rise)),
        int(round(cx + half)), int(round(down_y - rise)),
    )


class NoWheelDoubleSpinBox(QDoubleSpinBox):
    """DPI-safe modern DoubleSpinBox that ignores wheel changes inside scroll areas."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setProperty("modernSpin", True)

    def wheelEvent(self, event):
        event.ignore()

    def paintEvent(self, event):
        super().paintEvent(event)
        _paint_spinbox_step_arrows(self)


class NoWheelSpinBox(QSpinBox):
    """Integer companion of NoWheelDoubleSpinBox."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setProperty("modernSpin", True)

    def wheelEvent(self, event):
        event.ignore()

    def paintEvent(self, event):
        super().paintEvent(event)
        _paint_spinbox_step_arrows(self)


class NoWheelComboBox(QComboBox):
    """Disable accidental wheel selection changes inside the left scroll area."""

    def wheelEvent(self, event):
        event.ignore()

def apply_card_shadow(widget):
    """Subtle card shadow; silently skip on platforms that do not support it well."""
    try:
        effect = QGraphicsDropShadowEffect(widget)
        effect.setBlurRadius(18)
        effect.setOffset(0, 4)
        effect.setColor(QColor(15, 23, 42, 24))
        widget.setGraphicsEffect(effect)
    except Exception:
        pass

class DropFileList(QListWidget):
    filesDropped = Signal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.setAlternatingRowColors(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event)

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super().dragMoveEvent(event)

    def dropEvent(self, event):
        paths = [u.toLocalFile() for u in event.mimeData().urls() if u.isLocalFile()]
        paths = [p for p in paths if Path(p).suffix.lower() in SUPPORTED_EXTENSIONS]
        if paths:
            self.filesDropped.emit(paths)
            event.acceptProposedAction()
        else:
            super().dropEvent(event)


class CopyableTableWidget(QTableWidget):
    """Read-only result table with Excel-friendly TSV copy support."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_copy_menu)

    @staticmethod
    def _clean_cell_text(text):
        # TSV cells cannot contain literal newlines without breaking rows.
        return str(text or "").replace("\r", " ").replace("\n", " / ")

    def _selected_rows(self):
        rows = sorted({index.row() for index in self.selectedIndexes()})
        if not rows and self.currentRow() >= 0:
            rows = [self.currentRow()]
        return rows

    def _rows_to_tsv(self, rows, include_header=False):
        lines = []
        if include_header:
            headers = []
            for col in range(self.columnCount()):
                item = self.horizontalHeaderItem(col)
                headers.append(self._clean_cell_text(item.text() if item else ""))
            lines.append("\t".join(headers))
        for row in rows:
            values = []
            for col in range(self.columnCount()):
                item = self.item(row, col)
                values.append(self._clean_cell_text(item.text() if item else ""))
            lines.append("\t".join(values))
        return "\n".join(lines)

    def _copy_text(self, text):
        if text:
            QApplication.clipboard().setText(text)

    def copy_selected(self):
        self._copy_text(self._rows_to_tsv(self._selected_rows(), include_header=False))

    def copy_all(self, include_header=False):
        self._copy_text(self._rows_to_tsv(range(self.rowCount()), include_header=include_header))

    def keyPressEvent(self, event):
        if event.matches(QKeySequence.StandardKey.Copy):
            self.copy_selected()
            event.accept()
            return
        super().keyPressEvent(event)

    def _show_copy_menu(self, pos):
        index = self.indexAt(pos)
        if index.isValid() and index.row() not in self._selected_rows():
            self.selectRow(index.row())
        menu = QMenu(self)
        act_selected = menu.addAction(tr('复制所选'))
        act_all = menu.addAction(tr('复制全部'))
        act_all_header = menu.addAction(tr('复制全部（含表头）'))
        chosen = menu.exec(self.viewport().mapToGlobal(pos))
        if chosen == act_selected:
            self.copy_selected()
        elif chosen == act_all:
            self.copy_all(False)
        elif chosen == act_all_header:
            self.copy_all(True)


class LayoutSettingsDialog(QDialog):
    """Chinese, application-styled replacement for Matplotlib SubplotToolQt."""

    def __init__(self, panel, parent=None):
        super().__init__(parent)
        self.panel = panel
        self.setWindowTitle(tr('图表布局设置'))
        self.setMinimumWidth(410)
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 14)
        root.setSpacing(10)
        form = QGridLayout()
        form.setHorizontalSpacing(12); form.setVerticalSpacing(8)
        self.spins = {}
        labels = [
            ("top", tr('上边距')), ("bottom", tr('下边距')),
            ("left", tr('左边距')), ("right", tr('右边距')),
            ("hspace", tr('垂直间距')), ("wspace", tr('水平间距')),
        ]
        for idx, (key, text) in enumerate(labels):
            lab = QLabel(text)
            spin = NoWheelDoubleSpinBox()
            spin.setRange(0.0, 1.0); spin.setDecimals(3); spin.setSingleStep(0.01)
            spin.setValue(float(panel.layout_state[key]))
            self.spins[key] = spin
            form.addWidget(lab, idx // 2, (idx % 2) * 2)
            form.addWidget(spin, idx // 2, (idx % 2) * 2 + 1)
        root.addLayout(form)
        self.auto_check = ModernCheckBox(tr('自动紧凑布局'))
        self.auto_check.setChecked(bool(panel.layout_state.get("auto_layout", False)))
        root.addWidget(self.auto_check)
        hint = QLabel(tr('手动设置会保留在当前图表页；长图例需要额外空间时会临时预留，不覆盖这里保存的值。'))
        hint.setWordWrap(True); hint.setProperty("muted", True)
        root.addWidget(hint)
        buttons = QHBoxLayout()
        reset = QPushButton(tr('恢复默认'))
        apply_btn = QPushButton(tr('应用')); apply_btn.setProperty("primary", True)
        close_btn = QPushButton(tr('关闭'))
        reset.clicked.connect(self._reset)
        apply_btn.clicked.connect(self._apply)
        close_btn.clicked.connect(self.accept)
        buttons.addWidget(reset); buttons.addStretch(1); buttons.addWidget(apply_btn); buttons.addWidget(close_btn)
        root.addLayout(buttons)

    def _reset(self):
        state = self.panel.default_layout_state()
        for key, spin in self.spins.items():
            spin.setValue(float(state[key]))
        self.auto_check.setChecked(bool(state["auto_layout"]))
        self._apply()

    def _apply(self):
        for key, spin in self.spins.items():
            self.panel.layout_state[key] = float(spin.value())
        # Keep margins sane and ordered.
        self.panel.layout_state["left"] = min(self.panel.layout_state["left"], 0.45)
        self.panel.layout_state["right"] = max(self.panel.layout_state["right"], 0.55)
        self.panel.layout_state["bottom"] = min(self.panel.layout_state["bottom"], 0.45)
        self.panel.layout_state["top"] = max(self.panel.layout_state["top"], 0.55)
        self.panel.layout_state["auto_layout"] = self.auto_check.isChecked()
        self.panel.draw()


class PlotSettingsDialog(QDialog):
    """Small Chinese plot editor integrated with the application's theme."""

    def __init__(self, panel, parent=None):
        super().__init__(parent)
        self.panel = panel
        self.setWindowTitle(tr('图形设置'))
        self.setMinimumWidth(460)
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 14); root.setSpacing(10)
        form = QFormLayout(); form.setHorizontalSpacing(12); form.setVerticalSpacing(8)
        defaults = panel.current_plot_defaults
        settings = panel.plot_settings
        self.title_edit = QLineEdit(settings.get("title") if settings.get("title") is not None else defaults.get("title", ""))
        self.x_edit = QLineEdit(settings.get("xlabel") if settings.get("xlabel") is not None else defaults.get("xlabel", ""))
        self.y_edit = QLineEdit(settings.get("ylabel") if settings.get("ylabel") is not None else defaults.get("ylabel", ""))
        form.addRow(tr('图标题'), self.title_edit); form.addRow(tr('X 轴标题'), self.x_edit); form.addRow(tr('Y 轴标题'), self.y_edit)
        root.addLayout(form)

        opts = QHBoxLayout()
        self.grid_check = ModernCheckBox(tr('显示网格'))
        self.legend_check = ModernCheckBox(tr('显示图例'))
        self.grid_check.setChecked(bool(settings.get("grid", True)))
        self.legend_check.setChecked(bool(settings.get("legend_visible", True)))
        opts.addWidget(self.grid_check); opts.addWidget(self.legend_check); opts.addStretch(1)
        root.addLayout(opts)

        range_grid = QGridLayout(); range_grid.setHorizontalSpacing(8); range_grid.setVerticalSpacing(8)
        self.x_auto = ModernCheckBox(tr('X 自动范围')); self.y_auto = ModernCheckBox(tr('Y 自动范围'))
        self.x_auto.setChecked(bool(settings.get("x_auto", True))); self.y_auto.setChecked(bool(settings.get("y_auto", True)))
        self.x_min = NoWheelDoubleSpinBox(); self.x_max = NoWheelDoubleSpinBox(); self.y_min = NoWheelDoubleSpinBox(); self.y_max = NoWheelDoubleSpinBox()
        for sp in (self.x_min, self.x_max, self.y_min, self.y_max):
            sp.setRange(-1e12, 1e12); sp.setDecimals(6); sp.setMinimumWidth(120)
        xlim = panel.ax.get_xlim() if panel.ax is not None else (0.0, 1.0)
        ylim = panel.ax.get_ylim() if panel.ax is not None else (0.0, 1.0)
        sx = settings.get("xlim") or xlim; sy = settings.get("ylim") or ylim
        self.x_min.setValue(float(sx[0])); self.x_max.setValue(float(sx[1])); self.y_min.setValue(float(sy[0])); self.y_max.setValue(float(sy[1]))
        range_grid.addWidget(self.x_auto, 0, 0); range_grid.addWidget(QLabel(tr('最小')), 0, 1); range_grid.addWidget(self.x_min, 0, 2); range_grid.addWidget(QLabel(tr('最大')), 0, 3); range_grid.addWidget(self.x_max, 0, 4)
        range_grid.addWidget(self.y_auto, 1, 0); range_grid.addWidget(QLabel(tr('最小')), 1, 1); range_grid.addWidget(self.y_min, 1, 2); range_grid.addWidget(QLabel(tr('最大')), 1, 3); range_grid.addWidget(self.y_max, 1, 4)
        root.addLayout(range_grid)
        self.x_auto.toggled.connect(lambda checked: self._set_range_enabled("x", not checked))
        self.y_auto.toggled.connect(lambda checked: self._set_range_enabled("y", not checked))
        self._set_range_enabled("x", not self.x_auto.isChecked()); self._set_range_enabled("y", not self.y_auto.isChecked())

        style_row = QHBoxLayout(); style_row.addWidget(QLabel(tr('线宽')))
        self.line_width = NoWheelDoubleSpinBox(); self.line_width.setRange(0.5, 5.0); self.line_width.setDecimals(1); self.line_width.setSingleStep(0.1); self.line_width.setValue(float(settings.get("line_width") or 2.0))
        style_row.addWidget(self.line_width); style_row.addSpacing(16); style_row.addWidget(QLabel(tr('基础字号')))
        self.font_size = NoWheelDoubleSpinBox(); self.font_size.setRange(7.0, 18.0); self.font_size.setDecimals(1); self.font_size.setSingleStep(0.5); self.font_size.setValue(float(settings.get("font_size") or 9.5))
        style_row.addWidget(self.font_size); style_row.addStretch(1); root.addLayout(style_row)

        buttons = QHBoxLayout(); reset = QPushButton(tr('恢复默认')); apply_btn = QPushButton(tr('应用')); apply_btn.setProperty("primary", True); close_btn = QPushButton(tr('关闭'))
        reset.clicked.connect(self._reset); apply_btn.clicked.connect(self._apply); close_btn.clicked.connect(self.accept)
        buttons.addWidget(reset); buttons.addStretch(1); buttons.addWidget(apply_btn); buttons.addWidget(close_btn); root.addLayout(buttons)

    def _set_range_enabled(self, axis, enabled):
        pair = (self.x_min, self.x_max) if axis == "x" else (self.y_min, self.y_max)
        for widget in pair: widget.setEnabled(enabled)

    def _reset(self):
        self.panel.reset_plot_settings()
        self.accept()

    def _apply(self):
        settings = self.panel.plot_settings
        settings.update({
            "title": self.title_edit.text(), "xlabel": self.x_edit.text(), "ylabel": self.y_edit.text(),
            "grid": self.grid_check.isChecked(), "legend_visible": self.legend_check.isChecked(),
            "x_auto": self.x_auto.isChecked(), "y_auto": self.y_auto.isChecked(),
            "xlim": (self.x_min.value(), self.x_max.value()), "ylim": (self.y_min.value(), self.y_max.value()),
            "line_width": self.line_width.value(), "font_size": self.font_size.value(),
        })
        self.panel.apply_plot_settings_to_current_axes()
        self.panel.draw()


class ChineseNavigationToolbar(NavigationToolbar2QT):
    """Matplotlib toolbar with localized actions and project-owned dialogs."""

    toolitems = (
        ("主页", "恢复初始视图", "home", "home"),
        ("后退", "返回上一视图", "back", "back"),
        ("前进", "前进到下一视图", "forward", "forward"),
        (None, None, None, None),
        ("平移", "拖动画布；右键可缩放", "move", "pan"),
        ("缩放", "框选区域进行缩放", "zoom_to_rect", "zoom"),
        ("布局", "调整图表边距与间距", "subplots", "configure_subplots"),
        ("设置", "修改标题、坐标轴、网格和范围", "qt4_editor_options", "edit_parameters"),
        (None, None, None, None),
        ("保存", "保存当前图像", "filesave", "save_figure"),
    )

    def __init__(self, canvas, panel, parent=None):
        self.panel = panel
        self.toolitems = tuple((tr(label) if label else None, tr(tip) if tip else None, icon, callback)
                               for label, tip, icon, callback in type(self).toolitems)
        super().__init__(canvas, parent or panel, coordinates=True)

    def configure_subplots(self):
        LayoutSettingsDialog(self.panel, self).exec()

    def edit_parameters(self):
        PlotSettingsDialog(self.panel, self).exec()

    def save_figure(self, *args):
        default_type = self.canvas.get_default_filetype()
        filters = [tr('PNG 图像 (*.png)'), tr('PDF 文档 (*.pdf)'), tr('SVG 矢量图 (*.svg)'), tr('JPEG 图像 (*.jpg *.jpeg)'), tr('所有文件 (*)')]
        start = str(Path.home() / tr('CV图表.{0}', default_type))
        filename, _ = QFileDialog.getSaveFileName(self, tr('保存图像'), start, ";;".join(filters), options=QFileDialog.Option.DontUseNativeDialog)
        if not filename:
            return
        try:
            self.canvas.figure.savefig(filename, dpi=300, bbox_inches="tight")
            try:
                self.panel.hoverStatus.emit(tr('图像已保存：{0}', filename))
            except Exception:
                pass
        except Exception as exc:
            QMessageBox.critical(self, tr('保存图像失败'), str(exc))


class MplPanel(QWidget):
    curveClicked = Signal(str, bool)
    hoverStatus = Signal(str)

    def __init__(self, parent=None, empty_text="", compact=False):
        super().__init__(parent)
        self.empty_text = empty_text
        self.compact = compact
        self.theme = "light"
        self.figure = Figure(figsize=(8, 5), dpi=100, facecolor="#FFFFFF")
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.toolbar = ChineseNavigationToolbar(self.canvas, self, self)
        self.toolbar.setIconSize(QSize(20, 20))
        layout = QVBoxLayout(self); layout.setContentsMargins(0, 0, 0, 0); layout.setSpacing(0)
        layout.addWidget(self.toolbar); layout.addWidget(self.canvas, 1)
        self.ax = self.figure.add_subplot(111)
        self.artists = []
        self.annotation = None
        self.current_hover_artist = None
        self.layout_state = self.default_layout_state()
        self._legend_layout_override = {}
        self.current_plot_defaults = {"title": "", "xlabel": "", "ylabel": ""}
        self.plot_settings = self.default_plot_settings()
        self.canvas.mpl_connect("motion_notify_event", self._on_motion)
        self.canvas.mpl_connect("figure_leave_event", self._on_leave)
        self.canvas.mpl_connect("pick_event", self._on_pick)
        self.set_theme("light")
        self.show_empty(empty_text or tr('暂无数据'))

    @staticmethod
    def default_layout_state():
        return {"left": 0.14, "bottom": 0.18, "right": 0.92, "top": 0.90,
                "wspace": 0.20, "hspace": 0.20, "auto_layout": False}

    @staticmethod
    def default_plot_settings():
        return {"title": None, "xlabel": None, "ylabel": None, "grid": True,
                "legend_visible": True, "x_auto": True, "y_auto": True,
                "xlim": None, "ylim": None, "line_width": None, "font_size": None}

    def reset_plot_settings(self):
        # Reset display overrides without clearing/recreating the current axes.
        self.plot_settings = self.default_plot_settings()
        self.apply_plot_settings_to_current_axes()
        self.draw()

    def set_theme(self, theme):
        self.theme = "dark" if theme == "dark" else "light"
        if self.theme == "dark":
            self._colors = {
                "figure": "#111827", "axes": "#111827", "text": "#E2E8F0",
                "muted": "#94A3B8", "spine": "#475569", "grid": "#334155",
                "tooltip_bg": "#1E293B", "tooltip_edge": "#64748B",
            }
            self.toolbar.setStyleSheet(
                "QToolBar{background:#111827;border:0;border-bottom:1px solid #334155;spacing:3px;padding:3px;}"
                "QToolButton{background:transparent;color:#E2E8F0;border:0;border-radius:5px;padding:3px;}"
                "QToolButton:hover{background:#243047;} QLabel{color:#CBD5E1;background:transparent;}"
            )
        else:
            self._colors = {
                "figure": "#FFFFFF", "axes": "#FFFFFF", "text": "#1E293B",
                "muted": "#64748B", "spine": "#CBD5E1", "grid": "#E9ECEF",
                "tooltip_bg": "#FFFFFF", "tooltip_edge": "#CBD5E1",
            }
            self.toolbar.setStyleSheet(
                "QToolBar{background:#FFFFFF;border:0;border-bottom:1px solid #E2E8F0;spacing:3px;padding:3px;}"
                "QToolButton{background:transparent;color:#334155;border:0;border-radius:5px;padding:3px;}"
                "QToolButton:hover{background:#F1F5F9;} QLabel{color:#64748B;background:transparent;}"
            )
        # Do not call show_empty() here: clearing every non-current tab during a
        # theme change used to discard plot state.  The active page is refreshed
        # by the main window; other pages refresh normally when activated.
        try:
            self.figure.patch.set_facecolor(self._colors["figure"])
            if self.ax is not None:
                self.ax.set_facecolor(self._colors["axes"])
            self.canvas.draw_idle()
        except Exception:
            pass

    def _effective_layout(self):
        values = {k: self.layout_state[k] for k in ("left", "bottom", "right", "top", "wspace", "hspace")}
        for key, value in self._legend_layout_override.items():
            if key in ("top", "right"):
                values[key] = min(values[key], value)
            elif key in ("left", "bottom"):
                values[key] = max(values[key], value)
            else:
                values[key] = value
        return values

    def _apply_layout(self):
        values = self._effective_layout()
        try:
            if self.layout_state.get("auto_layout", False):
                self.figure.tight_layout(
                    pad=1.35 if self.compact else 1.55,
                    rect=(values["left"] * 0.55, values["bottom"] * 0.55, values["right"], values["top"]),
                )
            else:
                self.figure.subplots_adjust(**values)
        except Exception:
            try:
                self.figure.subplots_adjust(**values)
            except Exception:
                pass

    def prepare(self, title="", xlabel="", ylabel=""):
        self.figure.clear(); self.ax = self.figure.add_subplot(111); self._legend_layout_override = {}
        self._legend_title_padding = 10.0
        self.current_plot_defaults = {"title": title, "xlabel": xlabel, "ylabel": ylabel}
        c = self._colors; settings = self.plot_settings
        title_text = title if settings.get("title") is None else settings.get("title")
        x_text = xlabel if settings.get("xlabel") is None else settings.get("xlabel")
        y_text = ylabel if settings.get("ylabel") is None else settings.get("ylabel")
        base_font = float(settings.get("font_size") or 9.5)
        self.figure.patch.set_facecolor(c["figure"]); self.ax.set_facecolor(c["axes"])
        self.ax.set_title(title_text, color=c["text"], fontsize=base_font + (2.0 if self.compact else 3.0),
                          pad=10, fontweight="semibold", fontfamily=MATPLOTLIB_FONT)
        self.ax.set_xlabel(x_text, color=c["text"], fontsize=base_font, fontfamily=MATPLOTLIB_FONT)
        self.ax.set_ylabel(y_text, color=c["text"], fontsize=base_font, fontfamily=MATPLOTLIB_FONT)
        self.ax.tick_params(colors=c["muted"], labelsize=max(7.5, base_font - 0.7))
        self.ax.spines["top"].set_visible(False); self.ax.spines["right"].set_visible(False)
        self.ax.spines["left"].set_color(c["spine"]); self.ax.spines["bottom"].set_color(c["spine"])
        self.ax.grid(bool(settings.get("grid", True)), color=c["grid"], linewidth=0.8, linestyle="--", alpha=0.9)
        self.annotation = self.ax.annotate(
            "", xy=(0, 0), xytext=(12, 12), textcoords="offset points",
            bbox=dict(boxstyle="round,pad=0.60", fc=c["tooltip_bg"], ec=c["tooltip_edge"], alpha=0.97),
            color=c["text"], fontsize=8.8, fontfamily=MATPLOTLIB_FONT,
        )
        self.annotation.set_visible(False); self.artists = []
        self._apply_layout()
        return self.ax

    def show_empty(self, message):
        ax = self.prepare("", tr('电位 / Potential (V)'), tr('电流 / Current (A)'))
        ax.text(0.5, 0.5, message, ha="center", va="center", transform=ax.transAxes,
                color=self._colors["muted"], fontsize=11.5, fontfamily=MATPLOTLIB_FONT)
        ax.set_xticks([]); ax.set_yticks([]); self.draw()

    def register(self, artist, curve, tooltip, status_text=None, tooltip_fn=None):
        try: artist.set_picker(5)
        except Exception: pass
        artist._cv_curve = str(curve)
        self.artists.append({"artist": artist, "curve": str(curve), "tooltip": tooltip,
                             "status": status_text or str(curve), "tooltip_fn": tooltip_fn})

    def apply_plot_settings_to_current_axes(self):
        if self.ax is None: return
        s = self.plot_settings; d = self.current_plot_defaults; c = self._colors
        base_font = float(s.get("font_size") or 9.5)
        self.ax.set_title(d.get("title", "") if s.get("title") is None else s.get("title"), color=c["text"], fontfamily=MATPLOTLIB_FONT, fontsize=base_font + (2.0 if self.compact else 3.0), pad=self._legend_title_padding)
        self.ax.set_xlabel(d.get("xlabel", "") if s.get("xlabel") is None else s.get("xlabel"), color=c["text"], fontfamily=MATPLOTLIB_FONT, fontsize=base_font)
        self.ax.set_ylabel(d.get("ylabel", "") if s.get("ylabel") is None else s.get("ylabel"), color=c["text"], fontfamily=MATPLOTLIB_FONT, fontsize=base_font)
        self.ax.tick_params(colors=c["muted"], labelsize=max(7.5, base_font - 0.7))
        self.ax.grid(bool(s.get("grid", True)), color=c["grid"], linewidth=0.8, linestyle="--", alpha=0.9)
        if s.get("x_auto", True):
            try: self.ax.autoscale(enable=True, axis="x", tight=False)
            except Exception: pass
        elif s.get("xlim"):
            self.ax.set_xlim(*s["xlim"])
        if s.get("y_auto", True):
            try: self.ax.autoscale(enable=True, axis="y", tight=False)
            except Exception: pass
        elif s.get("ylim"):
            self.ax.set_ylim(*s["ylim"])
        for line in self.ax.lines:
            try:
                if not hasattr(line, "_cv_default_linewidth"):
                    line._cv_default_linewidth = line.get_linewidth()
                line.set_linewidth(float(s["line_width"]) if s.get("line_width") is not None else line._cv_default_linewidth)
            except Exception:
                pass
        legend = self.ax.get_legend()
        if legend is not None:
            legend.set_visible(bool(s.get("legend_visible", True)))

    def add_smart_labels(self, items, fontsize=8.5, add_y_margin=True):
        """Add collision-aware labels with subtle background and leader lines."""
        items = [dict(item) for item in items if np.isfinite(float(item.get("x", np.nan))) and np.isfinite(float(item.get("y", np.nan)))]
        if not items: return []
        if add_y_margin:
            try: self.ax.margins(y=0.11)
            except Exception: pass
        xlim = self.ax.get_xlim(); ylim = self.ax.get_ylim()
        size = (max(500.0, float(self.canvas.width() or 900)), max(320.0, float(self.canvas.height() or 520)))
        placements = smart_label_layout(items, xlim, ylim, axes_size=size, fontsize=fontsize)
        annotations = []
        for item, place in zip(items, placements):
            color = item.get("color") or self._colors["text"]
            arrowprops = None
            if place.arrow:
                arrowprops = dict(arrowstyle="-", color=color, lw=0.65, alpha=0.50, shrinkA=3, shrinkB=2)
            ann = self.ax.annotate(
                str(item.get("text", "")), (float(item["x"]), float(item["y"])),
                xytext=(place.dx, place.dy), textcoords="offset points",
                ha=place.ha, va=place.va, fontsize=fontsize,
                color=color, fontfamily=MATPLOTLIB_FONT,
                bbox=dict(boxstyle="round,pad=0.18", fc=self._colors["tooltip_bg"], ec=color, lw=0.45, alpha=0.82),
                arrowprops=arrowprops, annotation_clip=False, zorder=20,
            )
            annotations.append(ann)
        return annotations

    def apply_legend(self, handles=None, labels=None, *, enabled=True, extra_handles=None, extra_labels=None):
        """Create a themed, draggable, length-aware legend."""
        self._legend_layout_override = {}
        self._legend_title_padding = 10.0
        old = self.ax.get_legend() if self.ax is not None else None
        if old is not None:
            try: old.remove()
            except Exception: pass
        if not enabled or not self.plot_settings.get("legend_visible", True):
            return None
        if handles is None or labels is None:
            handles, labels = self.ax.get_legend_handles_labels()
        handles = list(handles); labels = list(labels)
        if extra_handles:
            handles.extend(extra_handles); labels.extend(list(extra_labels or [""] * len(extra_handles)))
        # Deduplicate while preserving order and ignore Matplotlib's no-legend labels.
        dedup_h, dedup_l, seen = [], [], set()
        for h, label in zip(handles, labels):
            label = str(label)
            if not label or label.startswith("_") or label in seen: continue
            seen.add(label); dedup_h.append(h); dedup_l.append(label)
        if not dedup_h: return None
        policy = adaptive_legend_layout(len(dedup_h)); self._legend_layout_override = dict(policy["layout_override"])
        if "bbox_to_anchor" in policy["kwargs"]:
            rows = (len(dedup_l) + policy["kwargs"]["ncol"] - 1) // policy["kwargs"]["ncol"]
            self._legend_title_padding = 8.8 * 1.8 * rows + 12.0
            title = self.plot_settings.get("title")
            if title is None:
                title = self.current_plot_defaults.get("title", "")
            title_lines = max(1, str(title).count("\n") + 1)
            title_font = float(self.plot_settings.get("font_size") or 9.5) + (2.0 if self.compact else 3.0)
            reserve_points = self._legend_title_padding + title_font * 1.5 * title_lines + 6.0
            height = max(200.0, float(self.canvas.height()))
            reserve = reserve_points * self.figure.dpi / 72.0 / height
            self._legend_layout_override["top"] = min(self._legend_layout_override["top"], max(0.35, 1.0 - reserve))
        legend = self.ax.legend(dedup_h, dedup_l, fontsize=8.8, framealpha=0.90,
                                borderpad=0.55, columnspacing=1.0, handlelength=1.8,
                                **policy["kwargs"])
        if legend is not None:
            legend.set_draggable(True)
            legend.get_frame().set_facecolor(self._colors["tooltip_bg"])
            legend.get_frame().set_edgecolor(self._colors["spine"])
            for text in legend.get_texts():
                text.set_color(self._colors["text"]); text.set_fontfamily(MATPLOTLIB_FONT)
        return legend

    def draw(self):
        self.apply_plot_settings_to_current_axes()
        self._apply_layout()
        self.canvas.draw_idle()

    def _find_hit(self, event):
        if event.inaxes != self.ax: return None
        for rec in reversed(self.artists):
            try: hit, _info = rec["artist"].contains(event)
            except Exception: continue
            if hit: return rec
        return None

    def _on_motion(self, event):
        rec = self._find_hit(event)
        if rec is None:
            if self.annotation is not None and self.annotation.get_visible():
                self.annotation.set_visible(False); self.canvas.draw_idle()
            return
        text = rec["tooltip"]
        if rec.get("tooltip_fn") is not None:
            try: text = rec["tooltip_fn"](event)
            except Exception: pass
        if self.annotation is not None and event.xdata is not None and event.ydata is not None:
            self.annotation.xy = (event.xdata, event.ydata); self.annotation.set_text(text)
            xlim = self.ax.get_xlim(); ylim = self.ax.get_ylim(); x_span = xlim[1]-xlim[0]; y_span = ylim[1]-ylim[0]
            x_frac = (event.xdata-xlim[0])/x_span if abs(x_span)>1e-15 else 0.5
            y_frac = (event.ydata-ylim[0])/y_span if abs(y_span)>1e-15 else 0.5
            near_right = float(np.clip(x_frac,0,1)) >= 0.78; near_top = float(np.clip(y_frac,0,1)) >= 0.80
            dx = -14 if near_right else 14; dy = -14 if near_top else 14
            self.annotation.set_position((dx,dy)); self.annotation.set_ha("right" if near_right else "left"); self.annotation.set_va("top" if near_top else "bottom")
            self.annotation.set_visible(True); self.canvas.draw_idle()
        self.hoverStatus.emit(rec.get("status") or rec["curve"])

    def _on_leave(self, event):
        if self.annotation is not None and self.annotation.get_visible():
            self.annotation.set_visible(False); self.canvas.draw_idle()

    def _on_pick(self, event):
        curve = getattr(event.artist, "_cv_curve", "")
        if curve:
            self.curveClicked.emit(curve, bool(getattr(event.mouseevent, "dblclick", False)))


class CycleSelectorDialog(QDialog):
    def __init__(self, curves, selected, parent=None):
        super().__init__(parent)
        self.setWindowTitle(tr('选择显示圈数'))
        self.resize(460, 680)
        self.setMinimumSize(390, 520)
        self.curves = list(curves)
        self.selected = set(selected)
        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(8)
        hint = QLabel(tr('勾选需要显示的 CV 循环；支持鼠标滚轮与滚动条。'))
        hint.setProperty("muted", True)
        root.addWidget(hint)
        self.list = QListWidget()
        self.list.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.list.setStyleSheet(
            "QListWidget{font-size:14px;} QListWidget::item{min-height:31px;}"
        )
        for curve in curves:
            item = QListWidgetItem(curve)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Checked if curve in self.selected else Qt.CheckState.Unchecked)
            self.list.addItem(item)
        root.addWidget(self.list, 1)
        footer = QHBoxLayout()
        all_btn = QPushButton(tr('全选'))
        clear_btn = QPushButton(tr('清空'))
        cancel_btn = QPushButton(tr('取消'))
        apply_btn = QPushButton(tr('应用'))
        apply_btn.setProperty("primary", True)
        all_btn.clicked.connect(lambda: self._set_all(True))
        clear_btn.clicked.connect(lambda: self._set_all(False))
        cancel_btn.clicked.connect(self.reject)
        apply_btn.clicked.connect(self.accept)
        footer.addWidget(all_btn); footer.addWidget(clear_btn); footer.addStretch(1)
        footer.addWidget(cancel_btn); footer.addWidget(apply_btn)
        root.addLayout(footer)
        QTimer.singleShot(0, lambda: self.list.verticalScrollBar().setValue(0))

    def _set_all(self, checked):
        state = Qt.CheckState.Checked if checked else Qt.CheckState.Unchecked
        for i in range(self.list.count()):
            self.list.item(i).setCheckState(state)

    def selected_curves(self):
        return [self.list.item(i).text() for i in range(self.list.count())
                if self.list.item(i).checkState() == Qt.CheckState.Checked]


class ProcessingWorker(QThread):
    log = Signal(str, str)
    finishedData = Signal(object, object)
    failedFatal = Signal(str)

    def __init__(self, paths, params, parent=None):
        super().__init__(parent)
        self.paths = list(paths)
        self.params = dict(params)

    def run(self):
        results, errors = {}, {}
        set_log_callback(lambda level, msg: self.log.emit(level, msg))
        try:
            for idx, path in enumerate(self.paths, 1):
                self.log.emit("INFO", tr('处理 {0}/{1}：{2}', idx, len(self.paths), Path(path).name))
                try:
                    out = process_cv_file(
                        input_path=path,
                        mode=self.params["mode"],
                        scan_rate_mv=self.params["scan_rate_mv"],
                        precision_mv=self.params["precision_mv"],
                        start_voltage=self.params["start_voltage"],
                        end_voltage=self.params["end_voltage"],
                        save_verification=self.params["save_verification"],
                        selection_mode=self.params["selection_mode"],
                        auto_target=self.params["auto_target"],
                        manual_indices=self.params["manual_indices"],
                        apply_cut_to_all=self.params["apply_cut_to_all"],
                        output_dir=self.params["output_dir"],
                        return_all=True,
                        # Reuse the processor's parsed curves instead of reading the file again for the CV page.
                        include_raw_curves=True,
                    )
                    verification_file, integral_file, df_filtered, df_all, raw_curves = out
                    results[path] = {
                        "verification_file": verification_file,
                        "integral_file": integral_file,
                        "df_filtered": df_filtered,
                        "df_all": df_all,
                        "raw_curves": raw_curves,
                        "mode": self.params["mode"],
                    }
                except Exception as exc:
                    errors[path] = str(exc)
                    self.log.emit("ERROR", f"{Path(path).name}：{exc}")
            self.finishedData.emit(results, errors)
        except Exception:
            self.failedFatal.emit(traceback.format_exc(limit=8))
        finally:
            set_log_callback(None)
