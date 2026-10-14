from __future__ import annotations

try:
    from PySide6.QtCore import Qt, QThread, Signal, QTimer, QSize, QRectF, QSettings, QPoint
    from PySide6.QtGui import (
        QColor, QFont, QIcon, QAction, QActionGroup, QBrush, QPainter, QPen,
        QKeySequence, QCursor
    )
    from PySide6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
        QGroupBox, QLabel, QPushButton, QLineEdit, QRadioButton, QCheckBox,
        QComboBox, QDoubleSpinBox, QSpinBox, QListWidget, QListWidgetItem,
        QFileDialog, QMessageBox, QSplitter, QTabWidget, QTableWidget,
        QTableWidgetItem, QAbstractItemView, QHeaderView, QDialog, QScrollArea,
        QPlainTextEdit, QFrame, QSizePolicy, QToolButton, QButtonGroup,
        QGraphicsDropShadowEffect, QMenu, QFormLayout
    )
    import matplotlib
    matplotlib.use("QtAgg")
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg, NavigationToolbar2QT
    PYSIDE6_AVAILABLE = True
    QT_IMPORT_ERROR = None
except Exception as exc:
    PYSIDE6_AVAILABLE = False
    QT_IMPORT_ERROR = exc


def require_qt():
    if not PYSIDE6_AVAILABLE:
        raise RuntimeError(
            "PySide6/Qt 无法导入。请安装 requirements.txt 后重试。\n"
            f"导入错误：{QT_IMPORT_ERROR}"
        )
