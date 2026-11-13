-- Lending Club — PostgreSQL schema. Grain: one accepted loan.
-- Only the columns used by the pipeline are listed; the raw file has 151.
CREATE SCHEMA IF NOT EXISTS lendingclub;

CREATE TABLE lendingclub.loans (
    id BIGINT PRIMARY KEY, loan_amnt NUMERIC(10,2), funded_amnt NUMERIC(10,2),
    term TEXT, int_rate NUMERIC(5,2), installment NUMERIC(10,2),
    grade CHAR(1), sub_grade VARCHAR(2), emp_length TEXT,
    home_ownership TEXT, annual_inc NUMERIC(12,2),
    verification_status TEXT, issue_d DATE, loan_status TEXT,
    purpose TEXT, addr_state CHAR(2), dti NUMERIC(5,2),
    delinq_2yrs INT, earliest_cr_line DATE,
    fico_range_low INT, fico_range_high INT,
    open_acc INT, revol_bal NUMERIC(12,2), revol_util NUMERIC(5,2),
    total_acc INT, application_type TEXT, initial_list_status CHAR(1),
    -- post-origination fields: realised outcomes only, NEVER predictors
    out_prncp NUMERIC(12,2), total_pymnt NUMERIC(12,2),
    total_rec_prncp NUMERIC(12,2), total_rec_int NUMERIC(12,2),
    recoveries NUMERIC(12,2), last_pymnt_amnt NUMERIC(12,2));
