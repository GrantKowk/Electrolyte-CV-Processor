# Electrolyte CV Processor v2.0

用于电解液循环伏安（CV）数据处理的桌面工具，提供中文界面。基于 Python、PySide6 和 Matplotlib。

A desktop application for electrolyte cyclic voltammetry analysis, plotting, and Excel export.

**版本：v2.0 · 启动入口：`main.py` · 程序主体：`electrolyte_cv/`**

本仓库仅发布程序源码和运行、构建所需文件，不包含 DTA、Excel、测试数据或处理结果。

[功能](#features--功能) · [安装与运行](#run--运行) · [源码结构](#source-layout--源码结构) · [使用方法](#usage--使用) · [Windows 打包](#windows-build--windows-打包) · [数据隐私](#privacy--数据隐私)

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
├── main.py                       # 启动入口
├── electrolyte_cv/               # v2.0 程序主体
│   ├── app.py                    # 初始化并启动 Qt 应用
│   ├── core/                     # 数据解析、分析、绘图与导出
│   ├── ui/                       # 主窗口、设置对话框与界面控件
│   ├── resources.py              # 资源路径管理
│   └── settings_manager.py       # 本机偏好设置
├── assets/                       # 应用图标
├── requirements.txt              # 运行依赖
├── requirements-build.txt        # 打包依赖
├── ElectrolyteCVProcessor.spec   # PyInstaller 构建配置
├── version_info.txt              # Windows 可执行文件版本信息
├── .gitignore                    # 限定允许提交的文件
└── README.md
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
python -m pip install -r requirements-build.txt
python -m PyInstaller --clean --noconfirm ElectrolyteCVProcessor.spec
```

The executable is written to `dist/`. Installer tooling and prebuilt executables are not part of this source publication.

## Privacy / 数据隐私

This repository contains application source, interface icons, dependency lists, and build configuration only. No experimental data, test fixtures, sample datasets, generated results, local settings, or historical test reports are included. Supply your own data locally. The application processes files on your computer.

本仓库不公开任何实验数据、测试数据、样例数据或处理结果；请在本机使用自己的数据。压缩包中的 `tests/`、`legacy/`、历史测试报告和辅助开发工具均未纳入本次发布。

`.gitignore` 采用允许清单，只允许提交指定源码、图标、文档及构建配置，并排除 DTA、Excel、CSV 等数据文件。提交前仍请检查 Git 暂存清单，避免通过强制添加等方式将私人数据纳入版本历史。
