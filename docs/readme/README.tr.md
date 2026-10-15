# Electrolyte CV Processor

<details open>
<summary>Languages</summary>

[English](../../README.md) · [简体中文](README.zh-CN.md) · [繁體中文](README.zh-TW.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Deutsch](README.de.md) · [Français](README.fr.md) · [Español](README.es.md) · [Italiano](README.it.md) · [Português (Brasil)](README.pt-BR.md) · [Русский](README.ru.md) · [Українська](README.uk.md) · [Polski](README.pl.md) · [Nederlands](README.nl.md) · [Svenska](README.sv.md) · [Suomi](README.fi.md) · [Čeština](README.cs.md) · **Türkçe** · [Ελληνικά](README.el.md) · [العربية](README.ar.md) · [فارسی](README.fa.md) · [עברית](README.he.md) · [हिन्दी](README.hi.md) · [বাংলা](README.bn.md) · [اردو](README.ur.md) · [Bahasa Indonesia](README.id.md) · [Bahasa Melayu](README.ms.md) · [Tiếng Việt](README.vi.md) · [ไทย](README.th.md) · [Română](README.ro.md)

</details>

Python, PySide6 ve Matplotlib ile geliştirilmiş, elektrolitlerin döngüsel voltametri (CV) analizi için bir masaüstü aracıdır. Arayüz İngilizce ve Basitleştirilmiş Çinceyi destekler; varsayılan dil İngilizcedir.

## Özellikler

- Gamry DTA/TXT ve desteklenen Excel eğri dosyalarını içe aktarın.
- Döngüleri otomatik veya elle seçin; yükseltgenme veya indirgenme taramalarını analiz edin.
- Ayarlanan tarama hızından integral alanlarını ve yükü hesaplayın.
- CV eğrilerini, pik ve başlangıç potansiyellerini, referans döngüye göre kaymaları ve kalite kontrollerini görüntüleyin.
- Excel çalışma kitapları ve şekiller dışa aktarın; görüntüleme ve işleme tercihlerini kaydedin.

## Çalıştırma

Windows, Python 3.10 veya üzeri. Komutları proje kök dizininde çalıştırın.

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python main.py
```

## Kullanım

1. CV dosyalarını ekleyin. Metin tablolarında `Vf` ve `Im` sütunları bulunan `CURVE... TABLE` bölümleri olmalıdır.
2. Analiz modunu, gerilim aralığını, tarama hızını ve döngü seçimini ayarlayın.
3. İşlemeyi başlatın, sonuçları inceleyin ve dışa aktarın.
4. Arayüz dilini **Settings → Language** veya **Settings → Preferences** üzerinden değiştirin. Seçiminiz kaydedilir.

## Kaynak kod yapısı

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

## Windows derlemesi

```powershell
.venv\Scripts\python -m pip install -r requirements.txt -r packaging/requirements-build.txt
.venv\Scripts\python -m PyInstaller --clean --noconfirm packaging/ElectrolyteCVProcessor.spec
```

Çalıştırılabilir dosya `dist/` içinde oluşturulur.

## Lisans

[MIT](../../LICENSE)
