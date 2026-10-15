from __future__ import annotations

from ..i18n import tr

import re
import pandas as pd

from .logging_utils import log_info, log_warning

def parse_txt_to_curves(txt_path):
    "Parse electrochemical TXT files and extract Vf and Im for each CURVE."
    log_info(tr('正在解析 TXT 文件：{0}', txt_path))
    with open(txt_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    curves = {}
    current_curve = None
    header = None
    data_lines = []
    expected_columns = None

    for line in lines:
        line = line.rstrip('\n')
        if not line:
            continue

        match = re.match(r'^(CURVE\d+)\s+TABLE$', line)
        if match:
            if current_curve is not None and header is not None and data_lines:
                df = pd.DataFrame(data_lines, columns=header)
                if 'Vf' in df.columns and 'Im' in df.columns:
                    df = df[['Vf', 'Im']].copy()
                else:
                    if df.shape[1] >= 4:
                        df = df.iloc[:, [2, 3]].copy()
                        df.columns = ['Vf', 'Im']
                    else:
                        log_warning(tr('曲线 {0} 列数不足，跳过', current_curve))
                        df = None
                if df is not None and not df.empty:
                    curves[current_curve] = df

            current_curve = match.group(1)
            header = None
            data_lines = []
            expected_columns = None
            continue

        if current_curve is not None and header is None:
            if 'Pt' in line and 'T' in line and 'Vf' in line:
                header = [col.strip() for col in line.split('\t')]
                expected_columns = len(header)
                continue

        if current_curve is not None and header is not None:
            parts = line.split('\t')
            if len(parts) == expected_columns:
                row = []
                for val in parts:
                    val = val.strip()
                    if val == '':
                        row.append(None)
                    else:
                        try:
                            row.append(float(val))
                        except ValueError:
                            row.append(val)
                data_lines.append(row)

    if current_curve is not None and header is not None and data_lines:
        df = pd.DataFrame(data_lines, columns=header)
        if 'Vf' in df.columns and 'Im' in df.columns:
            df = df[['Vf', 'Im']].copy()
        else:
            if df.shape[1] >= 4:
                df = df.iloc[:, [2, 3]].copy()
                df.columns = ['Vf', 'Im']
            else:
                log_warning(tr('曲线 {0} 列数不足，跳过', current_curve))
                df = None
        if df is not None and not df.empty:
            curves[current_curve] = df

    if not curves:
        raise ValueError(tr('未解析到任何 CURVE 数据，请检查文件格式'))
    log_info(tr('成功解析 {0} 条曲线', len(curves)))
    return curves

# ================== Excel parser (legacy three-column format) ==================
def parse_excel_to_curves(excel_path):
    "Parse legacy Excel files with three headerless columns and CURVE markers in column A."
    log_info(tr('正在解析 Excel 文件（旧格式）：{0}', excel_path))
    df_raw = pd.read_excel(excel_path, header=None, names=['A', 'B', 'C'], dtype=str)
    curves = {}
    i = 0
    n_rows = len(df_raw)
    while i < n_rows:
        cell_a = str(df_raw.loc[i, 'A']).strip()
        if cell_a.startswith('CURVE'):
            curve_name = cell_a
            i += 3
            data = {'Vf': [], 'Im': []}
            while i < n_rows and not str(df_raw.loc[i, 'A']).strip().startswith('CURVE'):
                vf_val = df_raw.loc[i, 'B']
                im_val = df_raw.loc[i, 'C']
                if pd.notna(vf_val) and pd.notna(im_val):
                    try:
                        data['Vf'].append(float(vf_val))
                        data['Im'].append(float(im_val))
                    except ValueError:
                        pass
                i += 1
            if len(data['Vf']) > 0:
                curves[curve_name] = pd.DataFrame(data)
        else:
            i += 1
    if not curves:
        raise ValueError(tr('未解析到任何 CURVE 数据，请检查 Excel 格式'))
    log_info(tr('成功解析 {0} 条曲线', len(curves)))
    return curves
