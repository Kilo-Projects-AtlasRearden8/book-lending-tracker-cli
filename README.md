# Book Lending Tracker CLI

A local-first, dependency-free Python command line tool for tracking books lent
to friends and borrowers, with due dates, returns, and local JSON/CSV export.

Built with care by **Asdale Dynamics, LLC** (Copyright (c) 2026 Asdale Dynamics, LLC).

## Who this is for

Anyone who lends books to friends and wants to remember who has what, and when
it's due. Built as part of Asdale Dynamics, LLC's focus on practical, local-first
tools that small businesses, authors, and everyday people can actually use.

## Features

- Add books and borrowers
- Lend a book with a due date (default 14 days, customizable)
- Mark loans as returned
- List books, borrowers, and active or overdue loans
- Export all data to JSON, or loans to CSV
- Zero dependencies: runs on Python 3 with the standard library only
- Local-first: all data stays in the `data/` folder on your machine
- No API keys, no accounts, no network calls

## Install

No installation required. Clone or copy this folder and run:

```bash
python3 book_lender.py --help
```

## Quick start

```bash
# Add a book
python3 book_lender.py add-book "The Massive AI Manual" --author "Dylan Asdale"

# Add a borrower
python3 book_lender.py add-borrower "Sam"

# Lend the book (due in 14 days by default)
python3 book_lender.py lend 1 1

# Or pick a due date
python3 book_lender.py lend 1 1 --due-date 2026-12-01

# See what's out
python3 book_lender.py list-loans

# See overdue books
python3 book_lender.py overdue

# Mark a loan returned
python3 book_lender.py return 1

# Export
python3 book_lender.py export-json backup.json
python3 book_lender.py export-csv loans.csv
```

All data is stored as plain JSON in the `data/` folder. Point `BOOK_LENDER_DATA_DIR`
at another folder to store data elsewhere.

## Tests

```bash
python3 -m unittest test_book_lender.py -v
```

Tests cover date math: default 14-day due dates, custom due days, explicit due
dates, overdue detection, days-overdue calculation, and return behavior.

## License

MIT License. Copyright (c) 2026 Asdale Dynamics, LLC. See `LICENSE`.

## About Asdale Dynamics, LLC

Asdale Dynamics, LLC (Indiana, formed October 2026) is founded by Dylan Asdale,
a registered nurse turned AI author and founder. The LLC focuses on
beginner-friendly AI education, books and guides, and practical tools it can
publish or sell -- including small-business and author tools like this one.

Dylan's book *The Massive AI Manual* and hub site dylanasdale.github.io explain
AI "like a friend would": plain English, step by step, never condescending.
