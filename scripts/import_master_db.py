"""Convert the user-maintained ARCHELION workbook into a browser-loadable DB."""
import json
import math
import sys
from pathlib import Path

import pandas as pd

source = Path(sys.argv[1])
destination = Path(__file__).resolve().parents[1] / "data" / "master-db.js"

SHEETS = {
    "drops": "01_부산물_M025-M096",
    "essences": "02_정수_126",
    "equipment": "03_장비_206",
    "recipes": "04_제작_40_레시피",
    "monsterRewards": "05_몬스터_EXP_Gold",
    "sets": "06_세트효과",
    "items": "07_아이템_설명",
    "skills": "08_스킬_마스터",
    "monsterDrops": "10_몬스터_보상드롭",
    "dungeonSpawns": "11_던전_출현테이블",
}


def clean(value):
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return None
    if isinstance(value, (float, int)) and not isinstance(value, bool):
        return int(value) if float(value).is_integer() else value
    return str(value).strip()


def rows(sheet):
    frame = pd.read_excel(source, sheet_name=sheet).where(pd.notna, None)
    return [{str(key).strip(): clean(value) for key, value in row.items()} for row in frame.to_dict("records")]


def matrix(sheet):
    frame = pd.read_excel(source, sheet_name=sheet, header=None).where(pd.notna, None)
    return [[clean(value) for value in row] for row in frame.to_numpy().tolist()]


def upper_lower_grade(number):
    if number <= 2:
        return "일반"
    if number <= 4:
        return "고급"
    if number <= 10:
        return "희귀"
    if number <= 18:
        return "희귀"
    if number <= 22:
        return "영웅"
    if number <= 24:
        return "고급"
    if number <= 28:
        return "희귀"
    if number <= 32:
        return "영웅"
    if number <= 36:
        return "전설"
    return "고유"


def upper_lower_rows():
    raw = matrix("09_상의하의_DB")
    result = []
    grades = {"일반", "고급", "희귀", "영웅", "전설", "고유"}
    for row in raw[1:]:
        item_id = str(row[0] or "")
        if not item_id.startswith("UL"):
            continue
        number = int(item_id[2:])
        # UL004 이후 일부 행은 원본 시트에서 등급 셀이 비어 있어 열이 한 칸씩 왼쪽으로 밀린다.
        shifted = row[4] not in grades
        if shifted:
            category, slot, description, options, set_name, set_effect, buy, sell, sale = row[2:11]
            grade = upper_lower_grade(number)
        else:
            category, slot, grade, description, options, set_name, set_effect, buy, sell, sale = row[2:12]
        result.append({
            "ID": item_id, "이름": row[1], "분류": category, "부위": slot, "등급": grade,
            "장비 설명": description, "옵션": options, "세트": set_name,
            "세트 효과 요약": set_effect, "구매가": buy, "판매가": sell, "판매": sale,
        })
    return result


payload = {key: rows(sheet) for key, sheet in SHEETS.items()}
upper_lower = upper_lower_rows()
payload["equipment"] = [row for row in payload["equipment"] if not str(row.get("ID", "")).startswith("UL")] + upper_lower
payload["gameConfig"] = matrix("12_게임확률_CONFIG")
payload["meta"] = {"source": source.name, "version": "v4"}
destination.parent.mkdir(parents=True, exist_ok=True)
destination.write_text(
    f"/* Generated from {source.name}. Do not hand-edit. */\n"
    "window.ARCHELION_MASTER_DB = "
    + json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    + ";\n",
    encoding="utf-8",
)
print(json.dumps({key: len(value) for key, value in payload.items() if isinstance(value, list)}, ensure_ascii=False))
