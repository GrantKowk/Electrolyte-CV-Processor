# Electrolyte CV Processor

<details open>
<summary>Languages</summary>

[English](../../README.md) · [简体中文](README.zh-CN.md) · [繁體中文](README.zh-TW.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Deutsch](README.de.md) · [Français](README.fr.md) · [Español](README.es.md) · [Italiano](README.it.md) · [Português (Brasil)](README.pt-BR.md) · [Русский](README.ru.md) · [Українська](README.uk.md) · [Polski](README.pl.md) · [Nederlands](README.nl.md) · [Svenska](README.sv.md) · [Suomi](README.fi.md) · [Čeština](README.cs.md) · [Türkçe](README.tr.md) · [Ελληνικά](README.el.md) · [العربية](README.ar.md) · [فارسی](README.fa.md) · [עברית](README.he.md) · [हिन्दी](README.hi.md) · [বাংলা](README.bn.md) · [اردو](README.ur.md) · [Bahasa Indonesia](README.id.md) · [Bahasa Melayu](README.ms.md) · **Tiếng Việt** · [ไทย](README.th.md) · [Română](README.ro.md)

</details>

Công cụ máy tính để phân tích voltammetry vòng (CV) của chất điện ly, được xây dựng bằng Python, PySide6 và Matplotlib. Giao diện hỗ trợ tiếng Anh và tiếng Trung giản thể; mặc định là tiếng Anh.

## Tính năng

- Nhập tệp Gamry DTA/TXT và các tệp đường cong Excel được hỗ trợ.
- Chọn chu kỳ tự động hoặc thủ công và phân tích phép quét oxy hóa hoặc khử.
- Tính diện tích tích phân và điện lượng từ tốc độ quét đã đặt.
- Xem đường cong CV, thế đỉnh và thế bắt đầu, độ dịch chuyển so với chu kỳ tham chiếu và kiểm tra chất lượng.
- Xuất sổ làm việc Excel và hình; lưu tùy chọn hiển thị và xử lý.

## Chạy chương trình

Windows, Python 3.10 trở lên. Chạy các lệnh này từ thư mục gốc của dự án.

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python main.py
```

## Sử dụng

1. Thêm tệp CV. Bảng văn bản phải có các phần `CURVE... TABLE` với cột `Vf` và `Im`.
2. Đặt chế độ phân tích, khoảng điện áp, tốc độ quét và lựa chọn chu kỳ.
3. Chạy xử lý, kiểm tra kết quả và xuất.
4. Đổi ngôn ngữ giao diện qua **Settings → Language** hoặc **Settings → Preferences**. Lựa chọn được lưu lại.

## Cấu trúc mã nguồn

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

## Đóng gói Windows

```powershell
.venv\Scripts\python -m pip install -r requirements.txt -r packaging/requirements-build.txt
.venv\Scripts\python -m PyInstaller --clean --noconfirm packaging/ElectrolyteCVProcessor.spec
```

Tệp thực thi được tạo trong `dist/`.

## Giấy phép

[MIT](../../LICENSE)
