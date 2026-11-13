-- 1. Charge-off rate by grade (resolved loans only)
SELECT grade, COUNT(*) AS loans, SUM(funded_amnt) AS funded,
       AVG(int_rate) AS avg_int_rate,
       100.0 * SUM(CASE WHEN loan_status = 'Charged Off' THEN 1 ELSE 0 END)
           / NULLIF(SUM(CASE WHEN loan_status IN ('Fully Paid','Charged Off') THEN 1 ELSE 0 END), 0)
           AS charge_off_rate_pct_resolved
FROM lendingclub.loans
GROUP BY 1 ORDER BY 1;

-- 2. Charge-off rate by FICO band (application-time signal)
SELECT CASE WHEN fico_range_low < 660 THEN '<660'
            WHEN fico_range_low < 680 THEN '660-679'
            WHEN fico_range_low < 700 THEN '680-699'
            WHEN fico_range_low < 720 THEN '700-719'
            WHEN fico_range_low < 740 THEN '720-739' ELSE '740+' END AS fico_band,
       COUNT(*) AS loans, AVG(int_rate) AS avg_int_rate,
       100.0 * SUM(CASE WHEN loan_status = 'Charged Off' THEN 1 ELSE 0 END)
           / NULLIF(SUM(CASE WHEN loan_status IN ('Fully Paid','Charged Off') THEN 1 ELSE 0 END), 0)
           AS charge_off_rate_pct_resolved
FROM lendingclub.loans
GROUP BY 1 ORDER BY 1;

-- 3. Charge-off rate by purpose
SELECT purpose, COUNT(*) AS loans, SUM(funded_amnt) AS funded,
       AVG(int_rate) AS avg_int_rate,
       100.0 * SUM(CASE WHEN loan_status = 'Charged Off' THEN 1 ELSE 0 END)
           / NULLIF(SUM(CASE WHEN loan_status IN ('Fully Paid','Charged Off') THEN 1 ELSE 0 END), 0)
           AS charge_off_rate_pct_resolved
FROM lendingclub.loans
GROUP BY 1 ORDER BY funded DESC;

-- 4. Vintage: loans and charge-off rate by issue year
SELECT EXTRACT(YEAR FROM issue_d) AS issue_year, COUNT(*) AS loans,
       SUM(funded_amnt) AS funded,
       100.0 * SUM(CASE WHEN loan_status = 'Charged Off' THEN 1 ELSE 0 END)
           / NULLIF(SUM(CASE WHEN loan_status IN ('Fully Paid','Charged Off') THEN 1 ELSE 0 END), 0)
           AS charge_off_rate_pct_resolved
FROM lendingclub.loans
GROUP BY 1 ORDER BY 1;
-- NOTE: 2017-2018 vintages are less mature; their rates are understated.

-- 5. Loan status counts
SELECT loan_status, COUNT(*) AS loans FROM lendingclub.loans GROUP BY 1 ORDER BY 2 DESC;
