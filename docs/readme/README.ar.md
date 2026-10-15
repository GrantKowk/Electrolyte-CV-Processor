# Electrolyte CV Processor

<details open>
<summary>Languages</summary>

[English](../../README.md) · [简体中文](README.zh-CN.md) · [繁體中文](README.zh-TW.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Deutsch](README.de.md) · [Français](README.fr.md) · [Español](README.es.md) · [Italiano](README.it.md) · [Português (Brasil)](README.pt-BR.md) · [Русский](README.ru.md) · [Українська](README.uk.md) · [Polski](README.pl.md) · [Nederlands](README.nl.md) · [Svenska](README.sv.md) · [Suomi](README.fi.md) · [Čeština](README.cs.md) · [Türkçe](README.tr.md) · [Ελληνικά](README.el.md) · **العربية** · [فارسی](README.fa.md) · [עברית](README.he.md) · [हिन्दी](README.hi.md) · [বাংলা](README.bn.md) · [اردو](README.ur.md) · [Bahasa Indonesia](README.id.md) · [Bahasa Melayu](README.ms.md) · [Tiếng Việt](README.vi.md) · [ไทย](README.th.md) · [Română](README.ro.md)

</details>

أداة مكتبية لتحليل الفولتمترية الدورية (CV) للإلكتروليتات، مبنية باستخدام Python وPySide6 وMatplotlib. تدعم الواجهة الإنجليزية والصينية المبسطة؛ واللغة الافتراضية هي الإنجليزية.

## الميزات

- استيراد ملفات Gamry DTA/TXT وملفات منحنيات Excel المدعومة.
- اختيار الدورات تلقائيًا أو يدويًا وتحليل مسوح الأكسدة أو الاختزال.
- حساب المساحات المتكاملة والشحنة بناءً على معدل المسح المحدد.
- عرض منحنيات CV وجهود القمم وبداية التفاعل والانزياحات بالنسبة إلى دورة مرجعية وفحوص الجودة.
- تصدير مصنفات Excel والأشكال وحفظ تفضيلات العرض والمعالجة.

## التشغيل

Windows وPython 3.10 أو أحدث. نفّذ الأوامر من المجلد الرئيسي للمشروع.

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python main.py
```

## الاستخدام

1. أضف ملفات CV. يجب أن تحتوي الجداول النصية على أقسام `CURVE... TABLE` وأعمدة `Vf` و`Im`.
2. اضبط وضع التحليل ونطاق الجهد ومعدل المسح واختيار الدورات.
3. شغّل المعالجة وراجع النتائج ثم صدّرها.
4. غيّر لغة الواجهة عبر **Settings → Language** أو **Settings → Preferences**. يُحفظ اختيارك.

## بنية الشفرة المصدرية

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

## البناء لنظام Windows

```powershell
.venv\Scripts\python -m pip install -r requirements.txt -r packaging/requirements-build.txt
.venv\Scripts\python -m PyInstaller --clean --noconfirm packaging/ElectrolyteCVProcessor.spec
```

يُنشأ الملف التنفيذي في `dist/`.

## الترخيص

[MIT](../../LICENSE)
