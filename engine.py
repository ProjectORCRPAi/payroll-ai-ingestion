import pandas as pd
from fuzzywuzzy import process

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

def standardize_columns(df):
    col_map = {}
    for col in df.columns:
        match = None
        for std_col, aliases in STANDARD_COLUMNS.items():
            if col.lower() in aliases:
                match = std_col
                break
            else:
                best_match, score = process.extractOne(col.lower(), aliases)
                if score > 85:
                    match = std_col
                    break
        if match:
            col_map[col] = match
    return df.rename(columns=col_map)

def validate_contributions(df):
    df["deferral_amt"] = pd.to_numeric(df.get("deferral_amt", 0), errors='coerce').fillna(0)
    df["roth_amt"] = pd.to_numeric(df.get("roth_amt", 0), errors='coerce').fillna(0)
    df["match_amt"] = pd.to_numeric(df.get("match_amt", 0), errors='coerce').fillna(0)
    df["total_contrib"] = df["deferral_amt"] + df["roth_amt"]
    df["over_limit"] = df["total_contrib"] > PLAN_RULES["max_deferral_amt"]
    df["match_capped"] = df["match_amt"] > PLAN_RULES["match_cap"]
    return df

def load_and_process(filepath):
    df = pd.read_csv(filepath) if filepath.endswith(".csv") else pd.read_excel(filepath)
    df = standardize_columns(df)
    df = validate_contributions(df)
    return df
