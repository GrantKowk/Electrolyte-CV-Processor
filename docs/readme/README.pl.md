# Electrolyte CV Processor

<details open>
<summary>Languages</summary>

[English](../../README.md) · [简体中文](README.zh-CN.md) · [繁體中文](README.zh-TW.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Deutsch](README.de.md) · [Français](README.fr.md) · [Español](README.es.md) · [Italiano](README.it.md) · [Português (Brasil)](README.pt-BR.md) · [Русский](README.ru.md) · [Українська](README.uk.md) · **Polski** · [Nederlands](README.nl.md) · [Svenska](README.sv.md) · [Suomi](README.fi.md) · [Čeština](README.cs.md) · [Türkçe](README.tr.md) · [Ελληνικά](README.el.md) · [العربية](README.ar.md) · [فارسی](README.fa.md) · [עברית](README.he.md) · [हिन्दी](README.hi.md) · [বাংলা](README.bn.md) · [اردو](README.ur.md) · [Bahasa Indonesia](README.id.md) · [Bahasa Melayu](README.ms.md) · [Tiếng Việt](README.vi.md) · [ไทย](README.th.md) · [Română](README.ro.md)

</details>

Narzędzie desktopowe do analizy woltamperometrii cyklicznej (CV) elektrolitów, oparte na Pythonie, PySide6 i Matplotlib. Interfejs obsługuje angielski i uproszczony chiński; domyślnym językiem jest angielski.

## Funkcje

- Import plików Gamry DTA/TXT i obsługiwanych plików krzywych Excel.
- Automatyczny lub ręczny wybór cykli oraz analiza przebiegów utleniania lub redukcji.
- Obliczanie pól całek i ładunku na podstawie ustawionej szybkości skanowania.
- Wyświetlanie krzywych CV, potencjałów piku i początku procesu, przesunięć względem cyklu odniesienia oraz kontroli jakości.
- Eksport skoroszytów Excel i wykresów; zapisywanie preferencji wyświetlania i przetwarzania.

## Uruchamianie

Windows, Python 3.10 lub nowszy. Polecenia należy uruchamiać w katalogu głównym projektu.

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python main.py
```

## Użycie

1. Dodaj pliki CV. Tabele tekstowe muszą zawierać sekcje `CURVE... TABLE` z kolumnami `Vf` i `Im`.
2. Ustaw tryb analizy, zakres napięcia, szybkość skanowania i wybór cykli.
3. Uruchom przetwarzanie, sprawdź wyniki i je wyeksportuj.
4. Zmień język interfejsu w **Settings → Language** lub **Settings → Preferences**. Wybór jest zapisywany.

## Struktura kodu

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

## Kompilacja dla Windows

```powershell
.venv\Scripts\python -m pip install -r requirements.txt -r packaging/requirements-build.txt
.venv\Scripts\python -m PyInstaller --clean --noconfirm packaging/ElectrolyteCVProcessor.spec
```

Plik wykonywalny powstaje w `dist/`.

## Licencja

[MIT](../../LICENSE)
