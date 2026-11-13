# Data provenance — Lending Club accepted loans

- **File processed:** `accepted_2007_to_2018Q4.csv`
- **Rows:** 2,260,701 data rows (2,260,702 lines including header) x 151 columns
- **Size:** 1,675,133,810 bytes
- **SHA-256:** 3eae03c28fd9d2e8a076ebeb73507e8d4d0f44d90500decdb0936e0933d1f36a
- **Kaggle source:** https://www.kaggle.com/datasets/wordsforthewise/lending-club
- **Copy actually downloaded (no login):** https://huggingface.co/datasets/codesignal/lending-club-loan-accepted/resolve/main/accepted_2007_to_2018Q4.csv
- **Licence:** CC0 Public Domain (confirmed by two independent sources). Sellable.
- **Processed:** 2026-11-13, in chunks of 100,000 rows, with `scripts/01_clean_analyse.py`.
  Verified totals: USD 34,004,208,600 funded; 1,345,310 resolved loans; 268,559 charged off (19.96% of resolved).
- **Raw file deleted after processing** (deliberately — 1.67 GB). Kept instead:
  `data/clean/lending_club_sample_100k.csv` (98,292 rows, every 23rd row, deterministic)
  and all aggregates in `output/*.csv`, which cover all 2,260,701 loans.
- **To reproduce:** download the file from either link above into `data/raw/` and run
  `python3 scripts/01_clean_analyse.py`. The script re-verifies row count, size and SHA-256.
