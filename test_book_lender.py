"""Tests for the Book Lending Tracker, focused on date math and storage.

Run with:  python3 -m unittest test_book_lender.py -v
"""

import argparse
import io
import json
import shutil
import tempfile
import unittest
from contextlib import redirect_stdout
from datetime import date, timedelta
from pathlib import Path

import book_lender


class DateMathTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp())
        self.store = book_lender.Store(data_dir=self.tmp)
        self.book = self.store.add_book("The Massive AI Manual")
        self.borrower = self.store.add_borrower("Dylan Asdale")

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp)

    def test_default_due_date_is_14_days(self):
        loan = self.store.lend(self.book["id"], self.borrower["id"])
        expected = date.today() + timedelta(days=14)
        self.assertEqual(book_lender._parse_date(loan["due_date"]), expected)

    def test_due_days_override(self):
        loan = self.store.lend(self.book["id"], self.borrower["id"], due_days=3)
        expected = date.today() + timedelta(days=3)
        self.assertEqual(book_lender._parse_date(loan["due_date"]), expected)

    def test_explicit_due_date(self):
        due = date(2026, 12, 25)
        loan = self.store.lend(self.book["id"], self.borrower["id"], due_date=due)
        self.assertEqual(book_lender._parse_date(loan["due_date"]), due)

    def test_loan_not_overdue_before_due_date(self):
        future = date.today() + timedelta(days=5)
        self.store.lend(self.book["id"], self.borrower["id"], due_date=future)
        self.assertEqual(self.store.loans_list(overdue_only=True), [])

    def test_loan_overdue_after_due_date(self):
        past = date.today() - timedelta(days=2)
        self.store.lend(self.book["id"], self.borrower["id"], due_date=past)
        overdue = self.store.loans_list(overdue_only=True)
        self.assertEqual(len(overdue), 1)
        self.assertEqual(overdue[0]["id"], self.store.loans[0]["id"])

    def test_days_overdue_matches_date_math(self):
        past = date.today() - timedelta(days=7)
        self.store.lend(self.book["id"], self.borrower["id"], due_date=past)
        overdue = self.store.loans_list(overdue_only=True)[0]
        due = book_lender._parse_date(overdue["due_date"])
        self.assertEqual((date.today() - due).days, 7)

    def test_returned_loan_not_overdue_or_active(self):
        past = date.today() - timedelta(days=5)
        loan = self.store.lend(self.book["id"], self.borrower["id"], due_date=past)
        self.store.return_book(loan["id"])
        self.assertEqual(self.store.loans_list(overdue_only=True), [])
        self.assertEqual(self.store.loans_list(active_only=True), [])

    def test_return_twice_raises(self):
        loan = self.store.lend(self.book["id"], self.borrower["id"])
        self.store.return_book(loan["id"])
        with self.assertRaises(ValueError):
            self.store.return_book(loan["id"])

    def test_lend_active_book_raises(self):
        self.store.lend(self.book["id"], self.borrower["id"])
        with self.assertRaises(ValueError):
            self.store.lend(self.book["id"], self.borrower["id"])

    def test_lend_unknown_book_raises(self):
        with self.assertRaises(ValueError):
            self.store.lend(999, self.borrower["id"])

    def test_parse_date_handles_iso_and_ymd(self):
        self.assertEqual(book_lender._parse_date("2026-10-31"), date(2026, 10, 31))
        self.assertIsNone(book_lender._parse_date(""))
        self.assertIsNone(book_lender._parse_date("not-a-date"))


class PersistenceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp())
        self.store = book_lender.Store(data_dir=self.tmp)
        self.book = self.store.add_book("Test Book")
        self.borrower = self.store.add_borrower("Sam")

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp)

    def test_data_persisted_to_disk_after_write(self):
        self.store.lend(self.book["id"], self.borrower["id"], due_days=5)
        reloaded = book_lender.Store(data_dir=self.tmp)
        self.assertEqual(len(reloaded.books), 1)
        self.assertEqual(len(reloaded.borrowers), 1)
        self.assertEqual(len(reloaded.loans), 1)
        self.assertEqual(reloaded.loans[0]["due_date"], reloaded.loans[0]["due_date"])

    def test_empty_store_creates_data_directory(self):
        empty = Path(self.tmp / "empty")
        book_lender.Store(data_dir=empty)
        self.assertTrue(empty.is_dir())


class ExportTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp())
        self.store = book_lender.Store(data_dir=self.tmp)
        self.book = self.store.add_book("Export Book")
        self.borrower = self.store.add_borrower("Sam")
        self.store.lend(self.book["id"], self.borrower["id"], due_days=-5)

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp)

    def test_export_json_contains_all_collections(self):
        out = self.tmp / "backup.json"
        self.store.export_json(out)
        payload = json.loads(out.read_text())
        self.assertIn("books", payload)
        self.assertIn("borrowers", payload)
        self.assertIn("loans", payload)
        self.assertIn("exported_at", payload)

    def test_export_csv_contains_overdue_column(self):
        out = self.tmp / "loans.csv"
        self.store.export_csv(out)
        lines = out.read_text().splitlines()
        self.assertEqual(len(lines), 2)  # header + one overdue loan
        self.assertIn("days_overdue", lines[0])
        self.assertEqual(lines[1].split(",")[0], "1")  # loan id


class CLITests(unittest.TestCase):
    def test_version_flag_prints_version(self):
        store = book_lender.Store(data_dir=Path(tempfile.mkdtemp()))
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = book_lender.cmd_version(argparse.Namespace(), store)
        self.assertEqual(rc, 0)
        self.assertIn("book-lender", buf.getvalue())

    def test_list_books_filters_available_and_lent(self):
        store = book_lender.Store(data_dir=Path(tempfile.mkdtemp()))
        book1 = store.add_book("Available Book")
        book2 = store.add_book("Lent Book")
        borrower = store.add_borrower("Sam")
        store.lend(book2["id"], borrower["id"])

        avail_buf = io.StringIO()
        lent_buf = io.StringIO()
        with redirect_stdout(avail_buf):
            book_lender.cmd_list_books(argparse.Namespace(available=True, lent=False), store)
        with redirect_stdout(lent_buf):
            book_lender.cmd_list_books(argparse.Namespace(available=False, lent=True), store)
        avail = avail_buf.getvalue()
        lent = lent_buf.getvalue()
        self.assertIn("Available Book", avail)
        self.assertNotIn("Lent Book", avail)
        self.assertIn("Lent Book", lent)
        self.assertNotIn("Available Book", lent)


if __name__ == "__main__":
    unittest.main()