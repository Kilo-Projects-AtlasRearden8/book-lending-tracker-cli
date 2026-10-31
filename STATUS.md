# STATUS.md

## What was built

A local-first Python CLI for tracking books lent to friends and borrowers, with
due dates, returns, and local JSON/CSV export. Built for Asdale Dynamics, LLC.

Files:
- `book_lender.py` — the CLI (stdlib only, no dependencies)
- `test_book_lender.py` — unit tests focused on date math
- `LICENSE` — MIT License, Copyright (c) 2026 Asdale Dynamics, LLC
- `README.md` — usage guide, credits Asdale Dynamics, LLC
- `STATUS.md` — this file

## How to run

```bash
python3 book_lender.py --help

# Add a book and a borrower
python3 book_lender.py add-book "The Massive AI Manual" --author "Dylan Asdale"
python3 book_lender.py add-borrower "Sam"

# Lend a book (due in 14 days by default)
python3 book_lender.py lend 1 1

# Custom due date
python3 book_lender.py lend 1 1 --due-date 2026-12-01

# List active loans and overdue books
python3 book_lender.py list-loans
python3 book_lender.py overdue

# Mark a loan returned
python3 book_lender.py return 1

# Export data
python3 book_lender.py export-json backup.json
python3 book_lender.py export-csv loans.csv
```

All data stays in the `data/` folder as plain JSON. No API keys, no accounts,
no network.

## Verification results

- `python3 -m unittest test_book_lender.py -v` → 11 tests, all OK
  - default 14-day due date
  - custom `--due-days`
  - explicit `--due-date`
  - overdue detection before/after due date
  - days-overdue date math
  - returned loans no longer overdue / not active
  - double-return and re-lend of active book raise errors
  - date parsing (ISO and YYYY-MM-DD, empty/invalid)
  - CSV export includes `days_overdue` column
- CLI smoke test end-to-end: add-book, add-borrower, lend, list-loans,
  overdue, return, export-json, export-csv all run successfully
- Python 3.13.5, standard library only

## Known gaps

- No `--available` / `--lent` filtering implemented on `list-books` (flags
  accepted but not applied)
- No edit/delete commands for books, borrowers, or loans
- Data files are not encrypted; local-first means physical access = data access
- IDs are never reused after deletion (no deletion exists yet)
- No configuration file; data dir overridable via `BOOK_LENDER_DATA_DIR` env var
