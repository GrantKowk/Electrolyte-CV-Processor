# Electrolyte CV Processor

<details open>
<summary>Languages</summary>

[English](../../README.md) · [简体中文](README.zh-CN.md) · [繁體中文](README.zh-TW.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · **Deutsch** · [Français](README.fr.md) · [Español](README.es.md) · [Italiano](README.it.md) · [Português (Brasil)](README.pt-BR.md) · [Русский](README.ru.md) · [Українська](README.uk.md) · [Polski](README.pl.md) · [Nederlands](README.nl.md) · [Svenska](README.sv.md) · [Suomi](README.fi.md) · [Čeština](README.cs.md) · [Türkçe](README.tr.md) · [Ελληνικά](README.el.md) · [العربية](README.ar.md) · [فارسی](README.fa.md) · [עברית](README.he.md) · [हिन्दी](README.hi.md) · [বাংলা](README.bn.md) · [اردو](README.ur.md) · [Bahasa Indonesia](README.id.md) · [Bahasa Melayu](README.ms.md) · [Tiếng Việt](README.vi.md) · [ไทย](README.th.md) · [Română](README.ro.md)

</details>

Ein Desktop-Werkzeug zur Analyse der zyklischen Voltammetrie (CV) von Elektrolyten, entwickelt mit Python, PySide6 und Matplotlib. Die Oberfläche unterstützt Englisch und vereinfachtes Chinesisch; Englisch ist voreingestellt.

## Funktionen

- Gamry-DTA/TXT-Dateien und unterstützte Excel-Kurvendateien importieren.
- Zyklen automatisch oder manuell auswählen und Oxidations- oder Reduktionsscans analysieren.
- Integrationsflächen und Ladung anhand der eingestellten Scanrate berechnen.
- CV-Kurven, Peak- und Einsatzpotenziale, Verschiebungen gegenüber einem Referenzzyklus und Qualitätsprüfungen anzeigen.
- Excel-Arbeitsmappen und Abbildungen exportieren sowie Anzeige- und Verarbeitungseinstellungen speichern.

## Starten

Windows, Python 3.10 oder neuer. Die folgenden Befehle im Projektverzeichnis ausführen.

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python main.py
```

## Verwendung

1. CV-Dateien hinzufügen. Texttabellen müssen Abschnitte `CURVE... TABLE` mit den Spalten `Vf` und `Im` enthalten.
2. Analysemodus, Spannungsbereich, Scanrate und Zyklusauswahl einstellen.
3. Verarbeitung starten, Ergebnisse prüfen und exportieren.
4. Die Oberflächensprache unter **Settings → Language** oder **Settings → Preferences** wechseln. Die Auswahl wird gespeichert.

## Quellcodestruktur

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

## Windows-Build

```powershell
.venv\Scripts\python -m pip install -r requirements.txt -r packaging/requirements-build.txt
.venv\Scripts\python -m PyInstaller --clean --noconfirm packaging/ElectrolyteCVProcessor.spec
```

Die ausführbare Datei wird in `dist/` erstellt.

## Lizenz

[MIT](../../LICENSE)
