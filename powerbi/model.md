# Power BI model — Lending Club Credit Risk Analytics

No .pbix is in this repo (no Power BI Desktop here). Build it from this document:
load `data/clean/lending_club_sample_100k.csv` and the `output/*.csv` aggregates
(the aggregates cover all 2,260,701 loans; the sample is for loan-level visuals),
or connect Power BI to the PostgreSQL schema in `sql/schema.sql`.

## Star schema
- **FactLoans** (grain: one loan) — sample file; aggregates in output/*.csv.
  loan_amnt, funded_amnt, int_rate, dti, annual_inc, fico_range_low.
- **DimGrade** — grade (A–G), sub_grade.
- **DimPurpose** — purpose (debt_consolidation, credit_card, …).
- **DimDate** — issue_d, issue_year.
- **DimState** — addr_state.
- Relationships: FactLoans → DimGrade, → DimPurpose, → DimDate, → DimState.

## DAX measures
```dax
Loans = COUNTROWS(FactLoans)
Funded Amount = SUM(FactLoans[funded_amnt])
Avg Interest Rate = AVERAGE(FactLoans[int_rate])
Resolved Loans = CALCULATE(COUNTROWS(FactLoans),
    FactLoans[loan_status] IN {"Fully Paid", "Charged Off"})
Charged Off Loans = CALCULATE(COUNTROWS(FactLoans), FactLoans[loan_status] = "Charged Off")
Charge-Off Rate % = 100 * DIVIDE([Charged Off Loans], [Resolved Loans])
Avg FICO = AVERAGE(FactLoans[fico_range_low])
Avg DTI = AVERAGE(FactLoans[dti])
-- Charge-off rates are computed on RESOLVED loans only. Never use
-- out_prncp, total_pymnt, recoveries or last_pymnt_amnt as predictors:
-- they are only known after the loan performs.
```

## Pages
1. **Overview** — loans, funded amount, avg interest rate, charge-off rate (resolved); vintage trend.
2. **Grades** — charge-off rate vs avg interest rate by grade; where pricing does not cover risk.
3. **Borrower signals** — charge-off rate by FICO band, DTI band and income band.
4. **Purpose & geography** — charge-off rate by purpose and by state.
