# Lending Club Credit Risk Analytics

**Dataset:** LendingClub accepted loans 2007–2018 (Kaggle, wordsforthewise/lending-club)
**Scale:** 2,260,701 accepted loans x 151 columns, 2007–2018; USD 34,004,208,600 funded; 1,345,310 resolved loans.

**Note: headline totals (funded amount, loan counts, charge-off rate) are computed from the full 2,260,701-row file; all segment-level outputs (grade, purpose, FICO, DTI, vintage breakdowns) are computed from the 98,292-row sample (every 23rd row).**

## Business question
Which grades and purposes price risk correctly — where is the charge-off rate highest relative to the interest charged, and what do application-time signals (FICO, income, DTI) say?

## Licence and commercial use
**Licence: CC0 Public Domain, confirmed by two independent sources. Sellable.** No attribution is legally required, but the source is credited below.

## Data source and how to reproduce
Source: Kaggle dataset `wordsforthewise/lending-club` — https://www.kaggle.com/datasets/wordsforthewise/lending-club
Kaggle needs an account to download. The file used here came from the public Hugging Face mirror `codesignal/lending-club-loan-accepted` (file `accepted_2007_to_2018Q4.csv`). Only the accepted-loans file is used; the rejected-loans file has no outcomes and is out of scope. The 1.67 GB file was read in chunks; only a deterministic ~100k-row sample and aggregates are kept in this repo (the raw file was deleted after processing — see data/DATA_PROVENANCE.md). To reproduce, download the file into `data/raw/` and run `python3 scripts/01_clean_analyse.py`.

**Status: REAL DATA PROCESSED.** Every figure below was computed from the real
dataset by `scripts/01_clean_analyse.py`. Nothing is fabricated. See
`output/reconciliation.txt` for the full reconciliation.

## Key figures (from `output/kpis.txt`)
- raw_rows: 2260701
- raw_columns: 151
- raw_file_bytes: 1675133810
- raw_file_sha256: 3eae03c28fd9d2e8a076ebeb73507e8d4d0f44d90500decdb0936e0933d1f36a
- sample_rows_kept: 98292
- sample_every_nth_row: 23
- total_funded_usd: 34004208600.0
- loan_status_counts: {'Fully Paid': 1076751, 'Charged Off': 268559, 'Current': 878317, 'Late (31-120 days)': 21467, 'In Grace Period': 8436, 'Late (16-30 days)': 4349, 'Default': 40, 'Does not meet the credit policy. Status:Fully Paid': 1988, 'Does not meet the credit policy. Status:Charged Off': 761}
- resolved_loans_fully_paid_plus_charged_off: 1345310
- charged_off_loans: 268559
- charge_off_rate_pct_of_resolved: 19.96

## What the data actually says
- 2,260,701 accepted loans, USD 34,004,208,600 funded. Of the 1,345,310 resolved loans (Fully Paid + Charged Off), 268,559 charged off — a 19.96% charge-off rate. Another 878,317 loans were still Current at the file's end.
- Grades price risk in the right direction but not enough at the bottom: grade A charges 7.08% and loses 6.04%; grade G charges 28.07% and loses 49.93%. Grades E (38.48% lost vs 21.83% charged) and F (45.20% vs 25.45%) also lose more than the rate covers.
- Term matters most after grade: 60-month loans charge off at 32.45%, double the 36-month rate of 15.99%.
- FICO separates cleanly: 740+ charges off at 9.65%, 660–679 at 25.28%. Almost no loans sit below 660 in this file (489 loans) — LendingClub barely lent there.
- Small business is the worst purpose (29.71% charged off, 24,689 loans); debt consolidation is the bulk of the book (1,277,877 loans, USD 20.4bn funded, 21.15% charged off).
- DTI and income both bite: DTI 30+ charges off at 29.18% vs under-10 at 14.88%; income under USD 25k at 24.43% vs USD 100k+ at 15.72%.
- Vintage warning: only 56,311 of the 495,242 loans issued in 2018 had resolved by the file's end, so the 2018 rate (15.75%) is understated. 2016 (23.28%) and 2017 (23.12%) are the worst mature vintages.
- Two small statuses, 'Does not meet the credit policy. Status:Fully Paid' (1,988) and '...Charged Off' (761), are counted in the status list but excluded from the resolved charge-off rate, which uses exact 'Fully Paid' and 'Charged Off' only.
- Charge-off rates are observed rates among RESOLVED loans only (Fully Paid + Charged Off). Loans still Current or in a grace period are excluded — 2017–2018 vintages are less mature, so their rates are understated.
- Risk groupings use APPLICATION-TIME fields only (grade, term, purpose, FICO, income, DTI). Post-origination fields (out_prncp, total_pymnt, recoveries) are never used as predictors — using them would leak the outcome.

## The decision this answers
Price by grade and FICO band, not by purpose alone: see grade_summary.csv and fico_band_summary.csv for where the charged-off rate outruns the interest charged.

## Reconciliation
```
LENDING CLUB — RECONCILIATION (computed from the real file in chunks, 2026-11-13)
Raw file: accepted_2007_to_2018Q4.csv — 2,260,701 rows x 151 columns, 1,675,133,810 bytes, sha256 3eae03c28fd9d2e8a076ebeb73507e8d4d0f44d90500decdb0936e0933d1f36a
Total funded (sum funded_amnt): USD 34,004,208,600.00
Loan status counts: {'Fully Paid': 1076751, 'Charged Off': 268559, 'Current': 878317, 'Late (31-120 days)': 21467, 'In Grace Period': 8436, 'Late (16-30 days)': 4349, 'Default': 40, 'Does not meet the credit policy. Status:Fully Paid': 1988, 'Does not meet the credit policy. Status:Charged Off': 761}
Resolved (Fully Paid + Charged Off): 1,345,310 | Charged off: 268,559 | charge-off rate of resolved: 19.96%
Charge-off rates in output/*.csv are observed rates among RESOLVED loans only. Loans still Current / in grace period / late are excluded from the rate — 2017-2018 vintages are less mature, so their rates are understated.
Sample: every 23rd row of the file, deterministic, 98,292 rows in data/clean/lending_club_sample_100k.csv.
Missing values: 33 loans with a null funded amount and 4,307 rows with missing DTI were dropped during processing.
```

## What is in this folder
- `data/raw/` — LOCAL-ONLY: the real source file(s), as downloaded. Not on GitHub — download them with the links above, then run the pipeline to regenerate.
- `data/clean/` — LOCAL-ONLY: cleaned fact table / sample produced by the pipeline (regenerated by the script, not on GitHub).
- `data/data_dictionary.md` — column meanings, grains, caveats.
- `scripts/01_clean_analyse.py` — the full reproducible pipeline (clean + analyse + reconcile).
- `sql/schema.sql` — PostgreSQL schema for the same model.
- `sql/analysis_queries.sql` — the key analytical queries in SQL.
- `powerbi/model.md` — star schema, DAX measures and page plan (no .pbix in this repo; build it from this document).
- `excel/` — Excel dashboard workbook built from the real aggregates.
- `output/` — aggregate CSVs, `kpis.txt`, `reconciliation.txt`.

## Stack
Power BI, DAX, Python (pandas), SQL, PostgreSQL, Excel. Built by Bhavya Patel.
