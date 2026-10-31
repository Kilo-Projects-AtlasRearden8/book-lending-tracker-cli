#!/usr/bin/env python3
"""Book Lending Tracker CLI.

A local-first, dependency-free command line tool for tracking books lent
to friends and borrowers, with due dates, returns, and local JSON/CSV export.

No API keys, no accounts, no network. All data stays on your machine in the
`data/` folder as plain JSON files.

Built by Asdale Dynamics, LLC (Copyright (c) 2026 Asdale Dynamics, LLC).
"""

import argparse
import csv
import json
import os
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

__version__ = "1.0.0"

DATA_DIR = Path(os.environ.get("BOOK_LENDER_DATA_DIR", Path(__file__).resolve().parent / "data"))
BOOKS_FILE = DATA_DIR / "books.json"
BORROWERS_FILE = DATA_DIR / "borrowers.json"
LOANS_FILE = DATA_DIR / "loans.json"

DATE_FORMAT = "%Y-%m-%d"


class Store:
    """Simple JSON-backed store for books, borrowers, and loans."""

    def __init__(self, data_dir: Path = DATA_DIR) -> None:
        self.data_dir = data_dir
        self.books_file = data_dir / "books.json"
        self.borrowers_file = data_dir / "borrowers.json"
        self.loans_file = data_dir / "loans.json"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.books = self._load(self.books_file)
        self.borrowers = self._load(self.borrowers_file)
        self.loans = self._load(self.loans_file)

    def _load(self, path: Path) -> list:
        if not path.exists():
            return []
        try:
            with path.open("r", encoding="utf-8") as handle:
                data = json.load(handle)
        except (json.JSONDecodeError, OSError):
            return []
        if not isinstance(data, list):
            return []
        return data

    def _save(self, path: Path, data: list) -> None:
        tmp = path.with_suffix(path.suffix + ".tmp")
        with tmp.open("w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=2, ensure_ascii=False)
            handle.write("\n")
        tmp.replace(path)

    def persist(self) -> None:
        self._save(self.books_file, self.books)
        self._save(self.borrowers_file, self.borrowers)
        self._save(self.loans_file, self.loans)

    @staticmethod
    def _next_id(items: list) -> int:
        if not items:
            return 1
        return max(int(item.get("id", 0)) for item in items) + 1

    def add_book(self, title: str, author: str = "", isbn: str = "") -> dict:
        book = {
            "id": self._next_id(self.books),
            "title": title.strip(),
            "author": author.strip(),
            "isbn": isbn.strip(),
            "created_at": _now_iso(),
        }
        self.books.append(book)
        self.persist()
        return book

    def add_borrower(self, name: str, phone: str = "", email: str = "") -> dict:
        borrower = {
            "id": self._next_id(self.borrowers),
            "name": name.strip(),
            "phone": phone.strip(),
            "email": email.strip(),
            "created_at": _now_iso(),
        }
        self.borrowers.append(borrower)
        self.persist()
        return borrower

    def find_book(self, book_id: int) -> dict | None:
        for book in self.books:
            if int(book.get("id", 0)) == book_id:
                return book
        return None

    def find_borrower(self, borrower_id: int) -> dict | None:
        for borrower in self.borrowers:
            if int(borrower.get("id", 0)) == borrower_id:
                return borrower
        return None

    def active_loan_for_book(self, book_id: int) -> dict | None:
        for loan in self.loans:
            if int(loan.get("book_id", 0)) == book_id and loan.get("returned_at") in (None, ""):
                return loan
        return None

    def lend(
        self,
        book_id: int,
        borrower_id: int,
        due_date: date | None = None,
        due_days: int | None = None,
    ) -> dict:
        book = self.find_book(book_id)
        if book is None:
            raise ValueError(f"Book id {book_id} not found")
        borrower = self.find_borrower(borrower_id)
        if borrower is None:
            raise ValueError(f"Borrower id {borrower_id} not found")
        if self.active_loan_for_book(book_id) is not None:
            raise ValueError(f"Book id {book_id} is already lent out")

        lent = date.today()
        if due_date is not None:
            due = due_date
        elif due_days is not None:
            due = lent + timedelta(days=due_days)
        else:
            due = lent + timedelta(days=14)

        loan = {
            "id": self._next_id(self.loans),
            "book_id": book_id,
            "borrower_id": borrower_id,
            "lent_at": lent.isoformat(),
            "due_date": due.isoformat(),
            "returned_at": "",
        }
        self.loans.append(loan)
        self.persist()
        return loan

    def return_book(self, loan_id: int) -> dict:
        for loan in self.loans:
            if int(loan.get("id", 0)) == loan_id:
                if loan.get("returned_at") not in (None, ""):
                    raise ValueError(f"Loan id {loan_id} was already returned")
                loan["returned_at"] = date.today().isoformat()
                self.persist()
                return loan
        raise ValueError(f"Loan id {loan_id} not found")

    def loans_list(self, active_only: bool = False, overdue_only: bool = False) -> list:
        today = date.today()
        result = []
        for loan in self.loans:
            if active_only and loan.get("returned_at") not in (None, ""):
                continue
            if overdue_only:
                if loan.get("returned_at") not in (None, ""):
                    continue
                due = _parse_date(loan.get("due_date", ""))
                if due is None or due >= today:
                    continue
            result.append(loan)
        return result

    def export_json(self, path: Path) -> None:
        payload = {
            "books": self.books,
            "borrowers": self.borrowers,
            "loans": self.loans,
            "exported_at": _now_iso(),
        }
        with path.open("w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, ensure_ascii=False)
            handle.write("\n")

    def export_csv(self, path: Path) -> None:
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerow(["loan_id", "book_id", "book_title", "borrower_id", "borrower_name",
                             "lent_at", "due_date", "returned_at", "days_overdue"])
            today = date.today()
            for loan in self.loans:
                book = self.find_book(int(loan.get("book_id", 0))) or {}
                borrower = self.find_borrower(int(loan.get("borrower_id", 0))) or {}
                due = _parse_date(loan.get("due_date", ""))
                days_overdue = ""
                if due is not None and loan.get("returned_at") in (None, "") and due < today:
                    days_overdue = (today - due).days
                writer.writerow([
                    loan.get("id", ""),
                    loan.get("book_id", ""),
                    book.get("title", ""),
                    loan.get("borrower_id", ""),
                    borrower.get("name", ""),
                    loan.get("lent_at", ""),
                    loan.get("due_date", ""),
                    loan.get("returned_at", ""),
                    days_overdue,
                ])


def _now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def _parse_date(value: str) -> date | None:
    if not value:
        return None
    try:
        return datetime.strptime(value, DATE_FORMAT).date()
    except ValueError:
        try:
            return datetime.fromisoformat(value).date()
        except ValueError:
            return None


def _format_loan(loan: dict, store: Store) -> str:
    book = store.find_book(int(loan.get("book_id", 0))) or {}
    borrower = store.find_borrower(int(loan.get("borrower_id", 0))) or {}
    due = _parse_date(loan.get("due_date", ""))
    overdue = ""
    if due is not None and loan.get("returned_at") in (None, "") and due < date.today():
        overdue = f" OVERDUE by {(date.today() - due).days} day(s)"
    returned = loan.get("returned_at", "")
    status = "returned" if returned else "out"
    return (
        f"#{loan.get('id', '')} {book.get('title', '(unknown book)')} -> "
        f"{borrower.get('name', '(unknown borrower)')} | lent {loan.get('lent_at', '')} | "
        f"due {loan.get('due_date', '')} | {status}{overdue}"
    )


def cmd_add_book(args: argparse.Namespace, store: Store) -> int:
    book = store.add_book(args.title, args.author, args.isbn)
    print(f"Added book #{book['id']}: {book['title']}")
    return 0


def cmd_add_borrower(args: argparse.Namespace, store: Store) -> int:
    borrower = store.add_borrower(args.name, args.phone, args.email)
    print(f"Added borrower #{borrower['id']}: {borrower['name']}")
    return 0


def cmd_lend(args: argparse.Namespace, store: Store) -> int:
    due_date = _parse_date(args.due_date) if args.due_date else None
    loan = store.lend(args.book, args.borrower, due_date=due_date, due_days=args.due_days)
    book = store.find_book(int(loan["book_id"])) or {}
    borrower = store.find_borrower(int(loan["borrower_id"])) or {}
    print(
        f"Lent #{loan['id']}: '{book.get('title', '')}' to {borrower.get('name', '')} "
        f"(due {loan['due_date']})"
    )
    return 0


def cmd_return(args: argparse.Namespace, store: Store) -> int:
    loan = store.return_book(args.loan)
    book = store.find_book(int(loan.get("book_id", 0))) or {}
    print(f"Returned #{loan['id']}: '{book.get('title', '')}' on {loan['returned_at']}")
    return 0


def cmd_list_books(args: argparse.Namespace, store: Store) -> int:
    if not store.books:
        print("No books recorded.")
        return 0
    for book in store.books:
        loan = store.active_loan_for_book(int(book.get("id", 0)))
        is_lent = loan is not None
        if args.available and is_lent:
            continue
        if args.lent and not is_lent:
            continue
        tag = "lent out" if is_lent else "available"
        print(f"#{book.get('id', '')} {book.get('title', '')} [{tag}]")
        if book.get("author"):
            print(f"      author: {book['author']}")
        if book.get("isbn"):
            print(f"      isbn: {book['isbn']}")
    return 0


def cmd_list_borrowers(args: argparse.Namespace, store: Store) -> int:
    if not store.borrowers:
        print("No borrowers recorded.")
        return 0
    for borrower in store.borrowers:
        bits = [f"#{borrower.get('id', '')} {borrower.get('name', '')}"]
        if borrower.get("phone"):
            bits.append(f"phone: {borrower['phone']}")
        if borrower.get("email"):
            bits.append(f"email: {borrower['email']}")
        print(" | ".join(bits))
    return 0


def cmd_list_loans(args: argparse.Namespace, store: Store) -> int:
    loans = store.loans_list(active_only=args.active, overdue_only=args.overdue)
    if not loans:
        print("No loans.")
        return 0
    for loan in loans:
        print(_format_loan(loan, store))
    return 0


def cmd_overdue(args: argparse.Namespace, store: Store) -> int:
    loans = store.loans_list(overdue_only=True)
    if not loans:
        print("No overdue books.")
        return 0
    for loan in loans:
        print(_format_loan(loan, store))
    return 0


def cmd_version(args: argparse.Namespace, store: Store) -> int:
    print(f"book-lender {__version__}")
    return 0


def cmd_export_json(args: argparse.Namespace, store: Store) -> int:
    store.export_json(Path(args.path))
    print(f"Exported JSON to {args.path}")
    return 0


def cmd_export_csv(args: argparse.Namespace, store: Store) -> int:
    store.export_csv(Path(args.path))
    print(f"Exported CSV to {args.path}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="book-lender",
        description="Track books lent to friends and borrowers, locally.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("add-book", help="Add a book to the library")
    p.add_argument("title", help="Book title")
    p.add_argument("--author", default="", help="Author name")
    p.add_argument("--isbn", default="", help="ISBN")
    p.set_defaults(func=cmd_add_book)

    p = sub.add_parser("add-borrower", help="Add a borrower")
    p.add_argument("name", help="Borrower name")
    p.add_argument("--phone", default="", help="Phone number")
    p.add_argument("--email", default="", help="Email address")
    p.set_defaults(func=cmd_add_borrower)

    p = sub.add_parser("lend", help="Lend a book to a borrower")
    p.add_argument("book", type=int, help="Book id")
    p.add_argument("borrower", type=int, help="Borrower id")
    p.add_argument("--due-date", help="Due date (YYYY-MM-DD)")
    p.add_argument("--due-days", type=int, help="Days from today until due (default 14)")
    p.set_defaults(func=cmd_lend)

    p = sub.add_parser("return", help="Mark a loan as returned")
    p.add_argument("loan", type=int, help="Loan id")
    p.set_defaults(func=cmd_return)

    p = sub.add_parser("list-books", help="List books")
    p.add_argument("--available", action="store_true", help=argparse.SUPPRESS)
    p.add_argument("--lent", action="store_true", help=argparse.SUPPRESS)
    p.set_defaults(func=cmd_list_books)

    p = sub.add_parser("list-borrowers", help="List borrowers")
    p.set_defaults(func=cmd_list_borrowers)

    p = sub.add_parser("list-loans", help="List loans")
    p.add_argument("--active", action="store_true", help="Show only active loans")
    p.add_argument("--overdue", action="store_true", help="Show only overdue loans")
    p.set_defaults(func=cmd_list_loans)

    p = sub.add_parser("overdue", help="List overdue loans")
    p.set_defaults(func=cmd_overdue)

    p = sub.add_parser("version", help="Print version and exit")
    p.set_defaults(func=cmd_version)

    p = sub.add_parser("export-json", help="Export all data to a JSON file")
    p.add_argument("path", help="Output file path")
    p.set_defaults(func=cmd_export_json)

    p = sub.add_parser("export-csv", help="Export all loans to a CSV file")
    p.add_argument("path", help="Output file path")
    p.set_defaults(func=cmd_export_csv)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    store = Store()
    return args.func(args, store)


if __name__ == "__main__":
    sys.exit(main())
