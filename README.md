# Electrolyte CV Processor

<details open>
<summary>Languages</summary>

**English** · [简体中文](docs/readme/README.zh-CN.md) · [繁體中文](docs/readme/README.zh-TW.md) · [日本語](docs/readme/README.ja.md) · [한국어](docs/readme/README.ko.md) · [Deutsch](docs/readme/README.de.md) · [Français](docs/readme/README.fr.md) · [Español](docs/readme/README.es.md) · [Italiano](docs/readme/README.it.md) · [Português (Brasil)](docs/readme/README.pt-BR.md) · [Русский](docs/readme/README.ru.md) · [Українська](docs/readme/README.uk.md) · [Polski](docs/readme/README.pl.md) · [Nederlands](docs/readme/README.nl.md) · [Svenska](docs/readme/README.sv.md) · [Suomi](docs/readme/README.fi.md) · [Čeština](docs/readme/README.cs.md) · [Türkçe](docs/readme/README.tr.md) · [Ελληνικά](docs/readme/README.el.md) · [العربية](docs/readme/README.ar.md) · [فارسی](docs/readme/README.fa.md) · [עברית](docs/readme/README.he.md) · [हिन्दी](docs/readme/README.hi.md) · [বাংলা](docs/readme/README.bn.md) · [اردو](docs/readme/README.ur.md) · [Bahasa Indonesia](docs/readme/README.id.md) · [Bahasa Melayu](docs/readme/README.ms.md) · [Tiếng Việt](docs/readme/README.vi.md) · [ไทย](docs/readme/README.th.md) · [Română](docs/readme/README.ro.md)

</details>

A desktop tool for electrolyte cyclic voltammetry (CV) analysis, built with Python, PySide6 and Matplotlib. The interface supports English and Simplified Chinese; English is the default.

## Features

- Import Gamry DTA/TXT and supported Excel curve files.
- Select cycles automatically or manually and analyze oxidation or reduction scans.
- Calculate integrated areas and charge from the configured scan rate.
- View CV curves, peak and onset potentials, shifts relative to a reference cycle, and quality checks.
- Export Excel workbooks and figures; save display and processing preferences.

## Run

Windows, Python 3.10 or newer. Run these commands from the project root.

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python main.py
```

## Usage

1. Add CV files. Text curve tables must contain `CURVE... TABLE` sections with `Vf` and `Im` columns.
2. Set the analysis mode, voltage range, scan rate and cycle selection.
3. Run processing, inspect the results and export.
4. Switch the interface language through **Settings → Language** or **Settings → Preferences**. Your choice is saved.

## Source layout

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

## Windows build

```powershell
.venv\Scripts\python -m pip install -r requirements.txt -r packaging/requirements-build.txt
.venv\Scripts\python -m PyInstaller --clean --noconfirm packaging/ElectrolyteCVProcessor.spec
```

The executable is generated in `dist/`.

## License

[MIT](LICENSE)
