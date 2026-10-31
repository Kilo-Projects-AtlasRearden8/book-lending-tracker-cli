# Book Lending Tracker CLI

A warm, local-first Python command line tool for tracking books you lend to
friends and borrowers — complete with due dates, returns, and local JSON/CSV
export.

Built with care by **Asdale Dynamics, LLC** (Copyright (c) 2026 Asdale Dynamics, LLC).

---

## Who this is for

You loaned a book to a friend. A month passed. You can't remember who has it,
or whether it's due back. This tool is for anyone — authors, small business
owners, teachers, or just book-loving friends — who wants a simple, private way
to keep track of lent books.

It's part of Asdale Dynamics, LLC's line of practical, beginner-friendly tools.
Dylan Asdale (a registered nurse turned AI author and founder of Asdale
Dynamics, LLC) writes *The Massive AI Manual* and runs dylanasdale.github.io,
explaining technology "like a friend would": plain English, step by step, never
condescending. This CLI follows that same spirit — clear, tested, and kind to
beginners.

---

## Features

- **Add books** with title, author, and ISBN
- **Add borrowers** with name, phone, and email
- **Lend a book** with a due date (defaults to 14 days from today)
- **Mark books as returned** when they come back
- **List books** — all, available, or currently lent out
- **List borrowers** and **list loans** (active or overdue)
- **See overdue books** at a glance, including how many days they're late
- **Export your data** to JSON (everything) or CSV (loans only)
- **Zero dependencies** — runs on Python 3 with the standard library only
- **Local-first** — all your data stays on your machine in a `data/` folder as
  plain JSON files. No cloud, no accounts, no network calls, no API keys

---

## Install

Nothing to install. Just copy this folder and run:

```bash
python3 book_lender.py --help
```

You need Python 3 (3.8+ recommended). No `pip install` required.

---

## Quick start

```bash
# 1. Add a book
python3 book_lender.py add-book "The Massive AI Manual" --author "Dylan Asdale"

# 2. Add a borrower
python3 book_lender.py add-borrower "Sam"

# 3. Lend the book (due back in 14 days by default)
python3 book_lender.py lend 1 1

# Pick a specific due date instead
python3 book_lender.py lend 1 1 --due-date 2026-12-01

# Or a custom number of days
python3 book_lender.py lend 1 1 --due-days 7

# 4. See what's out
python3 book_lender.py list-loans

# 5. See only books you haven't gotten back yet
python3 book_lender.py list-books --lent

# See only books currently available on your shelf
python3 book_lender.py list-books --available

# 6. Spot overdue books
python3 book_lender.py overdue

# 7. Mark a loan returned when the book comes back
python3 book_lender.py return 1

# 8. Export your data
python3 book_lender.py export-json backup.json
python3 book_lender.py export-csv loans.csv
```

All data is stored as plain JSON in the `data/` folder next to this script. To
store data somewhere else, set the `BOOK_LENDER_DATA_DIR` environment variable
to a folder path.

---

## Commands at a glance

| Command | What it does |
|---------|--------------|
| `add-book TITLE [--author X] [--isbn Y]` | Add a book to your library |
| `add-borrower NAME [--phone X] [--email Y]` | Add a borrower |
| `lend BOOK_ID BORROWER_ID [--due-date DATE] [--due-days N]` | Lend a book |
| `return LOAN_ID` | Mark a loan as returned |
| `list-books [--available] [--lent]` | List books (all / available / lent) |
| `list-borrowers` | List borrowers |
| `list-loans [--active] [--overdue]` | List loans |
| `overdue` | Show overdue loans |
| `export-json PATH` | Export all data to JSON |
| `export-csv PATH` | Export loans to CSV |
| `version` | Print the version |

---

## Run the tests

This project is tested. Date math (due dates, overdue detection, days overdue)
is covered by unit tests:

```bash
python3 -m unittest test_book_lender.py -v
```

---

## License

MIT License. Copyright (c) 2026 Asdale Dynamics, LLC. See `LICENSE`.

---

## About Asdale Dynamics, LLC

Asdale Dynamics, LLC (Indiana, formed October 2026) is founded by Dylan Asdale,
a registered nurse turned AI author and founder. The LLC focuses on
beginner-friendly AI education, books and guides, and practical tools it can
publish or sell — including small-business and author tools like this one.

Dylan's book *The Massive AI Manual* and hub site dylanasdale.github.io explain
AI "like a friend would": plain English, step by step, never condescending.

This README and the LICENSE credit Asdale Dynamics, LLC.
