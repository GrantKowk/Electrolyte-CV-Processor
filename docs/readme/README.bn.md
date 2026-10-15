# Electrolyte CV Processor

<details open>
<summary>Languages</summary>

[English](../../README.md) · [简体中文](README.zh-CN.md) · [繁體中文](README.zh-TW.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Deutsch](README.de.md) · [Français](README.fr.md) · [Español](README.es.md) · [Italiano](README.it.md) · [Português (Brasil)](README.pt-BR.md) · [Русский](README.ru.md) · [Українська](README.uk.md) · [Polski](README.pl.md) · [Nederlands](README.nl.md) · [Svenska](README.sv.md) · [Suomi](README.fi.md) · [Čeština](README.cs.md) · [Türkçe](README.tr.md) · [Ελληνικά](README.el.md) · [العربية](README.ar.md) · [فارسی](README.fa.md) · [עברית](README.he.md) · [हिन्दी](README.hi.md) · **বাংলা** · [اردو](README.ur.md) · [Bahasa Indonesia](README.id.md) · [Bahasa Melayu](README.ms.md) · [Tiếng Việt](README.vi.md) · [ไทย](README.th.md) · [Română](README.ro.md)

</details>

Python, PySide6 ও Matplotlib দিয়ে তৈরি ইলেক্ট্রোলাইটের সাইক্লিক ভোল্টামেট্রি (CV) বিশ্লেষণের ডেস্কটপ টুল। ইন্টারফেস ইংরেজি ও সরলীকৃত চীনা সমর্থন করে; ডিফল্ট ভাষা ইংরেজি।

## বৈশিষ্ট্য

- Gamry DTA/TXT ও সমর্থিত Excel কার্ভ ফাইল আমদানি করুন।
- চক্র স্বয়ংক্রিয়ভাবে বা নিজে নির্বাচন করে জারণ বা বিজারণ স্ক্যান বিশ্লেষণ করুন।
- নির্ধারিত স্ক্যান হার থেকে সমাকলিত ক্ষেত্রফল ও চার্জ হিসাব করুন।
- CV কার্ভ, পিক ও সূচনা বিভব, রেফারেন্স চক্রের তুলনায় স্থানান্তর এবং মান যাচাই দেখুন।
- Excel ওয়ার্কবুক ও চিত্র রপ্তানি করুন; প্রদর্শন ও প্রক্রিয়াকরণের পছন্দ সংরক্ষণ করুন।

## চালানো

Windows, Python 3.10 বা নতুন সংস্করণ। প্রকল্পের মূল ফোল্ডারে কমান্ডগুলো চালান।

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python main.py
```

## ব্যবহার

1. CV ফাইল যোগ করুন। টেক্সট টেবিলে `Vf` ও `Im` কলামসহ `CURVE... TABLE` অংশ থাকতে হবে।
2. বিশ্লেষণ মোড, ভোল্টেজ পরিসর, স্ক্যান হার ও চক্র নির্বাচন নির্ধারণ করুন।
3. প্রক্রিয়াকরণ চালান, ফলাফল দেখুন এবং রপ্তানি করুন।
4. **Settings → Language** বা **Settings → Preferences** থেকে ইন্টারফেসের ভাষা বদলান। আপনার পছন্দ সংরক্ষিত হয়।

## সোর্স কোডের বিন্যাস

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

## Windows বিল্ড

```powershell
.venv\Scripts\python -m pip install -r requirements.txt -r packaging/requirements-build.txt
.venv\Scripts\python -m PyInstaller --clean --noconfirm packaging/ElectrolyteCVProcessor.spec
```

এক্সিকিউটেবল ফাইল `dist/`-এ তৈরি হয়।

## লাইসেন্স

[MIT](../../LICENSE)
