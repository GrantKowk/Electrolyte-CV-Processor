"""Qt style sheets used by the desktop interface."""

LIGHT_STYLE = r"""
QWidget {
    background: #F5F7FA;
    color: #1E293B;
    font-family: "Microsoft YaHei UI", "Segoe UI Variable", "Segoe UI", sans-serif;
    font-size: 9pt;
}
QMainWindow, QDialog { background: #F5F7FA; }
QMenuBar {
    background: rgba(255,255,255,245);
    color: #1E293B;
    border-bottom: 1px solid #E2E8F0;
    padding: 3px 6px;
}
QMenuBar::item { padding: 7px 11px; border-radius: 6px; background: transparent; }
QMenuBar::item:selected { background: #EEF4FD; color: #2A7DE1; }
QMenu { background: #FFFFFF; color: #1E293B; border: 1px solid #E2E8F0; padding: 6px; }
QMenu::item { padding: 8px 28px 8px 12px; border-radius: 5px; }
QMenu::item:selected { background: #EEF4FD; color: #2A7DE1; }
QGroupBox {
    background: rgba(255,255,255,248);
    border: 1px solid #E2E8F0;
    border-radius: 10px;
    margin-top: 14px;
    padding: 14px 10px 10px 10px;
    font-weight: 600;
    color: #1E293B;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 12px;
    padding: 0 6px;
    background: #F5F7FA;
    color: #334155;
}
QLabel { color: #1E293B; background: transparent; }
QLabel[muted="true"] { color: #64748B; }
QLabel[summary="true"] { background:#FFFFFF; border:1px solid #E2E8F0; border-radius:10px; padding:10px; font-weight:600; }
QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {
    min-height: 34px;
    background: #FFFFFF;
    color: #0F172A;
    border: 1px solid #CBD5E1;
    border-radius: 8px;
    padding: 3px 9px;
    selection-background-color: #BFD9F8;
}
QLineEdit:hover, QComboBox:hover, QSpinBox:hover, QDoubleSpinBox:hover { border-color: #94A3B8; }
QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus {
    border: 1px solid #2A7DE1;
    background: #FFFFFF;
}
QComboBox::drop-down { border: 0; width: 26px; }
QComboBox QAbstractItemView {
    background: #FFFFFF; color: #1E293B; border: 1px solid #CBD5E1;
    selection-background-color: #E7F0FC; selection-color: #1E293B; outline: 0;
}
QPushButton, QToolButton {
    min-height: 34px;
    background: #FFFFFF;
    color: #334155;
    border: 1px solid #CBD5E1;
    border-radius: 8px;
    padding: 4px 13px;
    font-weight: 500;
}
QPushButton:hover, QToolButton:hover { background: #F8FAFC; border-color: #94A3B8; color: #0F172A; }
QPushButton:pressed, QToolButton:pressed { background: #EEF2F7; }
QPushButton:disabled { color: #94A3B8; background: #F1F5F9; border-color: #E2E8F0; }
QPushButton[primary="true"] {
    background: #2A7DE1;
    border: 1px solid #2A7DE1;
    color: #FFFFFF;
    font-weight: 600;
}
QPushButton[primary="true"]:hover { background: #1F6EC9; border-color: #1F6EC9; }
QListWidget {
    background: #FFFFFF; color: #1E293B; border: 1px solid #E2E8F0;
    border-radius: 8px; alternate-background-color: #FAFBFC;
}
QListWidget::item { min-height: 31px; padding: 3px 7px; border-radius: 5px; }
QListWidget::item:hover { background: #F8FAFC; }
QListWidget::item:selected { background: #E8F1FC; color: #1E293B; }
QTabWidget::pane { border: 1px solid #E2E8F0; border-radius: 10px; background: #FFFFFF; top: -1px; }
QTabBar::tab {
    background: transparent; color: #64748B; border: 0;
    padding: 10px 18px; margin: 4px 2px; min-width: 72px; border-radius: 15px;
}
QTabBar::tab:selected { background: #E8F1FC; color: #2A7DE1; font-weight: 600; }
QTabBar::tab:hover:!selected { background: #F1F5F9; color: #334155; }
QSplitter::handle { background: #E2E8F0; width: 4px; }
QSplitter::handle:hover { background: #AFCDF1; }
QPlainTextEdit {
    background: #FBFCFE; color: #334155; border: 1px solid #E2E8F0;
    border-radius: 8px; font-family: Consolas, "Microsoft YaHei UI"; font-size: 9pt;
}
QTableWidget {
    background: #FFFFFF;
    alternate-background-color: #FAFBFC;
    color: #1E293B;
    gridline-color: #E2E8F0;
    border: 1px solid #E2E8F0;
    border-radius: 8px;
    selection-background-color: #E8F1FC;
    selection-color: #1E293B;
}
QTableWidget::item { padding: 7px; border: 0; }
QTableWidget::item:hover { background: #F8FAFC; }
QHeaderView::section {
    background: #F1F5F9;
    color: #1E293B;
    border: 0;
    border-right: 1px solid #E2E8F0;
    border-bottom: 1px solid #CBD5E1;
    padding: 8px 7px;
    font-weight: 600;
}
QScrollBar:vertical { background: transparent; width: 12px; margin: 2px; }
QScrollBar::handle:vertical { background: #CBD5E1; min-height: 34px; border-radius: 5px; }
QScrollBar::handle:vertical:hover { background: #94A3B8; }
QScrollBar:horizontal { background: transparent; height: 12px; margin: 2px; }
QScrollBar::handle:horizontal { background: #CBD5E1; min-width: 34px; border-radius: 5px; }
QScrollBar::handle:horizontal:hover { background: #94A3B8; }
QScrollBar::add-line, QScrollBar::sub-line { width: 0; height: 0; }
QStatusBar { background: #FFFFFF; color: #64748B; border-top: 1px solid #E2E8F0; }
"""

DARK_STYLE = r"""
QWidget {
    background: #0F172A;
    color: #E2E8F0;
    font-family: "Microsoft YaHei UI", "Segoe UI Variable", "Segoe UI", sans-serif;
    font-size: 9pt;
}
QMainWindow, QDialog { background: #0F172A; }
QMenuBar { background: #111827; color: #E2E8F0; border-bottom: 1px solid #334155; padding: 3px 6px; }
QMenuBar::item { padding: 7px 11px; border-radius: 6px; }
QMenuBar::item:selected { background: #1E293B; color: #60A5FA; }
QMenu { background: #172033; color: #E2E8F0; border: 1px solid #334155; padding: 6px; }
QMenu::item { padding: 8px 28px 8px 12px; border-radius: 5px; }
QMenu::item:selected { background: #243047; color: #FFFFFF; }
QGroupBox { background: #162033; border: 1px solid #334155; border-radius: 10px; margin-top: 14px; padding: 14px 10px 10px 10px; font-weight: 600; }
QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; left: 12px; padding: 0 6px; background: #0F172A; color: #E2E8F0; }
QLabel { color: #E2E8F0; background: transparent; }
QLabel[muted="true"] { color: #94A3B8; }
QLabel[summary="true"] { background:#162033; border:1px solid #334155; border-radius:10px; padding:10px; font-weight:600; }
QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox { min-height: 34px; background: #1E293B; color: #E2E8F0; border: 1px solid #334155; border-radius: 8px; padding: 3px 9px; }
QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus { border: 1px solid #4C8DFF; }
QComboBox::drop-down { border:0; width:26px; }
QComboBox QAbstractItemView { background:#1E293B; color:#E2E8F0; border:1px solid #334155; selection-background-color:#334155; }
QPushButton, QToolButton { min-height:34px; background:#1E293B; color:#E2E8F0; border:1px solid #334155; border-radius:8px; padding:4px 13px; }
QPushButton:hover, QToolButton:hover { background:#243047; border-color:#475569; }
QPushButton[primary="true"] { background:#2A7DE1; border-color:#2A7DE1; color:white; font-weight:600; }
QListWidget { background:#172033; color:#E2E8F0; border:1px solid #334155; border-radius:8px; alternate-background-color:#152033; }
QListWidget::item { min-height:31px; padding:3px 7px; }
QListWidget::item:selected { background:#243B5A; color:#FFFFFF; }
QTabWidget::pane { border:1px solid #334155; border-radius:10px; background:#111827; top:-1px; }
QTabBar::tab { background:transparent; color:#94A3B8; border:0; padding:10px 18px; margin:4px 2px; min-width:72px; border-radius:15px; }
QTabBar::tab:selected { background:#213A5C; color:#93C5FD; font-weight:600; }
QTabBar::tab:hover:!selected { background:#1E293B; color:#E2E8F0; }
QSplitter::handle { background:#334155; width:4px; }
QPlainTextEdit { background:#0B1220; color:#CBD5E1; border:1px solid #334155; border-radius:8px; font-family:Consolas,"Microsoft YaHei UI"; font-size:9pt; }
QTableWidget { background:#111827; alternate-background-color:#162033; color:#E2E8F0; gridline-color:#334155; border:1px solid #334155; border-radius:8px; selection-background-color:#243B5A; selection-color:#FFFFFF; }
QTableWidget::item { padding:7px; }
QHeaderView::section { background:#1E293B; color:#E2E8F0; border:0; border-right:1px solid #334155; border-bottom:1px solid #475569; padding:8px 7px; font-weight:600; }
QScrollBar:vertical, QScrollBar:horizontal { background:transparent; }
QScrollBar:vertical { width:12px; } QScrollBar:horizontal { height:12px; }
QScrollBar::handle:vertical, QScrollBar::handle:horizontal { background:#475569; border-radius:5px; min-height:34px; min-width:34px; }
QScrollBar::add-line, QScrollBar::sub-line { width:0; height:0; }
QStatusBar { background:#111827; color:#94A3B8; border-top:1px solid #334155; }
"""

V19_LIGHT_STYLE = LIGHT_STYLE + r"""
QPushButton[secondary="true"] {
    background: #EEF6FF; color: #1769C2; border: 1px solid #B8D5F4;
    font-weight: 600;
}
QPushButton[secondary="true"]:hover { background:#DDEEFF; border-color:#7FB2EA; color:#105CA9; }
QPushButton[tertiary="true"] {
    background: #F8FAFC; color: #475569; border: 1px solid #D7E0EA;
    font-weight: 500;
}
QPushButton[tertiary="true"]:hover { background:#EEF2F7; border-color:#B7C4D3; color:#1E293B; }
QToolButton[logtoggle="true"] { background:transparent; border:0; color:#64748B; padding:2px 5px; }
QToolButton[logtoggle="true"]:hover { color:#2A7DE1; background:#EEF4FD; }
QLabel[state="ready"] { color:#168A5B; font-weight:600; }
QLabel[state="outdated"] { color:#B7791F; font-weight:600; }
QLabel[state="failed"] { color:#C24141; font-weight:600; }
QLabel[state="processing"] { color:#2A7DE1; font-weight:600; }
QLabel[state="idle"] { color:#64748B; font-weight:600; }
QFrame[diagnostic="true"] { background:#EEF6FF; border:1px solid #B8D5F4; border-radius:8px; }
/* Compact V19 cards: preserve readability while fitting the primary workflow vertically. */
QGroupBox { margin-top:12px; padding:10px 8px 8px 8px; }

/* v1.9.3 UI/DPI polish: keep one border width across normal/hover/focus. */
QLineEdit, QComboBox {
    min-height:36px;
    background:#FFFFFF;
    border:1px solid #94A3B8;
    border-radius:8px;
}
QLineEdit:hover, QComboBox:hover { border-color:#7EA6CF; background:#FFFFFF; }
QLineEdit:focus, QComboBox:focus { border-color:#2A7DE1; background:#FCFDFF; }

/* Only the V19 NoWheel spin boxes receive the custom step-button treatment. */
QSpinBox[modernSpin="true"], QDoubleSpinBox[modernSpin="true"] {
    min-height:36px;
    background:#FFFFFF;
    color:#0F172A;
    border:1px solid #A9BDD1;
    border-radius:8px;
    padding:3px 30px 3px 9px;
    selection-background-color:#BFD9F8;
}
QSpinBox[modernSpin="true"]:hover, QDoubleSpinBox[modernSpin="true"]:hover {
    border-color:#7EA6CF;
}
QSpinBox[modernSpin="true"]:focus, QDoubleSpinBox[modernSpin="true"]:focus {
    border-color:#2A7DE1;
    background:#FCFDFF;
}
QSpinBox[modernSpin="true"]:disabled, QDoubleSpinBox[modernSpin="true"]:disabled {
    color:#94A3B8;
    background:#F1F5F9;
    border-color:#CBD5E1;
}
QSpinBox[modernSpin="true"]::up-button, QDoubleSpinBox[modernSpin="true"]::up-button {
    subcontrol-origin:border;
    subcontrol-position:top right;
    width:26px;
    background:#F5F9FE;
    border:0;
    border-left:1px solid #D5E0EC;
    border-bottom:1px solid #E4EBF3;
    border-top-right-radius:7px;
}
QSpinBox[modernSpin="true"]::down-button, QDoubleSpinBox[modernSpin="true"]::down-button {
    subcontrol-origin:border;
    subcontrol-position:bottom right;
    width:26px;
    background:#F5F9FE;
    border:0;
    border-left:1px solid #D5E0EC;
    border-bottom-right-radius:7px;
}
QSpinBox[modernSpin="true"]::up-button:hover, QDoubleSpinBox[modernSpin="true"]::up-button:hover,
QSpinBox[modernSpin="true"]::down-button:hover, QDoubleSpinBox[modernSpin="true"]::down-button:hover {
    background:#EAF3FF;
}
QSpinBox[modernSpin="true"]::up-button:pressed, QDoubleSpinBox[modernSpin="true"]::up-button:pressed,
QSpinBox[modernSpin="true"]::down-button:pressed, QDoubleSpinBox[modernSpin="true"]::down-button:pressed {
    background:#D8E9FC;
}
/* Native Fusion glyphs are suppressed; widgets.py paints crisp DPI-aware chevrons. */
QSpinBox[modernSpin="true"]::up-arrow, QDoubleSpinBox[modernSpin="true"]::up-arrow,
QSpinBox[modernSpin="true"]::down-arrow, QDoubleSpinBox[modernSpin="true"]::down-arrow {
    image:none;
    width:0px;
    height:0px;
}
QGroupBox::title { padding:0 8px; }
QHeaderView::section { padding:10px 8px; }

/* Tab text uses point units to match QApplication's base font at Windows DPI scaling. */
QTabBar::tab { font-size:10pt; font-weight:500; }
QTabBar::tab:selected { background:#E8F1FC; color:#2A7DE1; font-weight:600; }

/* v1.9.2: Primary 按钮渐变与视觉深度 */
QPushButton[primary="true"] {
    color:#FFFFFF; border:none; border-radius:10px; min-height:44px; font-weight:600;
    background:qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #2A7DE1, stop:1 #1F6EC9);
}
QPushButton[primary="true"]:hover {
    background:qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #3B8BEB, stop:1 #2478D6);
}
QPushButton[primary="true"]:pressed {
    background:qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #1F6EC9, stop:1 #185DB0);
}
"""

V19_DARK_STYLE = DARK_STYLE + r"""
QPushButton[secondary="true"] { background:#183153; color:#93C5FD; border:1px solid #315C8F; font-weight:600; }
QPushButton[secondary="true"]:hover { background:#21426E; border-color:#4D7FB8; color:#DBEAFE; }
QPushButton[tertiary="true"] { background:#172033; color:#CBD5E1; border:1px solid #334155; }
QPushButton[tertiary="true"]:hover { background:#243047; border-color:#475569; }
QToolButton[logtoggle="true"] { background:transparent; border:0; color:#94A3B8; padding:2px 5px; }
QToolButton[logtoggle="true"]:hover { color:#60A5FA; background:#243047; }
QLabel[state="ready"] { color:#6EE7B7; font-weight:600; }
QLabel[state="outdated"] { color:#FBBF24; font-weight:600; }
QLabel[state="failed"] { color:#FCA5A5; font-weight:600; }
QLabel[state="processing"] { color:#60A5FA; font-weight:600; }
QLabel[state="idle"] { color:#94A3B8; font-weight:600; }
QFrame[diagnostic="true"] { background:#183153; border:1px solid #315C8F; border-radius:8px; }
/* Match light-theme vertical density without changing typography. */
QGroupBox { margin-top:12px; padding:10px 8px 8px 8px; }

/* v1.9.3 UI/DPI polish: dark controls keep the same 1 px frame in every state. */
QLineEdit, QComboBox {
    min-height:36px;
    background:#1E293B;
    border:1px solid #475D75;
    border-radius:8px;
}
QLineEdit:hover, QComboBox:hover { border-color:#6B89AA; background:#202D42; }
QLineEdit:focus, QComboBox:focus { border-color:#60A5FA; background:#202D42; }

QSpinBox[modernSpin="true"], QDoubleSpinBox[modernSpin="true"] {
    min-height:36px;
    background:#1E293B;
    color:#E2E8F0;
    border:1px solid #52687F;
    border-radius:8px;
    padding:3px 30px 3px 9px;
    selection-background-color:#315C8F;
}
QSpinBox[modernSpin="true"]:hover, QDoubleSpinBox[modernSpin="true"]:hover {
    border-color:#6B89AA;
}
QSpinBox[modernSpin="true"]:focus, QDoubleSpinBox[modernSpin="true"]:focus {
    border-color:#60A5FA;
    background:#202D42;
}
QSpinBox[modernSpin="true"]:disabled, QDoubleSpinBox[modernSpin="true"]:disabled {
    color:#64748B;
    background:#162033;
    border-color:#334155;
}
QSpinBox[modernSpin="true"]::up-button, QDoubleSpinBox[modernSpin="true"]::up-button {
    subcontrol-origin:border;
    subcontrol-position:top right;
    width:26px;
    background:#1A2638;
    border:0;
    border-left:1px solid #334A64;
    border-bottom:1px solid #2B4059;
    border-top-right-radius:7px;
}
QSpinBox[modernSpin="true"]::down-button, QDoubleSpinBox[modernSpin="true"]::down-button {
    subcontrol-origin:border;
    subcontrol-position:bottom right;
    width:26px;
    background:#1A2638;
    border:0;
    border-left:1px solid #334A64;
    border-bottom-right-radius:7px;
}
QSpinBox[modernSpin="true"]::up-button:hover, QDoubleSpinBox[modernSpin="true"]::up-button:hover,
QSpinBox[modernSpin="true"]::down-button:hover, QDoubleSpinBox[modernSpin="true"]::down-button:hover {
    background:#233A56;
}
QSpinBox[modernSpin="true"]::up-button:pressed, QDoubleSpinBox[modernSpin="true"]::up-button:pressed,
QSpinBox[modernSpin="true"]::down-button:pressed, QDoubleSpinBox[modernSpin="true"]::down-button:pressed {
    background:#294765;
}
QSpinBox[modernSpin="true"]::up-arrow, QDoubleSpinBox[modernSpin="true"]::up-arrow,
QSpinBox[modernSpin="true"]::down-arrow, QDoubleSpinBox[modernSpin="true"]::down-arrow {
    image:none;
    width:0px;
    height:0px;
}
QGroupBox::title { padding:0 8px; }
QHeaderView::section { padding:10px 8px; }

/* Tab font follows the same point-based DPI strategy as the light theme. */
QTabBar::tab { font-size:10pt; font-weight:500; }
QTabBar::tab:selected { background:#213A5C; color:#BFDBFE; font-weight:600; }

/* v1.9.2: 深色 Primary 按钮 */
QPushButton[primary="true"] {
    color:#FFFFFF; border:none; border-radius:10px; min-height:44px; font-weight:600;
    background:qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #3185E5, stop:1 #236AC0);
}
QPushButton[primary="true"]:hover {
    background:qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #4895EC, stop:1 #2D78CF);
}
QPushButton[primary="true"]:pressed {
    background:qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #236AC0, stop:1 #1A579D);
}
"""
