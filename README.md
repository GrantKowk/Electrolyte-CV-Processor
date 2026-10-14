# Electrolyte CV Processor

用于电解液循环伏安（CV）数据处理的桌面工具，提供中文界面。基于 Python、PySide6 和 Matplotlib。

## 功能

- 导入 Gamry DTA/TXT 及支持的 Excel 曲线文件。
- 自动或手动选择循环，分析氧化与还原扫描。
- 根据扫描速率计算积分面积与电荷。
- 查看 CV 曲线、峰电位、起始电位、相对参考循环的偏移及质量检查结果。
- 导出 Excel 和图像，保存显示与处理偏好。

## 运行

Windows，Python 3.10 或更高版本。

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python main.py
```

## 使用

1. 添加 CV 文件。文本曲线表需包含 `CURVE... TABLE`、`Vf` 和 `Im` 列。
2. 设置分析模式、电压范围、扫描速率和循环选择。
3. 运行处理，查看分析结果并导出。

## 源码结构

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

## Windows 打包

```powershell
.venv\Scripts\python -m pip install -r requirements.txt -r packaging/requirements-build.txt
.venv\Scripts\python -m PyInstaller --clean --noconfirm packaging/ElectrolyteCVProcessor.spec
```

生成的可执行文件位于 `dist/`。

## 许可证

[MIT](LICENSE)
