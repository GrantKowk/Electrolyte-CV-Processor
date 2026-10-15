from __future__ import annotations

from .i18n import tr

import sys

from .ui.qt_compat import PYSIDE6_AVAILABLE, QT_IMPORT_ERROR
from .resources import resource_path


def _set_windows_app_id():
    """Give Windows a stable taskbar identity for the packaged/source app."""
    if sys.platform != "win32":
        return
    try:
        import ctypes
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
            "ElectrolyteCVProcessor.Desktop.2.0"
        )
    except Exception:
        pass


def run_gui():
    if not PYSIDE6_AVAILABLE:
        raise SystemExit(
            tr('未安装 PySide6，无法启动 Qt 界面。\n请执行：pip install -r requirements.txt\n导入错误：{0}', QT_IMPORT_ERROR)
        )

    from .ui.qt_compat import QApplication, QFont, QIcon
    from .ui.styles import V19_LIGHT_STYLE
    from .ui.main_window import CVMainWindow

    _set_windows_app_id()
    app = QApplication.instance() or QApplication(sys.argv)
    app.setStyle("Fusion")

    # Qt 6 is per-monitor-DPI aware by default. Keep application typography in
    # point units so QFontMetrics and custom control size hints scale together.
    app_font = QFont("Microsoft YaHei UI")
    app_font.setPointSizeF(9.0)
    app.setFont(app_font)
    app.setStyleSheet(V19_LIGHT_STYLE)

    icon_file = resource_path("assets", "app_icon.ico")
    if icon_file.exists():
        app.setWindowIcon(QIcon(str(icon_file)))

    win = CVMainWindow()
    if icon_file.exists():
        win.setWindowIcon(QIcon(str(icon_file)))
    win.show()
    return app.exec()
