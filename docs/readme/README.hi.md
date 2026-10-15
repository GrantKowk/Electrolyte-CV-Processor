# Electrolyte CV Processor

<details open>
<summary>Languages</summary>

[English](../../README.md) · [简体中文](README.zh-CN.md) · [繁體中文](README.zh-TW.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Deutsch](README.de.md) · [Français](README.fr.md) · [Español](README.es.md) · [Italiano](README.it.md) · [Português (Brasil)](README.pt-BR.md) · [Русский](README.ru.md) · [Українська](README.uk.md) · [Polski](README.pl.md) · [Nederlands](README.nl.md) · [Svenska](README.sv.md) · [Suomi](README.fi.md) · [Čeština](README.cs.md) · [Türkçe](README.tr.md) · [Ελληνικά](README.el.md) · [العربية](README.ar.md) · [فارسی](README.fa.md) · [עברית](README.he.md) · **हिन्दी** · [বাংলা](README.bn.md) · [اردو](README.ur.md) · [Bahasa Indonesia](README.id.md) · [Bahasa Melayu](README.ms.md) · [Tiếng Việt](README.vi.md) · [ไทย](README.th.md) · [Română](README.ro.md)

</details>

Python, PySide6 और Matplotlib से बना इलेक्ट्रोलाइट की चक्रीय वोल्टामेट्री (CV) के विश्लेषण का डेस्कटॉप उपकरण। इंटरफ़ेस अंग्रेज़ी और सरलीकृत चीनी में उपलब्ध है; डिफ़ॉल्ट भाषा अंग्रेज़ी है।

## विशेषताएँ

- Gamry DTA/TXT और समर्थित Excel वक्र फ़ाइलें आयात करें।
- चक्रों का स्वचालित या मैनुअल चयन करें और ऑक्सीकरण या अपचयन स्कैन का विश्लेषण करें।
- निर्धारित स्कैन दर से समाकलित क्षेत्रफल और आवेश की गणना करें।
- CV वक्र, शिखर तथा आरंभ विभव, संदर्भ चक्र के सापेक्ष बदलाव और गुणवत्ता जाँच देखें।
- Excel कार्यपुस्तिकाएँ और चित्र निर्यात करें; प्रदर्शन और प्रसंस्करण प्राथमिकताएँ सहेजें।

## चलाना

Windows, Python 3.10 या नया संस्करण। आदेश प्रोजेक्ट के मूल फ़ोल्डर में चलाएँ।

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python main.py
```

## उपयोग

1. CV फ़ाइलें जोड़ें। टेक्स्ट सारणियों में `Vf` और `Im` स्तंभों वाले `CURVE... TABLE` खंड होने चाहिए।
2. विश्लेषण मोड, वोल्टेज सीमा, स्कैन दर और चक्र चयन सेट करें।
3. प्रसंस्करण चलाएँ, परिणाम देखें और निर्यात करें।
4. **Settings → Language** या **Settings → Preferences** में इंटरफ़ेस की भाषा बदलें। आपका चयन सहेजा जाता है।

## स्रोत कोड संरचना

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

## Windows बिल्ड

```powershell
.venv\Scripts\python -m pip install -r requirements.txt -r packaging/requirements-build.txt
.venv\Scripts\python -m PyInstaller --clean --noconfirm packaging/ElectrolyteCVProcessor.spec
```

निष्पादन योग्य फ़ाइल `dist/` में बनती है।

## लाइसेंस

[MIT](../../LICENSE)
