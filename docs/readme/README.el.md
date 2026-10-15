# Electrolyte CV Processor

<details open>
<summary>Languages</summary>

[English](../../README.md) · [简体中文](README.zh-CN.md) · [繁體中文](README.zh-TW.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Deutsch](README.de.md) · [Français](README.fr.md) · [Español](README.es.md) · [Italiano](README.it.md) · [Português (Brasil)](README.pt-BR.md) · [Русский](README.ru.md) · [Українська](README.uk.md) · [Polski](README.pl.md) · [Nederlands](README.nl.md) · [Svenska](README.sv.md) · [Suomi](README.fi.md) · [Čeština](README.cs.md) · [Türkçe](README.tr.md) · **Ελληνικά** · [العربية](README.ar.md) · [فارسی](README.fa.md) · [עברית](README.he.md) · [हिन्दी](README.hi.md) · [বাংলা](README.bn.md) · [اردو](README.ur.md) · [Bahasa Indonesia](README.id.md) · [Bahasa Melayu](README.ms.md) · [Tiếng Việt](README.vi.md) · [ไทย](README.th.md) · [Română](README.ro.md)

</details>

Εργαλείο υπολογιστή για ανάλυση κυκλικής βολταμμετρίας (CV) ηλεκτρολυτών, με Python, PySide6 και Matplotlib. Η διεπαφή υποστηρίζει αγγλικά και απλοποιημένα κινεζικά· η προεπιλεγμένη γλώσσα είναι τα αγγλικά.

## Δυνατότητες

- Εισαγωγή αρχείων Gamry DTA/TXT και υποστηριζόμενων αρχείων καμπυλών Excel.
- Αυτόματη ή χειροκίνητη επιλογή κύκλων και ανάλυση οξειδωτικών ή αναγωγικών σαρώσεων.
- Υπολογισμός ολοκληρωμένων εμβαδών και φορτίου από τον επιλεγμένο ρυθμό σάρωσης.
- Προβολή καμπυλών CV, δυναμικών κορυφής και έναρξης, μετατοπίσεων ως προς κύκλο αναφοράς και ελέγχων ποιότητας.
- Εξαγωγή βιβλίων Excel και εικόνων· αποθήκευση προτιμήσεων προβολής και επεξεργασίας.

## Εκτέλεση

Windows, Python 3.10 ή νεότερη. Εκτελέστε τις εντολές στον ριζικό φάκελο του έργου.

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python main.py
```

## Χρήση

1. Προσθέστε αρχεία CV. Οι πίνακες κειμένου πρέπει να περιέχουν ενότητες `CURVE... TABLE` με στήλες `Vf` και `Im`.
2. Ορίστε λειτουργία ανάλυσης, εύρος τάσης, ρυθμό σάρωσης και επιλογή κύκλων.
3. Εκτελέστε την επεξεργασία, ελέγξτε τα αποτελέσματα και εξαγάγετέ τα.
4. Αλλάξτε τη γλώσσα διεπαφής από **Settings → Language** ή **Settings → Preferences**. Η επιλογή αποθηκεύεται.

## Δομή πηγαίου κώδικα

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

## Μεταγλώττιση για Windows

```powershell
.venv\Scripts\python -m pip install -r requirements.txt -r packaging/requirements-build.txt
.venv\Scripts\python -m PyInstaller --clean --noconfirm packaging/ElectrolyteCVProcessor.spec
```

Το εκτελέσιμο αρχείο δημιουργείται στο `dist/`.

## Άδεια

[MIT](../../LICENSE)
