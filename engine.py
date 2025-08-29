import pandas as pd
from fuzzywuzzy import process
from typing import Union, IO

STANDARD_COLUMNS = {
    "employee_id": ["ee id", "employee id", "emp id", "id"],
    "first_name": ["first name", "fname"],
    "last_name": ["last name", "lname"],
    "pay_date": ["pay date", "payroll date"],
    "gross_comp": ["gross pay", "total compensation"],
    "deferral_pct": ["401k %", "deferral %"],
    "deferral_amt": ["401k $", "deferral $"],
    "roth_pct": ["roth %"],
    "roth_amt": ["roth $"],
    "match_amt": ["match $", "employer match"]
}

PLAN_RULES = {
    "max_deferral_pct": 100,
    "max_deferral_amt": 23000,
    "match_cap": 5000
}

def _detect_ext(file_like: Union[str, IO]) -> str:
    if isinstance(file_like, str):
        name = file_like
    else:
        name = getattr(file_like, "name", "") or ""
    name = name.lower()
    return ".xlsx" if (name.endswith(".xlsx") or name.endswith(".xls")) else ".csv"

def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    col_map = {}
    for col in df.columns:
        match = None
        for std_col, aliases in STANDARD_COLUMNS.items():
            if col.lower() in aliases:
                match = std_col
                break
            best = process.extractOne(col.lower(), aliases)
            if best and best[1] > 85:
                match = std_col
                break
        if match:
            col_map[col] = match
    return df.rename(columns=col_map)

def validate_contributions(df: pd.DataFrame) -> pd.DataFrame:
    df["deferral_amt"] = pd.to_numeric(df.get("deferral_amt", 0), errors='coerce').fillna(0)
    df["roth_amt"] = pd.to_numeric(df.get("roth_amt", 0), errors='coerce').fillna(0)
    df["match_amt"] = pd.to_numeric(df.get("match_amt", 0), errors='coerce').fillna(0)
    df["total_contrib"] = df["deferral_amt"] + df["roth_amt"]
    df["over_limit"] = df["total_contrib"] > PLAN_RULES["max_deferral_amt"]
    df["match_capped"] = df["match_amt"] > PLAN_RULES["match_cap"]
    return df

def load_and_process(file_like: Union[str, IO]) -> pd.DataFrame:
    ext = _detect_ext(file_like)
    if hasattr(file_like, "seek"):
        try:
            file_like.seek(0)
        except Exception:
            pass
    if ext == ".xlsx":
        df = pd.read_excel(file_like)
    else:
        df = pd.read_csv(file_like)
    df = standardize_columns(df)
    df = validate_contributions(df)
    return df
