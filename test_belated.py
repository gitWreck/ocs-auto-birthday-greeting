"""
Test script and CLI runner for Belated Happy Birthday greetings.

Supports:
1. Mock test mode (generates dummy Faculty & Student celebrants).
2. Live Google Sheet query for past dates (e.g., --days-ago 1 or --date MM-DD).
3. Safe Dry-Run mode by default (prints rendered details without sending).
4. Safe Recipient Override (--test-email) so real celebrants never get test emails.
5. Standard unittest test suite (`python -m unittest test_belated.py`).
"""

import argparse
import unittest
from datetime import datetime, timezone, timedelta
from pathlib import Path
import pandas as pd

from send_email import send_email, log_activity
from main import (
    PHT,
    clean_value,
    pick_value,
    load_faculty_df,
    load_students_df,
)

CURRENT_DIR = Path(__file__).resolve().parent


def build_belated_data(is_student: bool, name: str, birthday_str: str):
    """Generates subject and label formatted specifically for belated greetings."""
    if is_student:
        subject = "Belated Happy Birthday,"
    else:
        subject = "Belated Happy Birthday!"
    return {
        "subject": subject,
        "name": name,
        "birthday_date": birthday_str,
        "is_student": is_student,
    }


def run_belated_test(
    is_student: bool,
    target_md: str,
    sheet_name: str,
    test_email: str = None,
    dry_run: bool = True,
    use_mock: bool = False,
):
    """
    Finds celebrants for target_md or uses mock data, then previews or sends belated greetings.
    """
    label = "STUDENT" if is_student else "FACULTY"
    print(f"\n--- [TEST] BELATED {label} GREETING (Date: {target_md}, Sheet: {sheet_name}) ---")

    celebrants = []

    if use_mock:
        if is_student:
            celebrants.append({
                "name": "Juan Dela Cruz (Test Student)",
                "email": test_email or "test_student@example.com",
                "birthday": f"2002-{target_md}",
            })
        else:
            celebrants.append({
                "name": "Prof. Maria Santos (Test Faculty)",
                "email": test_email or "test_faculty@example.com",
                "birthday": f"1985-{target_md}",
            })
    else:
        try:
            if is_student:
                df = load_students_df(sheet_name)
            else:
                df = load_faculty_df(sheet_name)

            df_belated = df[
                df["Birthday"].notna()
                & (df["Birthday"].dt.strftime("%m-%d") == target_md)
            ]

            for _, row in df_belated.iterrows():
                if is_student:
                    name = str(row.get("Name", "")).strip()
                else:
                    address_as = pick_value(row.get("AD"), row.get("DESIGNATION"))
                    nick_or_first = pick_value(row.get("NICKNAME"), row.get("FIRSTNAME"))
                    name = f"{address_as} {nick_or_first}".strip()

                raw_email = clean_value(row.get("Email"))
                bday_obj = row["Birthday"]
                bday_str = bday_obj.strftime("%d %b %Y") if pd.notna(bday_obj) else target_md

                celebrants.append({
                    "name": name,
                    "email": raw_email,
                    "birthday": bday_str,
                })
        except Exception as e:
            print(f"Error fetching Google Sheet for {label}: {e}")
            return

    if not celebrants:
        print(f"No {label.lower()} birthdays found for target date: {target_md}.")
        return

    print(f"Found {len(celebrants)} {label.lower()} record(s):")
    for item in celebrants:
        recipient = test_email if test_email else item["email"]
        meta = build_belated_data(is_student, item["name"], item["birthday"])

        print(f" -> Name:      {meta['name']}")
        print(f"    Birthday:  {meta['birthday_date']}")
        print(f"    Subject:   {meta['subject']} {meta['name'].title()}!")
        print(f"    Recipient: {recipient}" + (" [OVERRIDDEN TEST EMAIL]" if test_email else ""))

        if dry_run:
            print("    [DRY RUN] Email not sent. Pass --send to transmit.")
        else:
            if not recipient or "@" not in recipient:
                print(f"    [SKIP] Invalid email: {recipient}")
                continue
            try:
                send_email(
                    subject=meta["subject"],
                    receiver_email=recipient,
                    name=meta["name"],
                    birthday_date=meta["birthday_date"],
                    is_student=is_student,
                )
                log_activity(f"[TEST-BELATED-{label}] Sent belated email to {meta['name']} ({recipient})")
                print("    [SENT] Email successfully dispatched via SMTP.")
            except Exception as err:
                print(f"    [FAILED] Error sending email: {err}")


# ==============================================================================
# Unit Tests (runnable with `python -m unittest test_belated.py`)
# ==============================================================================
class TestBelatedGreetings(unittest.TestCase):

    def test_belated_student_subject(self):
        meta = build_belated_data(is_student=True, name="Juan Santos", birthday_str="01 Sep 2001")
        self.assertEqual(meta["subject"], "Belated Happy Birthday,")
        full_subject = f"{meta['subject']} {meta['name'].title()}!"
        self.assertEqual(full_subject, "Belated Happy Birthday, Juan Santos!")

    def test_belated_faculty_subject(self):
        meta = build_belated_data(is_student=False, name="Prof. Maria Cruz", birthday_str="01 Sep 1980")
        self.assertEqual(meta["subject"], "Belated Happy Birthday!")
        full_subject = f"{meta['subject']} {meta['name'].title()}!"
        self.assertEqual(full_subject, "Belated Happy Birthday! Prof. Maria Cruz!")

    def test_date_calculation(self):
        today = datetime(2026, 9, 7, tzinfo=PHT)
        yesterday = today - timedelta(days=1)
        self.assertEqual(yesterday.strftime("%m-%d"), "09-06")


# ==============================================================================
# CLI Entrypoint
# ==============================================================================
def main():
    parser = argparse.ArgumentParser(
        description="Belated Happy Birthday Test Runner & Sender"
    )
    parser.add_argument(
        "--type",
        choices=["faculty", "students", "both"],
        default="both",
        help="Cohort to target (faculty, students, or both). Default: both",
    )
    parser.add_argument(
        "--days-ago",
        type=int,
        default=1,
        help="Number of days in past to check (default: 1, i.e. yesterday).",
    )
    parser.add_argument(
        "--date",
        type=str,
        default=None,
        help="Specific past date in MM-DD format (e.g. 09-05). Overrides --days-ago.",
    )
    parser.add_argument(
        "--month",
        type=str,
        default=None,
        help="Sheet tab name (e.g., September). Defaults to month of target date.",
    )
    parser.add_argument(
        "--mock",
        action="store_true",
        help="Use mock dummy records instead of querying Google Sheets.",
    )
    parser.add_argument(
        "--test-email",
        type=str,
        default=None,
        help="Safe redirect email. If provided, all emails route here instead of real users.",
    )
    parser.add_argument(
        "--direct-name",
        type=str,
        default=None,
        help="Direct test celebrant name (e.g. \"Ma'am Lalie\"). Bypasses Google Sheets.",
    )
    parser.add_argument(
        "--direct-email",
        type=str,
        default=None,
        help="Direct test celebrant email address.",
    )
    parser.add_argument(
        "--direct-date",
        type=str,
        default=None,
        help="Direct test celebrant birthday date string (e.g. \"September 6\").",
    )
    parser.add_argument(
        "--subject",
        type=str,
        default=None,
        help="Override subject prefix (e.g. \"Happy Birthday!\" instead of belated).",
    )
    parser.add_argument(
        "--body-phrase",
        type=str,
        default=None,
        help="Custom body phrase above GIF (e.g. \"May your day be as special as you are!\").",
    )
    parser.add_argument(
        "--custom-message",
        type=str,
        default=None,
        help="Custom closing message below GIF.",
    )
    parser.add_argument(
        "--send",
        action="store_true",
        help="Actually send email via SMTP. Defaults to False (safe dry-run).",
    )

    args = parser.parse_args()

    # Determine target date
    if args.date:
        target_md = args.date
        month_name = args.month or datetime.now(PHT).strftime("%B")
    else:
        target_dt = datetime.now(PHT) - timedelta(days=args.days_ago)
        target_md = target_dt.strftime("%m-%d")
        month_name = args.month or target_dt.strftime("%B")

    dry_run = not args.send

    # Handle Direct Mode
    if args.direct_name:
        is_student = (args.type == "students")
        label = "STUDENT" if is_student else "FACULTY"
        recipient = args.direct_email or args.test_email
        bday_str = args.direct_date or target_md
        meta = build_belated_data(is_student, args.direct_name, bday_str)
        if args.subject:
            meta["subject"] = args.subject

        print("==================================================")
        print("      OCS BELATED BIRTHDAY DIRECT TEST           ")
        print("==================================================")
        print(f"Mode:          DIRECT TEST ({label})")
        print(f"Name:          {meta['name']}")
        print(f"Birthday:      {meta['birthday_date']}")
        print(f"Subject:       {meta['subject']} {meta['name']}!")
        print(f"Recipient:     {recipient}")
        if args.body_phrase:
            print(f"Body Phrase:   {args.body_phrase}")
        if args.custom_message:
            print(f"Closing Note:  {args.custom_message}")
        print(f"Action:        {'DRY RUN (Preview only)' if dry_run else 'LIVE SEND'}")
        print("==================================================")

        if dry_run:
            print("[DRY RUN] Email not sent. Pass --send to transmit.")
        else:
            if not recipient or "@" not in recipient:
                print(f"[ERROR] Invalid recipient email: {recipient}")
                return
            try:
                send_email(
                    subject=meta["subject"],
                    receiver_email=recipient,
                    name=meta["name"],
                    birthday_date=meta["birthday_date"],
                    is_student=is_student,
                    custom_message=args.custom_message,
                    body_phrase=args.body_phrase,
                )
                log_activity(f"[DIRECT-{label}] Sent birthday email to {meta['name']} ({recipient})")
                print(f"[SUCCESS] Live birthday email sent to {recipient}!")
            except Exception as err:
                print(f"[ERROR] Failed to send email: {err}")
        return

    print("==================================================")
    print("      OCS BELATED BIRTHDAY TEST RUNNER           ")
    print("==================================================")
    print(f"Mode:          {'MOCK DATA' if args.mock else 'LIVE GOOGLE SHEETS'}")
    print(f"Target Date:   {target_md}")
    print(f"Sheet Month:   {month_name}")
    print(f"Action:        {'DRY RUN (Preview only)' if dry_run else 'LIVE SEND'}")
    if args.test_email:
        print(f"Safe Email:    {args.test_email}")
    print("==================================================")

    if args.type in ("faculty", "both"):
        run_belated_test(
            is_student=False,
            target_md=target_md,
            sheet_name=month_name,
            test_email=args.test_email,
            dry_run=dry_run,
            use_mock=args.mock,
        )

    if args.type in ("students", "both"):
        run_belated_test(
            is_student=True,
            target_md=target_md,
            sheet_name=month_name,
            test_email=args.test_email,
            dry_run=dry_run,
            use_mock=args.mock,
        )


if __name__ == "__main__":
    main()
