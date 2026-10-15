# Electrolyte CV Processor

<details open>
<summary>Languages</summary>

[English](../../README.md) · [简体中文](README.zh-CN.md) · [繁體中文](README.zh-TW.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Deutsch](README.de.md) · [Français](README.fr.md) · [Español](README.es.md) · [Italiano](README.it.md) · [Português (Brasil)](README.pt-BR.md) · [Русский](README.ru.md) · [Українська](README.uk.md) · [Polski](README.pl.md) · [Nederlands](README.nl.md) · [Svenska](README.sv.md) · [Suomi](README.fi.md) · **Čeština** · [Türkçe](README.tr.md) · [Ελληνικά](README.el.md) · [العربية](README.ar.md) · [فارسی](README.fa.md) · [עברית](README.he.md) · [हिन्दी](README.hi.md) · [বাংলা](README.bn.md) · [اردو](README.ur.md) · [Bahasa Indonesia](README.id.md) · [Bahasa Melayu](README.ms.md) · [Tiếng Việt](README.vi.md) · [ไทย](README.th.md) · [Română](README.ro.md)

</details>

Desktopový nástroj pro analýzu cyklické voltametrie (CV) elektrolytů, vytvořený pomocí Pythonu, PySide6 a Matplotlib. Rozhraní podporuje angličtinu a zjednodušenou čínštinu; výchozí je angličtina.

## Funkce

- Import souborů Gamry DTA/TXT a podporovaných souborů křivek Excel.
- Automatický nebo ruční výběr cyklů a analýza oxidačních či redukčních skenů.
- Výpočet integrovaných ploch a náboje z nastavené rychlosti skenování.
- Zobrazení CV křivek, potenciálů píku a počátku procesu, posunů vůči referenčnímu cyklu a kontrol kvality.
- Export sešitů Excel a obrázků; ukládání nastavení zobrazení a zpracování.

## Spuštění

Windows, Python 3.10 nebo novější. Příkazy spusťte v kořenové složce projektu.

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python main.py
```

## Použití

1. Přidejte soubory CV. Textové tabulky musí obsahovat sekce `CURVE... TABLE` se sloupci `Vf` a `Im`.
2. Nastavte režim analýzy, rozsah napětí, rychlost skenování a výběr cyklů.
3. Spusťte zpracování, zkontrolujte výsledky a exportujte je.
4. Jazyk rozhraní změňte v **Settings → Language** nebo **Settings → Preferences**. Volba se uloží.

## Struktura zdrojového kódu

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

## Sestavení pro Windows

```powershell
.venv\Scripts\python -m pip install -r requirements.txt -r packaging/requirements-build.txt
.venv\Scripts\python -m PyInstaller --clean --noconfirm packaging/ElectrolyteCVProcessor.spec
```

Spustitelný soubor se vytvoří v `dist/`.

## Licence

[MIT](../../LICENSE)
