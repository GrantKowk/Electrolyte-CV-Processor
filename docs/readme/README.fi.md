# Electrolyte CV Processor

<details open>
<summary>Languages</summary>

[English](../../README.md) · [简体中文](README.zh-CN.md) · [繁體中文](README.zh-TW.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Deutsch](README.de.md) · [Français](README.fr.md) · [Español](README.es.md) · [Italiano](README.it.md) · [Português (Brasil)](README.pt-BR.md) · [Русский](README.ru.md) · [Українська](README.uk.md) · [Polski](README.pl.md) · [Nederlands](README.nl.md) · [Svenska](README.sv.md) · **Suomi** · [Čeština](README.cs.md) · [Türkçe](README.tr.md) · [Ελληνικά](README.el.md) · [العربية](README.ar.md) · [فارسی](README.fa.md) · [עברית](README.he.md) · [हिन्दी](README.hi.md) · [বাংলা](README.bn.md) · [اردو](README.ur.md) · [Bahasa Indonesia](README.id.md) · [Bahasa Melayu](README.ms.md) · [Tiếng Việt](README.vi.md) · [ไทย](README.th.md) · [Română](README.ro.md)

</details>

Pythonilla, PySide6:lla ja Matplotlibilla toteutettu työpöytätyökalu elektrolyyttien syklisen voltammetrian (CV) analyysiin. Käyttöliittymän kielet ovat englanti ja yksinkertaistettu kiina; oletuskieli on englanti.

## Ominaisuudet

- Tuo Gamry DTA/TXT -tiedostoja ja tuettuja Excel-käyrätiedostoja.
- Valitse syklit automaattisesti tai käsin ja analysoi hapetus- tai pelkistyspyyhkäisyjä.
- Laske integraalipinta-alat ja varaus asetetun pyyhkäisynopeuden perusteella.
- Tarkastele CV-käyriä, huippu- ja alkamispotentiaaleja, siirtymiä vertailusykliin nähden sekä laaduntarkistuksia.
- Vie Excel-työkirjoja ja kuvia sekä tallenna näyttö- ja käsittelyasetukset.

## Käynnistys

Windows, Python 3.10 tai uudempi. Suorita komennot projektin juurihakemistossa.

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python main.py
```

## Käyttö

1. Lisää CV-tiedostot. Tekstitaulukoissa on oltava `CURVE... TABLE` -osiot sekä sarakkeet `Vf` ja `Im`.
2. Aseta analyysitila, jännitealue, pyyhkäisynopeus ja syklien valinta.
3. Käynnistä käsittely, tarkista tulokset ja vie ne.
4. Vaihda käyttöliittymän kieli kohdassa **Settings → Language** tai **Settings → Preferences**. Valinta tallennetaan.

## Lähdekoodin rakenne

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

## Windows-koonti

```powershell
.venv\Scripts\python -m pip install -r requirements.txt -r packaging/requirements-build.txt
.venv\Scripts\python -m PyInstaller --clean --noconfirm packaging/ElectrolyteCVProcessor.spec
```

Suoritettava tiedosto luodaan hakemistoon `dist/`.

## Lisenssi

[MIT](../../LICENSE)
