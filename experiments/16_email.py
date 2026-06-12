"""Phase 6 add-on - email notifications.

Run from PROJECT ROOT:
    $env:PYTHONPATH="."; python experiments\\16_email.py

With no SMTP_PASSWORD set, this runs in DRY-RUN and prints the composed emails.
Once you add a Gmail app password to .env, it will actually send to SMTP_USERNAME.
"""
import os
from app.notifications.email import send_ticket_email

# Send the test to yourself if creds exist, else a placeholder for the dry-run.
to = os.getenv("SMTP_USERNAME") or "customer@example.com"

print("=== Case 1: normal ticket (has a draft reply) ===")
send_ticket_email(
    to=to,
    ticket_id=1234,
    category="Billing",
    priority="High",
    escalated=False,
    draft_subject="Refund request for double charge",
    draft_body=(
        "We're sorry about the double charge on your subscription. We've logged "
        "the issue and will process your refund within 3-5 business days. We'll "
        "email you once it's done."
    ),
)

print("\n=== Case 2: escalated ticket (no AI reply - human will respond) ===")
send_ticket_email(
    to=to,
    ticket_id=1235,
    category="Complaint",
    priority="Critical",
    escalated=True,
)
