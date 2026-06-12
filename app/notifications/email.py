"""Email notifications - send the customer a 'query registered + reply' email.

Uses Python's STANDARD LIBRARY (smtplib + email.message) - no new dependency.
Config comes from the environment (12-factor). If credentials are missing or
EMAIL_ENABLED is false, it runs in DRY-RUN: the message is composed and printed
but not sent, so the whole app works with zero email setup.
"""
import os
import smtplib
import ssl
from email.message import EmailMessage

from dotenv import load_dotenv

from app.observability.logger import get_logger

load_dotenv()  # ensure .env is read even when this module runs standalone
_log = get_logger()

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "465"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
EMAIL_FROM = os.getenv("EMAIL_FROM", SMTP_USERNAME or "support@example.com")
EMAIL_ENABLED = os.getenv("EMAIL_ENABLED", "true").lower() == "true"
STORE_NAME = os.getenv("STORE_NAME", "Acme Store")


def is_email_configured() -> bool:
    """True only if we can ACTUALLY send (so the UI doesn't over-promise)."""
    return EMAIL_ENABLED and bool(SMTP_PASSWORD)


def _build_message(
    to: str,
    ticket_id: int,
    category: str,
    priority: str,
    escalated: bool,
    draft_body: str | None,
) -> EmailMessage:
    """Compose ONE email: query-registered acknowledgement + the reply."""
    msg = EmailMessage()
    msg["Subject"] = f"We've received your query (Ref #{ticket_id})"
    msg["From"] = EMAIL_FROM
    msg["To"] = to

    if escalated or not draft_body:
        # Escalated tickets are answered by a human - don't send an AI reply.
        reply = (
            "Your query has been flagged for priority handling. A senior support "
            "specialist will personally reach out to you very shortly."
        )
    else:
        reply = f"Here is our initial response:\n\n{draft_body}"

    msg.set_content(
        f"Hi,\n\n"
        f"Thank you for contacting {STORE_NAME} support. Your query has been "
        f"registered with reference number #{ticket_id} "
        f"(category: {category}, priority: {priority}).\n\n"
        f"{reply}\n\n"
        f"This is an automated acknowledgement; a member of our team may follow "
        f"up if needed.\n\n"
        f"— {STORE_NAME} Support"
    )
    return msg


def send_ticket_email(
    to: str,
    ticket_id: int,
    category: str,
    priority: str,
    escalated: bool,
    draft_subject: str | None = None,
    draft_body: str | None = None,
) -> bool:
    """Send (or dry-run) the customer email. Returns True if actually sent."""
    msg = _build_message(to, ticket_id, category, priority, escalated, draft_body)

    # DRY-RUN guard: no real send unless explicitly enabled AND a password exists.
    if not EMAIL_ENABLED or not SMTP_PASSWORD:
        _log.info(
            "email_dry_run",
            extra={"fields": {"to": to, "ticket_id": ticket_id,
                              "reason": "EMAIL_ENABLED off or SMTP_PASSWORD missing"}},
        )
        print("------- EMAIL (dry-run, not sent) -------")
        print(msg)
        print("-----------------------------------------")
        return False

    try:
        ctx = ssl.create_default_context()
        if SMTP_PORT == 465:  # implicit TLS
            with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, context=ctx) as s:
                s.login(SMTP_USERNAME, SMTP_PASSWORD)
                s.send_message(msg)
        else:  # 587 / STARTTLS
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as s:
                s.starttls(context=ctx)
                s.login(SMTP_USERNAME, SMTP_PASSWORD)
                s.send_message(msg)
        _log.info("email_sent", extra={"fields": {"to": to, "ticket_id": ticket_id}})
        return True
    except Exception:
        # Never let an email failure break ticket processing - just log it.
        _log.error(
            "email_failed",
            extra={"fields": {"to": to, "ticket_id": ticket_id}},
            exc_info=True,
        )
        return False
