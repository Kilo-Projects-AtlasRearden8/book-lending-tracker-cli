"""Tests for the Book Lending Tracker, focused on date math.

Run with:  python3 -m unittest test_book_lender.py -v
"""

import os
import shutil
import tempfile
import unittest
from datetime import date, timedelta

import book_lender


class DateMathTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.mkdtemp()
        self.store = book_lender.Store(data_dir=__import__("pathlib").Path(self.tmp))
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
        loan = self.store.lend(self.book["id"], self.borrower["id"], due_date=future)
        self.assertFalse(self.store.loans_list(overdue_only=True))

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

    def test_returned_loan_not_overdue(self):
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

    def test_parse_date_handles_iso_and_ymd(self):
        self.assertEqual(book_lender._parse_date("2026-10-31"), date(2026, 10, 31))
        self.assertEqual(book_lender._parse_date(""), None)
        self.assertIsNone(book_lender._parse_date("not-a-date"))

    def test_export_csv_contains_overdue_column(self):
        past = date.today() - timedelta(days=4)
        self.store.lend(self.book["id"], self.borrower["id"], due_date=past)
        out = os.path.join(self.tmp, "loans.csv")
        self.store.export_csv(__import__("pathlib").Path(out))
        with open(out, encoding="utf-8") as handle:
            header = handle.readline()
        self.assertIn("days_overdue", header)
        body = handle.read() if False else ""
        with open(out, encoding="utf-8") as handle:
            lines = handle.readlines()
        self.assertEqual(len(lines), 2)  # header + one loan


if __name__ == "__main__":
    unittest.main()
