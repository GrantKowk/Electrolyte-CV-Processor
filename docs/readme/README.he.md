# Electrolyte CV Processor

<details open>
<summary>Languages</summary>

[English](../../README.md) · [简体中文](README.zh-CN.md) · [繁體中文](README.zh-TW.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Deutsch](README.de.md) · [Français](README.fr.md) · [Español](README.es.md) · [Italiano](README.it.md) · [Português (Brasil)](README.pt-BR.md) · [Русский](README.ru.md) · [Українська](README.uk.md) · [Polski](README.pl.md) · [Nederlands](README.nl.md) · [Svenska](README.sv.md) · [Suomi](README.fi.md) · [Čeština](README.cs.md) · [Türkçe](README.tr.md) · [Ελληνικά](README.el.md) · [العربية](README.ar.md) · [فارسی](README.fa.md) · **עברית** · [हिन्दी](README.hi.md) · [বাংলা](README.bn.md) · [اردو](README.ur.md) · [Bahasa Indonesia](README.id.md) · [Bahasa Melayu](README.ms.md) · [Tiếng Việt](README.vi.md) · [ไทย](README.th.md) · [Română](README.ro.md)

</details>

כלי שולחני לניתוח וולטמטריה מחזורית (CV) של אלקטרוליטים, המבוסס על Python, PySide6 ו-Matplotlib. הממשק תומך באנגלית ובסינית מפושטת; אנגלית היא שפת ברירת המחדל.

## יכולות

- ייבוא קובצי Gamry DTA/TXT וקובצי עקומות Excel נתמכים.
- בחירת מחזורים אוטומטית או ידנית וניתוח סריקות חמצון או חיזור.
- חישוב שטחים באינטגרציה ומטען לפי קצב הסריקה שהוגדר.
- הצגת עקומות CV, פוטנציאלי שיא ותחילה, הסטות ביחס למחזור ייחוס ובדיקות איכות.
- ייצוא חוברות Excel ותרשימים ושמירת העדפות תצוגה ועיבוד.

## הפעלה

Windows, Python 3.10 ומעלה. יש להריץ את הפקודות בתיקיית השורש של הפרויקט.

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python main.py
```

## שימוש

1. הוסיפו קובצי CV. טבלאות טקסט חייבות להכיל מקטעי `CURVE... TABLE` עם העמודות `Vf` ו-`Im`.
2. הגדירו את מצב הניתוח, טווח המתח, קצב הסריקה ובחירת המחזורים.
3. הפעילו את העיבוד, בדקו את התוצאות וייצאו אותן.
4. שנו את שפת הממשק דרך **Settings → Language** או **Settings → Preferences**. הבחירה נשמרת.

## מבנה קוד המקור

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

## בנייה ל-Windows

```powershell
.venv\Scripts\python -m pip install -r requirements.txt -r packaging/requirements-build.txt
.venv\Scripts\python -m PyInstaller --clean --noconfirm packaging/ElectrolyteCVProcessor.spec
```

קובץ ההפעלה נוצר ב-`dist/`.

## רישיון

[MIT](../../LICENSE)
