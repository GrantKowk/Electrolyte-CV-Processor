# Electrolyte CV Processor

<details open>
<summary>Languages</summary>

[English](../../README.md) · [简体中文](README.zh-CN.md) · [繁體中文](README.zh-TW.md) · [日本語](README.ja.md) · **한국어** · [Deutsch](README.de.md) · [Français](README.fr.md) · [Español](README.es.md) · [Italiano](README.it.md) · [Português (Brasil)](README.pt-BR.md) · [Русский](README.ru.md) · [Українська](README.uk.md) · [Polski](README.pl.md) · [Nederlands](README.nl.md) · [Svenska](README.sv.md) · [Suomi](README.fi.md) · [Čeština](README.cs.md) · [Türkçe](README.tr.md) · [Ελληνικά](README.el.md) · [العربية](README.ar.md) · [فارسی](README.fa.md) · [עברית](README.he.md) · [हिन्दी](README.hi.md) · [বাংলা](README.bn.md) · [اردو](README.ur.md) · [Bahasa Indonesia](README.id.md) · [Bahasa Melayu](README.ms.md) · [Tiếng Việt](README.vi.md) · [ไทย](README.th.md) · [Română](README.ro.md)

</details>

Python, PySide6, Matplotlib로 만든 전해액 순환 전압전류법(CV) 분석용 데스크톱 도구입니다. 인터페이스는 영어와 중국어 간체를 지원하며 기본 언어는 영어입니다.

## 기능

- Gamry DTA/TXT 및 지원되는 Excel 곡선 파일을 가져옵니다.
- 사이클을 자동 또는 수동으로 선택하고 산화 또는 환원 주사를 분석합니다.
- 설정한 주사 속도로 적분 면적과 전하를 계산합니다.
- CV 곡선, 피크 전위, 개시 전위, 기준 사이클 대비 이동 및 품질 검사 결과를 확인합니다.
- Excel과 그림을 내보내고 표시 및 처리 환경설정을 저장합니다.

## 실행

Windows, Python 3.10 이상. 다음 명령은 프로젝트 루트에서 실행하세요.

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python main.py
```

## 사용 방법

1. CV 파일을 추가합니다. 텍스트 곡선 표에는 `CURVE... TABLE` 구간과 `Vf`, `Im` 열이 필요합니다.
2. 분석 모드, 전압 범위, 주사 속도 및 사이클 선택을 설정합니다.
3. 처리를 실행하고 결과를 확인한 후 내보냅니다.
4. **Settings → Language** 또는 **Settings → Preferences**에서 인터페이스 언어를 변경합니다. 선택은 저장됩니다.

## 소스 구조

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

## Windows 빌드

```powershell
.venv\Scripts\python -m pip install -r requirements.txt -r packaging/requirements-build.txt
.venv\Scripts\python -m PyInstaller --clean --noconfirm packaging/ElectrolyteCVProcessor.spec
```

실행 파일은 `dist/`에 생성됩니다.

## 라이선스

[MIT](../../LICENSE)
