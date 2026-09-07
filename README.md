# OCS Auto Birthday Greetings

Automated birthday greeting sender for **UP Los Baños - College of Forestry and Natural Resources (CFNR) Office of the College Secretary (OCS)**.

Fetches daily celebrants from Google Sheets (Faculty & Students), generates personalized HTML emails with animated GIFs, and sends them via Gmail SMTP.

---

## Features

- **Multi-Cohort Support**: Handles both Faculty and Students with cohort-specific email styling and address formats:
  - **Faculty**: Maroon header (`#90143c`), addressed by title/designation and nickname/firstname.
  - **Students**: Forest green header (`#0c513e`), addressed by full name.
- **Dynamic Google Sheets Sync**: Fetches live data via Google Visualization API CSV export filtered by current month tab (PHT / UTC+8).
- **Embedded Media & Phrases**:
  - Random GIF selected from `birthday_gif/` and embedded inline (`cid`).
  - Customizable phrases picked dynamically from `birthday_phrases.json`.
- **Activity Logging**: Records runs and emails sent to `birthday_greetings.log`.
- **Scheduled Delivery**: Runs daily at 8:00 AM PHT (00:00 UTC) via GitHub Actions.

---

## Project Structure

```
ocs-auto-birthday-greetings/
├── .github/
│   └── workflows/
│       └── daily_birthday.yml    # GitHub Actions cron workflow (00:00 UTC)
├── birthday_gif/                 # Folder containing birthday GIFs for attachments
├── birthday_phrases.json         # Custom body & closing greetings
├── birthday_greetings.log        # Activity execution log
├── main.py                       # Main entry point & Google Sheet parser
├── send_email.py                 # Email formatting (HTML/MIME) & SMTP sender
├── test_belated.py               # Test runner & CLI for belated birthday greetings
├── requirements.txt              # Python dependencies
└── .env                          # Local environment variables (git-ignored)
```

---

## Setup & Installation

### 1. Prerequisites
- Python 3.10+
- A Gmail account with an [App Password](https://myaccount.google.com/apppasswords) enabled.

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Create a `.env` file in the root folder:
```env
EMAIL="your_email@gmail.com"
PASSWORD="your_16_char_gmail_app_password"
```

---

## Usage

Run the script locally:

```bash
# Run for both faculty and students (default)
python main.py

# Run only for faculty
python main.py --type faculty

# Run only for students
python main.py --type students
```

---

## Testing Belated Greetings

Use [`test_belated.py`](file:///c:/devs/ocs-auto-birthday-greetings/test_belated.py) to test or manually send belated birthday greetings safely:

```bash
# 1. Safe dry-run preview with mock celebrants (no emails sent, no sheet required)
python test_belated.py --mock

# 2. Check yesterday's celebrants from Google Sheets (dry run preview)
python test_belated.py --days-ago 1

# 3. Check a specific past date (MM-DD)
python test_belated.py --date 09-05

# 4. Safe live test: send mock email routed ONLY to your own test email address
python test_belated.py --mock --test-email your_email@up.edu.ph --send

# 5. Run automated unit tests
python -m unittest test_belated.py
```

---

## Automation (GitHub Actions)

The workflow [`.github/workflows/daily_birthday.yml`](file:///.github/workflows/daily_birthday.yml) automates execution:
- **Trigger**: Runs daily at `00:00 UTC` (`8:00 AM PHT`) and supports manual trigger (`workflow_dispatch`).
- **Required Repository Secrets** (in GitHub repo `Settings -> Secrets and variables -> Actions`):
  - `EMAIL`: Sender Gmail address.
  - `PASSWORD`: Gmail App Password.
