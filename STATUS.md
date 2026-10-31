# STATUS.md

## What was built

A local-first Python CLI for tracking books lent to friends and borrowers, with
due dates, returns, and local JSON/CSV export. Built for Asdale Dynamics, LLC.

Files:
- `book_lender.py` — the CLI (stdlib only, no dependencies, version 1.0.0)
- `test_book_lender.py` — unit tests covering date math, persistence, export, and CLI behavior
- `LICENSE` — MIT License, Copyright (c) 2026 Asdale Dynamics, LLC
- `README.md` — warm, beginner-friendly usage guide; credits Asdale Dynamics, LLC
- `STATUS.md` — this file

## How to run

```bash
python3 book_lender.py --help

# Add a book and a borrower
python3 book_lender.py add-book "The Massive AI Manual" --author "Dylan Asdale"
python3 book_lender.py add-borrower "Sam"

# Lend a book (due in 14 days by default)
python3 book_lender.py lend 1 1

# Custom due date or due-days
python3 book_lender.py lend 1 1 --due-date 2026-12-01
python3 book_lender.py lend 1 1 --due-days 7

# List books (all / available / lent out)
python3 book_lender.py list-books
python3 book_lender.py list-books --available
python3 book_lender.py list-books --lent

# List borrowers and loans
python3 book_lender.py list-borrowers
python3 book_lender.py list-loans

# See overdue books
python3 book_lender.py overdue

# Mark a loan returned
python3 book_lender.py return 1

# Export data
python3 book_lender.py export-json backup.json
python3 book_lender.py export-csv loans.csv

# Print version
python3 book_lender.py version
```

All data stays in the `data/` folder as plain JSON. No API keys, no accounts,
no network. Override the data folder with `BOOK_LENDER_DATA_DIR`.

## Verification results

- `python3 -m unittest test_book_lender.py -v` → 17 tests, all OK
  - default 14-day due date
  - custom `--due-days` and `--due-date`
  - overdue detection before/after due date
  - days-overdue date math
  - returned loans no longer overdue / not active
  - double-return, re-lend of active book, and unknown book raise errors
  - date parsing (ISO and YYYY-MM-DD, empty/invalid)
  - data persists to disk across Store instances; empty store creates data dir
  - JSON export contains all collections; CSV export has `days_overdue` column
  - `version` command prints version
  - `list-books --available` / `--lent` filtering works correctly
- CLI smoke test end-to-end: version, add-book, add-borrower, lend,
  list-books (all/available/lent), list-loans, overdue, return,
  export-json, export-csv all run successfully
- Python 3.13.5, standard library only

## Known gaps

- No edit/delete commands for books, borrowers, or loans (IDs are never reused)
- Data files are not encrypted; local-first means physical access = data access
- No configuration file; data dir overridable only via `BOOK_LENDER_DATA_DIR`
- Returns always use today's date (no backdating a return)
