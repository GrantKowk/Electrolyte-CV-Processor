# Electrolyte CV Processor

<details open>
<summary>Languages</summary>

[English](../../README.md) · [简体中文](README.zh-CN.md) · [繁體中文](README.zh-TW.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Deutsch](README.de.md) · [Français](README.fr.md) · [Español](README.es.md) · [Italiano](README.it.md) · [Português (Brasil)](README.pt-BR.md) · [Русский](README.ru.md) · [Українська](README.uk.md) · [Polski](README.pl.md) · [Nederlands](README.nl.md) · [Svenska](README.sv.md) · [Suomi](README.fi.md) · [Čeština](README.cs.md) · [Türkçe](README.tr.md) · [Ελληνικά](README.el.md) · [العربية](README.ar.md) · [فارسی](README.fa.md) · [עברית](README.he.md) · [हिन्दी](README.hi.md) · [বাংলা](README.bn.md) · [اردو](README.ur.md) · **Bahasa Indonesia** · [Bahasa Melayu](README.ms.md) · [Tiếng Việt](README.vi.md) · [ไทย](README.th.md) · [Română](README.ro.md)

</details>

Alat desktop untuk analisis voltametri siklik (CV) elektrolit, dibuat dengan Python, PySide6, dan Matplotlib. Antarmuka mendukung bahasa Inggris dan Mandarin sederhana; bahasa Inggris adalah bahasa bawaan.

## Fitur

- Impor file Gamry DTA/TXT dan file kurva Excel yang didukung.
- Pilih siklus secara otomatis atau manual dan analisis pemindaian oksidasi atau reduksi.
- Hitung luas integral dan muatan berdasarkan laju pemindaian yang ditetapkan.
- Lihat kurva CV, potensial puncak dan awal, pergeseran terhadap siklus referensi, serta pemeriksaan kualitas.
- Ekspor buku kerja Excel dan gambar; simpan preferensi tampilan dan pemrosesan.

## Menjalankan

Windows, Python 3.10 atau lebih baru. Jalankan perintah ini dari direktori utama proyek.

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python main.py
```

## Penggunaan

1. Tambahkan file CV. Tabel teks harus memiliki bagian `CURVE... TABLE` dengan kolom `Vf` dan `Im`.
2. Atur mode analisis, rentang tegangan, laju pemindaian, dan pilihan siklus.
3. Jalankan pemrosesan, periksa hasilnya, lalu ekspor.
4. Ubah bahasa antarmuka melalui **Settings → Language** atau **Settings → Preferences**. Pilihan Anda disimpan.

## Struktur kode sumber

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

## Build Windows

```powershell
.venv\Scripts\python -m pip install -r requirements.txt -r packaging/requirements-build.txt
.venv\Scripts\python -m PyInstaller --clean --noconfirm packaging/ElectrolyteCVProcessor.spec
```

File yang dapat dijalankan dibuat di `dist/`.

## Lisensi

[MIT](../../LICENSE)
