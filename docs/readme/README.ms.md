# Electrolyte CV Processor

<details open>
<summary>Languages</summary>

[English](../../README.md) · [简体中文](README.zh-CN.md) · [繁體中文](README.zh-TW.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Deutsch](README.de.md) · [Français](README.fr.md) · [Español](README.es.md) · [Italiano](README.it.md) · [Português (Brasil)](README.pt-BR.md) · [Русский](README.ru.md) · [Українська](README.uk.md) · [Polski](README.pl.md) · [Nederlands](README.nl.md) · [Svenska](README.sv.md) · [Suomi](README.fi.md) · [Čeština](README.cs.md) · [Türkçe](README.tr.md) · [Ελληνικά](README.el.md) · [العربية](README.ar.md) · [فارسی](README.fa.md) · [עברית](README.he.md) · [हिन्दी](README.hi.md) · [বাংলা](README.bn.md) · [اردو](README.ur.md) · [Bahasa Indonesia](README.id.md) · **Bahasa Melayu** · [Tiếng Việt](README.vi.md) · [ไทย](README.th.md) · [Română](README.ro.md)

</details>

Alat desktop untuk analisis voltametri berkitar (CV) elektrolit, dibina dengan Python, PySide6 dan Matplotlib. Antara muka menyokong bahasa Inggeris dan bahasa Cina ringkas; bahasa lalai ialah Inggeris.

## Ciri

- Import fail Gamry DTA/TXT dan fail lengkung Excel yang disokong.
- Pilih kitaran secara automatik atau manual dan analisis imbasan pengoksidaan atau penurunan.
- Kira luas kamiran dan cas berdasarkan kadar imbasan yang ditetapkan.
- Lihat lengkung CV, keupayaan puncak dan permulaan, anjakan relatif kepada kitaran rujukan serta semakan kualiti.
- Eksport buku kerja Excel dan rajah; simpan keutamaan paparan dan pemprosesan.

## Menjalankan

Windows, Python 3.10 atau lebih baharu. Jalankan arahan ini dari direktori akar projek.

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python main.py
```

## Penggunaan

1. Tambah fail CV. Jadual teks mesti mengandungi bahagian `CURVE... TABLE` dengan lajur `Vf` dan `Im`.
2. Tetapkan mod analisis, julat voltan, kadar imbasan dan pemilihan kitaran.
3. Jalankan pemprosesan, semak hasil dan eksport.
4. Tukar bahasa antara muka melalui **Settings → Language** atau **Settings → Preferences**. Pilihan anda disimpan.

## Struktur kod sumber

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

## Binaan Windows

```powershell
.venv\Scripts\python -m pip install -r requirements.txt -r packaging/requirements-build.txt
.venv\Scripts\python -m PyInstaller --clean --noconfirm packaging/ElectrolyteCVProcessor.spec
```

Fail boleh laku dihasilkan dalam `dist/`.

## Lesen

[MIT](../../LICENSE)
