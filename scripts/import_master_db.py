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


payload = {key: rows(sheet) for key, sheet in SHEETS.items()}
payload["meta"] = {"source": source.name, "version": "v2"}
destination.parent.mkdir(parents=True, exist_ok=True)
destination.write_text(
    f"/* Generated from {source.name}. Do not hand-edit. */\n"
    "window.ARCHELION_MASTER_DB = "
    + json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    + ";\n",
    encoding="utf-8",
)
print(json.dumps({key: len(value) for key, value in payload.items() if isinstance(value, list)}, ensure_ascii=False))
