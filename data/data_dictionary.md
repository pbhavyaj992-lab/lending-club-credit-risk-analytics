# Data dictionary — Lending Club accepted loans (raw file, 151 columns)

Only the ~30 columns used by the pipeline are listed; the full dictionary is the
Lending Club data dictionary that ships with the Kaggle dataset.

| Column | Notes |
|---|---|
| id | Loan ID |
| loan_amnt / funded_amnt | Listed / funded amount (USD) |
| term | ' 36 months' or ' 60 months' |
| int_rate | Interest rate (%; stored with a % sign in some copies — the pipeline strips it) |
| installment | Monthly payment (USD) |
| grade / sub_grade | A–G, A1–G5 — assigned at origination |
| emp_length, home_ownership, annual_inc | Application-time borrower facts |
| verification_status | Verified / Source Verified / Not Verified |
| issue_d | Issue month (e.g. Jan-2015) |
| loan_status | Fully Paid / Charged Off / Current / Late (31-120 days) / In Grace Period / Late (16-30 days) / Default / Does not meet credit policy. Status was 'Fully Paid' or 'Charged Off' for resolved loans |
| purpose | debt_consolidation, credit_card, home_improvement, … |
| addr_state | Borrower state |
| dti | Debt-to-income ratio at application |
| fico_range_low / fico_range_high | FICO band at application |
| revol_util | Revolving utilisation (%) |
| out_prncp, total_pymnt, total_rec_prncp, total_rec_int, recoveries, last_pymnt_amnt | POST-ORIGINATION outcomes — realised-return arithmetic only, never predictors |

Sample: `data/clean/lending_club_sample_100k.csv` (every 23rd row, deterministic).
Aggregates in `output/*.csv` cover all loans.
