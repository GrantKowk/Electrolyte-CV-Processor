# Electrolyte CV Processor

<details open>
<summary>Languages</summary>

[English](../../README.md) · [简体中文](README.zh-CN.md) · **繁體中文** · [日本語](README.ja.md) · [한국어](README.ko.md) · [Deutsch](README.de.md) · [Français](README.fr.md) · [Español](README.es.md) · [Italiano](README.it.md) · [Português (Brasil)](README.pt-BR.md) · [Русский](README.ru.md) · [Українська](README.uk.md) · [Polski](README.pl.md) · [Nederlands](README.nl.md) · [Svenska](README.sv.md) · [Suomi](README.fi.md) · [Čeština](README.cs.md) · [Türkçe](README.tr.md) · [Ελληνικά](README.el.md) · [العربية](README.ar.md) · [فارسی](README.fa.md) · [עברית](README.he.md) · [हिन्दी](README.hi.md) · [বাংলা](README.bn.md) · [اردو](README.ur.md) · [Bahasa Indonesia](README.id.md) · [Bahasa Melayu](README.ms.md) · [Tiếng Việt](README.vi.md) · [ไทย](README.th.md) · [Română](README.ro.md)

</details>

用於電解液循環伏安（CV）分析的桌面工具，基於 Python、PySide6 和 Matplotlib。介面支援英語與簡體中文，預設為英語。

## 功能

- 匯入 Gamry DTA/TXT 及支援的 Excel 曲線檔案。
- 自動或手動選擇循環，分析氧化或還原掃描。
- 依設定的掃描速率計算積分面積與電荷。
- 檢視 CV 曲線、峰值電位、起始電位、相對參考循環的位移及品質檢查結果。
- 匯出 Excel 與圖像，儲存顯示及處理偏好。

## 執行

Windows，Python 3.10 或更新版本。請在專案根目錄執行以下命令。

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python main.py
```

## 使用方式

1. 加入 CV 檔案。文字曲線表需包含 `CURVE... TABLE` 區段及 `Vf`、`Im` 欄位。
2. 設定分析模式、電壓範圍、掃描速率及循環選擇。
3. 執行處理，檢視結果並匯出。
4. 透過 **Settings → Language** 或 **Settings → Preferences** 切換介面語言；選擇會被儲存。

## 原始碼結構

```text
Electrolyte-CV-Processor/
├── assets/
│   ├── app_icon.ico
│   └── app_icon.png
├── docs/
│   └── readme/
│       ├── README.ar.md
│       ├── README.bn.md
│       ├── README.cs.md
│       ├── README.de.md
│       ├── README.el.md
│       ├── README.es.md
│       ├── README.fa.md
│       ├── README.fi.md
│       ├── README.fr.md
│       ├── README.he.md
│       ├── README.hi.md
│       ├── README.id.md
│       ├── README.it.md
│       ├── README.ja.md
│       ├── README.ko.md
│       ├── README.ms.md
│       ├── README.nl.md
│       ├── README.pl.md
│       ├── README.pt-BR.md
│       ├── README.ro.md
│       ├── README.ru.md
│       ├── README.sv.md
│       ├── README.th.md
│       ├── README.tr.md
│       ├── README.uk.md
│       ├── README.ur.md
│       ├── README.vi.md
│       ├── README.zh-CN.md
│       └── README.zh-TW.md
├── electrolyte_cv/
│   ├── core/
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
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── main_window.py
│   │   ├── preferences_dialog.py
│   │   ├── qt_compat.py
│   │   ├── styles.py
│   │   └── widgets.py
│   ├── __init__.py
│   ├── app.py
│   ├── i18n.py
│   ├── resources.py
│   └── settings_manager.py
├── packaging/
│   ├── ElectrolyteCVProcessor.spec
│   ├── requirements-build.txt
│   └── version_info.txt
├── LICENSE
├── README.md
├── main.py
└── requirements.txt
```

## Windows 打包

```powershell
.venv\Scripts\python -m pip install -r requirements.txt -r packaging/requirements-build.txt
.venv\Scripts\python -m PyInstaller --clean --noconfirm packaging/ElectrolyteCVProcessor.spec
```

產生的可執行檔位於 `dist/`。

## 授權

[MIT](../../LICENSE)
