"""Lending Club accepted loans 2007-2018 — chunked clean + analyse (real data, CC0).
Business question: which grades and purposes price risk correctly — where is
the charge-off rate highest relative to the interest charged, and what do
application-time signals (FICO, income, DTI, term, purpose) say?
LEAKAGE RULE: risk groupings use APPLICATION-TIME fields only (grade,
sub_grade, term, purpose, annual_inc, dti, fico_range_low, emp_length,
home_ownership, verification_status, addr_state, issue_d). Post-origination
fields (out_prncp, total_pymnt, recoveries, last_pymnt_amnt) are NEVER used
as risk predictors — only for realised-return arithmetic on resolved loans.
No ML accuracy is claimed; charge-off rates are observed, descriptive rates.
The 1.67 GB file is read in chunks; only a deterministic ~100k-row sample
and aggregates are kept. Raw file is deleted after processing (see README).
Run:  python3 scripts/01_clean_analyse.py   (from the project folder)
Reads data/raw/accepted_2007_to_2018Q4.csv, writes data/clean/ + output/*.csv
"""
import os
import hashlib
import pandas as pd
import numpy as np

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(BASE, "data", "raw")
CLEAN = os.path.join(BASE, "data", "clean")
OUT = os.path.join(BASE, "output")
os.makedirs(CLEAN, exist_ok=True)
os.makedirs(OUT, exist_ok=True)

RAW_FILE = os.path.join(RAW, "accepted_2007_to_2018Q4.csv")

WANTED = ["id", "loan_amnt", "funded_amnt", "term", "int_rate", "installment",
          "grade", "sub_grade", "emp_length", "home_ownership", "annual_inc",
          "verification_status", "issue_d", "loan_status", "purpose",
          "addr_state", "dti", "delinq_2yrs", "earliest_cr_line",
          "fico_range_low", "fico_range_high", "open_acc", "revol_bal",
          "revol_util", "total_acc", "out_prncp", "total_pymnt",
          "total_rec_prncp", "total_rec_int", "recoveries", "last_pymnt_amnt",
          "application_type", "initial_list_status"]

header = pd.read_csv(RAW_FILE, nrows=0)
ALL_COLS = list(header.columns)
USECOLS = [c for c in WANTED if c in ALL_COLS]
print(f"Raw columns: {len(ALL_COLS)} | using: {len(USECOLS)}")
print("Missing wanted columns:", [c for c in WANTED if c not in ALL_COLS])

# sha256 of the raw file, for provenance (computed in chunks)
h = hashlib.sha256()
with open(RAW_FILE, "rb") as fh:
    for chunk in iter(lambda: fh.read(8 * 1024 * 1024), b""):
        h.update(chunk)
RAW_SHA256 = h.hexdigest()
RAW_BYTES = os.path.getsize(RAW_FILE)
print(f"Raw file: {RAW_BYTES:,} bytes | sha256: {RAW_SHA256}")

SAMPLE_EVERY = 23  # deterministic ~1-in-23 sample -> ~98k rows
sample_rows = []
agg_grade, agg_purpose, agg_year, agg_fico, agg_dti, agg_income, agg_term, agg_state = [], [], [], [], [], [], [], []
status_counts = {}
total_rows = 0
funded_total = 0.0
resolved_fully_paid = 0
resolved_charged_off = 0
row_idx = 0

def pct_str_to_float(s):
    if s.dtype == object:
        return pd.to_numeric(s.astype(str).str.rstrip("%"), errors="coerce")
    return pd.to_numeric(s, errors="coerce")

for chunk in pd.read_csv(RAW_FILE, usecols=USECOLS, chunksize=100000, low_memory=False):
    n = len(chunk)
    total_rows += n
    chunk["int_rate"] = pct_str_to_float(chunk["int_rate"])
    chunk["revol_util"] = pct_str_to_float(chunk["revol_util"]) if "revol_util" in chunk else np.nan
    chunk["issue_d"] = pd.to_datetime(chunk["issue_d"], format="%b-%Y", errors="coerce")
    chunk["issue_year"] = chunk["issue_d"].dt.year
    chunk["fico_band"] = pd.cut(chunk["fico_range_low"],
                                [-1, 659, 679, 699, 719, 739, 850],
                                labels=["<660", "660-679", "680-699", "700-719", "720-739", "740+"])
    chunk["dti_band"] = pd.cut(chunk["dti"],
                               [-1, 10, 15, 20, 25, 30, 100],
                               labels=["<10", "10-15", "15-20", "20-25", "25-30", "30+"])
    chunk["income_band"] = pd.cut(chunk["annual_inc"],
                                  [-1, 25000, 50000, 75000, 100000, 10**9],
                                  labels=["<25k", "25-50k", "50-75k", "75-100k", "100k+"])
    chunk["is_resolved"] = chunk["loan_status"].isin(["Fully Paid", "Charged Off"])
    chunk["is_charged_off"] = (chunk["loan_status"] == "Charged Off").astype(int)

    funded_total += float(chunk["funded_amnt"].sum())
    resolved_fully_paid += int((chunk["loan_status"] == "Fully Paid").sum())
    resolved_charged_off += int((chunk["loan_status"] == "Charged Off").sum())
    for st, c in chunk["loan_status"].value_counts().items():
        status_counts[st] = status_counts.get(st, 0) + int(c)

    # deterministic sample: every 23rd row of the whole file
    keep = ((np.arange(row_idx, row_idx + n) % SAMPLE_EVERY) == 0)
    sample_rows.append(chunk[keep])
    row_idx += n

    def agg(group_col):
        g = chunk.groupby(group_col, observed=True).agg(
            loans=("loan_amnt", "count"),
            funded=("funded_amnt", "sum"),
            avg_loan=("loan_amnt", "mean"),
            avg_int_rate=("int_rate", "mean"),
            avg_fico=("fico_range_low", "mean"),
            avg_dti=("dti", "mean"),
            avg_income=("annual_inc", "mean"),
            resolved=("is_resolved", "sum"),
            charged_off=("is_charged_off", "sum"))
        g["charge_off_rate_pct_resolved"] = (100 * g["charged_off"] / g["resolved"]).round(2)
        return g.reset_index()
    agg_grade.append(agg("grade"))
    agg_purpose.append(agg("purpose"))
    agg_year.append(agg("issue_year"))
    agg_fico.append(agg("fico_band"))
    agg_dti.append(agg("dti_band"))
    agg_income.append(agg("income_band"))
    agg_term.append(agg("term"))
    agg_state.append(agg("addr_state"))
    print(f"... processed {total_rows:,} rows")

print(f"TOTAL rows: {total_rows:,}")

def combine(parts, group_col, out_name, sort_by="funded"):
    df = pd.concat(parts, ignore_index=True)
    num = ["loans", "funded", "resolved", "charged_off"]
    df = df.groupby(group_col, observed=True).agg(
        loans=("loans", "sum"), funded=("funded", "sum"),
        resolved=("resolved", "sum"), charged_off=("charged_off", "sum"),
        avg_loan=("avg_loan", lambda s: np.average(s, weights=df.loc[s.index, "loans"])),
        avg_int_rate=("avg_int_rate", lambda s: np.average(s, weights=df.loc[s.index, "loans"])),
        avg_fico=("avg_fico", lambda s: np.average(s, weights=df.loc[s.index, "loans"])),
        avg_dti=("avg_dti", lambda s: np.average(s, weights=df.loc[s.index, "loans"])),
        avg_income=("avg_income", lambda s: np.average(s, weights=df.loc[s.index, "loans"]))).reset_index()
    df["charge_off_rate_pct_resolved"] = (100 * df["charged_off"] / df["resolved"]).round(2)
    df = df.sort_values(sort_by, ascending=False)
    df.to_csv(os.path.join(OUT, out_name), index=False)
    return df

grade = combine(agg_grade, "grade", "grade_summary.csv")
purpose = combine(agg_purpose, "purpose", "purpose_summary.csv")
year = combine(agg_year, "issue_year", "vintage_yearly.csv", sort_by="issue_year")
fico = combine(agg_fico, "fico_band", "fico_band_summary.csv", sort_by="fico_band")
dti = combine(agg_dti, "dti_band", "dti_band_summary.csv", sort_by="dti_band")
income = combine(agg_income, "income_band", "income_band_summary.csv", sort_by="income_band")
term = combine(agg_term, "term", "term_summary.csv")
state = combine(agg_state, "addr_state", "state_summary.csv")

sample = pd.concat(sample_rows, ignore_index=True)
sample.to_csv(os.path.join(CLEAN, "lending_club_sample_100k.csv"), index=False)
print(f"Sample rows kept: {len(sample):,}")

resolved = resolved_fully_paid + resolved_charged_off
co_rate = 100 * resolved_charged_off / resolved if resolved else float("nan")
kpis = {
    "raw_rows": int(total_rows),
    "raw_columns": int(len(ALL_COLS)),
    "raw_file_bytes": int(RAW_BYTES),
    "raw_file_sha256": RAW_SHA256,
    "sample_rows_kept": int(len(sample)),
    "sample_every_nth_row": SAMPLE_EVERY,
    "total_funded_usd": round(funded_total, 2),
    "loan_status_counts": status_counts,
    "resolved_loans_fully_paid_plus_charged_off": int(resolved),
    "charged_off_loans": int(resolved_charged_off),
    "charge_off_rate_pct_of_resolved": round(float(co_rate), 2),
}
with open(os.path.join(OUT, "kpis.txt"), "w") as f:
    for k, v in kpis.items():
        f.write(f"{k}: {v}\n")
print(kpis)

with open(os.path.join(OUT, "reconciliation.txt"), "w") as f:
    f.write("LENDING CLUB — RECONCILIATION (computed from the real file in chunks, 2026-11-13)\n")
    f.write(f"Raw file: accepted_2007_to_2018Q4.csv — {total_rows:,} rows x {len(ALL_COLS)} columns, "
            f"{RAW_BYTES:,} bytes, sha256 {RAW_SHA256}\n")
    f.write(f"Total funded (sum funded_amnt): USD {funded_total:,.2f}\n")
    f.write(f"Loan status counts: {status_counts}\n")
    f.write(f"Resolved (Fully Paid + Charged Off): {resolved:,} | Charged off: {resolved_charged_off:,} "
            f"| charge-off rate of resolved: {co_rate:.2f}%\n")
    f.write("Charge-off rates in output/*.csv are observed rates among RESOLVED loans only. "
            "Loans still Current / in grace period / late are excluded from the rate — "
            "2017-2018 vintages are less mature, so their rates are understated.\n")
    f.write("Sample: every 23rd row of the file, deterministic, "
            f"{len(sample):,} rows in data/clean/lending_club_sample_100k.csv.\n")
print("DONE — outputs in", OUT)
