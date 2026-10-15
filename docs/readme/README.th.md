# Electrolyte CV Processor

<details open>
<summary>Languages</summary>

[English](../../README.md) · [简体中文](README.zh-CN.md) · [繁體中文](README.zh-TW.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Deutsch](README.de.md) · [Français](README.fr.md) · [Español](README.es.md) · [Italiano](README.it.md) · [Português (Brasil)](README.pt-BR.md) · [Русский](README.ru.md) · [Українська](README.uk.md) · [Polski](README.pl.md) · [Nederlands](README.nl.md) · [Svenska](README.sv.md) · [Suomi](README.fi.md) · [Čeština](README.cs.md) · [Türkçe](README.tr.md) · [Ελληνικά](README.el.md) · [العربية](README.ar.md) · [فارسی](README.fa.md) · [עברית](README.he.md) · [हिन्दी](README.hi.md) · [বাংলা](README.bn.md) · [اردو](README.ur.md) · [Bahasa Indonesia](README.id.md) · [Bahasa Melayu](README.ms.md) · [Tiếng Việt](README.vi.md) · **ไทย** · [Română](README.ro.md)

</details>

เครื่องมือเดสก์ท็อปสำหรับวิเคราะห์ไซคลิกโวลแทมเมทรี (CV) ของอิเล็กโทรไลต์ พัฒนาด้วย Python, PySide6 และ Matplotlib อินเทอร์เฟซรองรับภาษาอังกฤษและภาษาจีนตัวย่อ โดยใช้ภาษาอังกฤษเป็นค่าเริ่มต้น

## คุณสมบัติ

- นำเข้าไฟล์ Gamry DTA/TXT และไฟล์เส้นโค้ง Excel ที่รองรับ
- เลือกรอบโดยอัตโนมัติหรือด้วยตนเอง และวิเคราะห์การสแกนออกซิเดชันหรือรีดักชัน
- คำนวณพื้นที่อินทิกรัลและประจุจากอัตราการสแกนที่กำหนด
- ดูเส้นโค้ง CV ศักย์พีกและศักย์เริ่มต้น การเลื่อนเทียบกับรอบอ้างอิง และการตรวจสอบคุณภาพ
- ส่งออกสมุดงาน Excel และรูปภาพ พร้อมบันทึกการตั้งค่าการแสดงผลและการประมวลผล

## การเรียกใช้

Windows และ Python 3.10 ขึ้นไป เรียกใช้คำสั่งจากโฟลเดอร์รากของโปรเจกต์

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python main.py
```

## วิธีใช้

1. เพิ่มไฟล์ CV ตารางข้อความต้องมีส่วน `CURVE... TABLE` พร้อมคอลัมน์ `Vf` และ `Im`
2. กำหนดโหมดวิเคราะห์ ช่วงแรงดัน อัตราการสแกน และรอบที่เลือก
3. เริ่มประมวลผล ตรวจสอบผลลัพธ์ และส่งออก
4. เปลี่ยนภาษาอินเทอร์เฟซผ่าน **Settings → Language** หรือ **Settings → Preferences** โดยระบบจะบันทึกตัวเลือกไว้

## โครงสร้างซอร์สโค้ด

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

## การบิลด์สำหรับ Windows

```powershell
.venv\Scripts\python -m pip install -r requirements.txt -r packaging/requirements-build.txt
.venv\Scripts\python -m PyInstaller --clean --noconfirm packaging/ElectrolyteCVProcessor.spec
```

ไฟล์ปฏิบัติการจะถูกสร้างใน `dist/`

## สัญญาอนุญาต

[MIT](../../LICENSE)
