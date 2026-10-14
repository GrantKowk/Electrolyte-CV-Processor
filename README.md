# Electrolyte CV Processor

用于电解液循环伏安（CV）数据处理的桌面工具，提供中文界面。基于 Python、PySide6 和 Matplotlib。

A desktop application for electrolyte cyclic voltammetry analysis, plotting, and Excel export.

**版本：v2.0 · 启动入口：`main.py` · 程序主体：`electrolyte_cv/`**

[功能](#features--功能) · [安装与运行](#run--运行) · [源码结构](#source-layout--源码结构) · [使用方法](#usage--使用) · [Windows 打包](#windows-build--windows-打包) · [许可证](#license--许可证)

## Features / 功能

- Import Gamry DTA/TXT curve tables and supported Excel curve layouts.
- Select cycles automatically or manually; process oxidation and reduction scans.
- Calculate integrated area and charge using the configured scan rate.
- Inspect CV plots, peak potentials, onset potentials, shifts relative to a reference cycle, and quality-control results.
- Export Excel workbooks and plots; save display and processing preferences locally.

## Run / 运行

Python 3.10 or newer is recommended. Windows is the primary desktop platform.

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python main.py
```

On other platforms, use the virtual environment's Python executable. A graphical desktop is required.

## Source layout / 源码结构

```text
Electrolyte-CV-Processor/
├── electrolyte_cv/                   # 应用源码
│   ├── core/                         # 数据处理与分析
│   │   ├── __init__.py
│   │   ├── analysis.py
│   │   ├── config.py
│   │   ├── cv_plot_pipeline.py
│   │   ├── export.py
│   │   ├── formatting.py
│   │   ├── logging_utils.py
│   │   ├── parsers.py
│   │   ├── plot_helpers.py
│   │   └── processor.py
│   ├── ui/                           # 桌面界面
│   │   ├── __init__.py
│   │   ├── main_window.py
│   │   ├── preferences_dialog.py
│   │   ├── qt_compat.py
│   │   ├── styles.py
│   │   └── widgets.py
│   ├── __init__.py
│   ├── app.py                        # Qt 应用入口
│   ├── resources.py                  # 资源路径管理
│   └── settings_manager.py           # 本机偏好设置
├── assets/                           # 应用图标
│   ├── app_icon.ico
│   └── app_icon.png
├── packaging/                        # Windows 打包配置
│   ├── ElectrolyteCVProcessor.spec
│   ├── requirements-build.txt
│   └── version_info.txt
├── LICENSE                           # MIT 许可证
├── main.py                           # 启动脚本
├── README.md                         # 项目说明
└── requirements.txt                  # 运行依赖
```

| 想查看的功能 | 源码位置 |
| --- | --- |
| 程序启动 | `main.py` → `electrolyte_cv/app.py` |
| 主界面与设置 | `electrolyte_cv/ui/main_window.py`、`preferences_dialog.py` |
| DTA / Excel 读取 | `electrolyte_cv/core/parsers.py` |
| CV 分析与绘图 | `electrolyte_cv/core/analysis.py`、`cv_plot_pipeline.py` |
| 批量处理与结果导出 | `electrolyte_cv/core/processor.py`、`export.py` |

`main.py` 需要与 `electrolyte_cv/`、`assets/` 一起使用；请下载整个仓库，不要只下载启动脚本。

## Usage / 使用

1. Add your local CV files. Text inputs must contain `CURVE... TABLE` sections with `Vf` and `Im` columns; Excel inputs must match the supported curve layout.
2. Set the analysis mode, voltage range, scan rate, split precision, and cycles to process.
3. Run processing, inspect the result pages and QC flags, then export to your chosen local folder.

Check units and scan settings against your measurement method before interpreting results.

## Windows build / Windows 打包

```powershell
.venv\Scripts\python -m pip install -r requirements.txt -r packaging/requirements-build.txt
.venv\Scripts\python -m PyInstaller --clean --noconfirm packaging/ElectrolyteCVProcessor.spec
```

The executable is written to `dist/`.

## License / 许可证

本项目源码采用 [MIT 许可证](LICENSE)。允许使用、修改、分发及商用，使用者需要保留版权与许可证声明。软件按现状提供，不作担保；完整条款请参阅 `LICENSE`。

Application source is licensed under MIT. Third-party dependencies remain under their respective licenses.
