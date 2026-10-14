# Electrolyte CV Processor v2.0

A Python desktop tool for processing electrolyte cyclic voltammetry (CV) measurements, built with PySide6 and Matplotlib.

用于电解液循环伏安（CV）数据处理的桌面工具，提供中文界面。

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

本仓库不公开任何实验数据、测试数据、样例数据或处理结果；请在本机使用自己的数据。提交文件前请检查 Git 暂存清单。
