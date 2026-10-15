# Electrolyte CV Processor

<details open>
<summary>Languages</summary>

[English](../../README.md) · [简体中文](README.zh-CN.md) · [繁體中文](README.zh-TW.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Deutsch](README.de.md) · [Français](README.fr.md) · [Español](README.es.md) · [Italiano](README.it.md) · [Português (Brasil)](README.pt-BR.md) · [Русский](README.ru.md) · [Українська](README.uk.md) · [Polski](README.pl.md) · [Nederlands](README.nl.md) · [Svenska](README.sv.md) · [Suomi](README.fi.md) · [Čeština](README.cs.md) · [Türkçe](README.tr.md) · [Ελληνικά](README.el.md) · [العربية](README.ar.md) · **فارسی** · [עברית](README.he.md) · [हिन्दी](README.hi.md) · [বাংলা](README.bn.md) · [اردو](README.ur.md) · [Bahasa Indonesia](README.id.md) · [Bahasa Melayu](README.ms.md) · [Tiếng Việt](README.vi.md) · [ไทย](README.th.md) · [Română](README.ro.md)

</details>

ابزار رومیزی تحلیل ولتامتری چرخه‌ای (CV) الکترولیت‌ها، ساخته‌شده با Python، PySide6 و Matplotlib. رابط کاربری از انگلیسی و چینی ساده‌شده پشتیبانی می‌کند؛ زبان پیش‌فرض انگلیسی است.

## قابلیت‌ها

- ورود فایل‌های Gamry DTA/TXT و فایل‌های منحنی Excel پشتیبانی‌شده.
- انتخاب خودکار یا دستی چرخه‌ها و تحلیل روبش‌های اکسایش یا کاهش.
- محاسبه مساحت انتگرال و بار بر اساس سرعت روبش تنظیم‌شده.
- نمایش منحنی‌های CV، پتانسیل قله و آغاز، جابه‌جایی نسبت به چرخه مرجع و بررسی‌های کیفیت.
- خروجی گرفتن از فایل‌های Excel و شکل‌ها و ذخیره تنظیمات نمایش و پردازش.

## اجرا

Windows و Python 3.10 یا جدیدتر. فرمان‌ها را در پوشه اصلی پروژه اجرا کنید.

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python main.py
```

## روش استفاده

1. فایل‌های CV را اضافه کنید. جدول‌های متنی باید بخش‌های `CURVE... TABLE` با ستون‌های `Vf` و `Im` داشته باشند.
2. حالت تحلیل، بازه ولتاژ، سرعت روبش و انتخاب چرخه‌ها را تنظیم کنید.
3. پردازش را اجرا کنید، نتایج را بررسی و خروجی بگیرید.
4. زبان رابط را از **Settings → Language** یا **Settings → Preferences** تغییر دهید. انتخاب شما ذخیره می‌شود.

## ساختار کد منبع

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

## ساخت برای Windows

```powershell
.venv\Scripts\python -m pip install -r requirements.txt -r packaging/requirements-build.txt
.venv\Scripts\python -m PyInstaller --clean --noconfirm packaging/ElectrolyteCVProcessor.spec
```

فایل اجرایی در `dist/` ساخته می‌شود.

## مجوز

[MIT](../../LICENSE)
