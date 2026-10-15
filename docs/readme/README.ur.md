# Electrolyte CV Processor

<details open>
<summary>Languages</summary>

[English](../../README.md) · [简体中文](README.zh-CN.md) · [繁體中文](README.zh-TW.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Deutsch](README.de.md) · [Français](README.fr.md) · [Español](README.es.md) · [Italiano](README.it.md) · [Português (Brasil)](README.pt-BR.md) · [Русский](README.ru.md) · [Українська](README.uk.md) · [Polski](README.pl.md) · [Nederlands](README.nl.md) · [Svenska](README.sv.md) · [Suomi](README.fi.md) · [Čeština](README.cs.md) · [Türkçe](README.tr.md) · [Ελληνικά](README.el.md) · [العربية](README.ar.md) · [فارسی](README.fa.md) · [עברית](README.he.md) · [हिन्दी](README.hi.md) · [বাংলা](README.bn.md) · **اردو** · [Bahasa Indonesia](README.id.md) · [Bahasa Melayu](README.ms.md) · [Tiếng Việt](README.vi.md) · [ไทย](README.th.md) · [Română](README.ro.md)

</details>

Python، PySide6 اور Matplotlib سے تیار کردہ الیکٹرولائٹ کی سائکلک وولٹامیٹری (CV) کے تجزیے کا ڈیسک ٹاپ ٹول۔ انٹرفیس انگریزی اور سادہ چینی کی حمایت کرتا ہے؛ طے شدہ زبان انگریزی ہے۔

## خصوصیات

- Gamry DTA/TXT اور معاون Excel منحنی فائلیں درآمد کریں۔
- سائیکل خودکار یا دستی طور پر منتخب کرکے تکسید یا اختزال کے اسکین کا تجزیہ کریں۔
- مقرر کردہ اسکین کی رفتار سے تکمیلی رقبہ اور چارج حساب کریں۔
- CV منحنیات، چوٹی اور آغاز کے پوٹینشل، حوالہ سائیکل کے مقابلے میں تبدیلی اور معیار کی جانچ دیکھیں۔
- Excel ورک بکس اور تصاویر برآمد کریں؛ نمائش اور پراسیسنگ کی ترجیحات محفوظ کریں۔

## چلانا

Windows، Python 3.10 یا جدید تر۔ کمانڈز پروجیکٹ کے بنیادی فولڈر میں چلائیں۔

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python main.py
```

## استعمال

1. CV فائلیں شامل کریں۔ متنی جدولوں میں `Vf` اور `Im` کالموں والے `CURVE... TABLE` حصے ہونے چاہئیں۔
2. تجزیے کا موڈ، وولٹیج کی حد، اسکین کی رفتار اور سائیکلوں کا انتخاب مقرر کریں۔
3. پراسیسنگ چلائیں، نتائج دیکھیں اور برآمد کریں۔
4. **Settings → Language** یا **Settings → Preferences** میں انٹرفیس کی زبان بدلیں۔ آپ کا انتخاب محفوظ ہوتا ہے۔

## سورس کوڈ کی ساخت

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

## Windows بلڈ

```powershell
.venv\Scripts\python -m pip install -r requirements.txt -r packaging/requirements-build.txt
.venv\Scripts\python -m PyInstaller --clean --noconfirm packaging/ElectrolyteCVProcessor.spec
```

قابلِ اجرا فائل `dist/` میں بنتی ہے۔

## لائسنس

[MIT](../../LICENSE)
