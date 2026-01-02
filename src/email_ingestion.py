"""
Email-based URL ingestion for Content Airlock.

This module connects to an email inbox via IMAP, extracts URLs from emails,
and processes them through the ingestion pipeline.

Supported email providers:
- Gmail (requires App Password)
- iCloud (requires App Password) 
- Outlook/Hotmail
- Any IMAP-enabled provider
"""

import argparse
import imaplib
import email
from email.header import decode_header
import re
import logging
import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional
from dotenv import load_dotenv

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from src.ingest import ingest_url

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Common IMAP servers
IMAP_SERVERS = {
    'gmail.com': 'imap.gmail.com',
    'googlemail.com': 'imap.gmail.com',
    'icloud.com': 'imap.mail.me.com',
    'me.com': 'imap.mail.me.com',
    'outlook.com': 'outlook.office365.com',
    'hotmail.com': 'outlook.office365.com',
    'yahoo.com': 'imap.mail.yahoo.com',
}

# URL extraction pattern
URL_PATTERN = re.compile(
    r'https?://[^\s<>\[\]\"\']+',
    re.IGNORECASE
)

# URLs to ignore (common in email signatures, etc.)
IGNORE_DOMAINS = [
    'unsubscribe',
    'email-tracking',
    'click.',
    'mailchimp.com',
    'sendgrid.net',
    'apple.com/legal',
    'support.apple.com',
    'google.com/settings',
]


def parse_allowed_senders(env_value: Optional[str]) -> list[str]:
    """
    Parse comma-separated list of allowed sender emails.
    Returns empty list if not configured (allows all senders).
    """
    if not env_value:
        return []
    return [addr.strip().lower() for addr in env_value.split(',') if addr.strip()]


def extract_sender_email(from_header: str) -> str:
    """
    Extract email address from a From header.
    Example: 'John Doe <john@example.com>' -> 'john@example.com'
    """
    # Try to extract email from angle brackets
    match = re.search(r'<([^>]+)>', from_header)
    if match:
        return match.group(1).lower()
    # If no angle brackets, assume the whole thing is an email
    return from_header.strip().lower()


def is_sender_allowed(from_header: str, allowed_senders: list[str]) -> bool:
    """
    Check if the sender is in the allowed list.
    If allowed_senders is empty, all senders are allowed.
    """
    if not allowed_senders:
        return True  # No restrictions if not configured
    
    sender_email = extract_sender_email(from_header)
    return sender_email in allowed_senders


def get_imap_server(email_address: str) -> str:
    """Determine IMAP server from email address."""
    domain = email_address.split('@')[-1].lower()
    
    # Check known providers
    if domain in IMAP_SERVERS:
        return IMAP_SERVERS[domain]
    
    # Default: try imap.domain
    return f'imap.{domain}'


def decode_email_subject(subject: str) -> str:
    """Decode email subject handling various encodings."""
    if subject is None:
        return ""
    
    decoded_parts = decode_header(subject)
    result = []
    for part, encoding in decoded_parts:
        if isinstance(part, bytes):
            result.append(part.decode(encoding or 'utf-8', errors='ignore'))
        else:
            result.append(part)
    return ' '.join(result)


def extract_urls_from_text(text: str) -> list[str]:
    """Extract valid article URLs from text, filtering out junk."""
    urls = URL_PATTERN.findall(text)
    
    valid_urls = []
    for url in urls:
        # Clean up trailing punctuation
        url = url.rstrip('.,;:!?)')
        
        # Skip ignored domains
        if any(ignore in url.lower() for ignore in IGNORE_DOMAINS):
            continue
        
        # Skip very short URLs (likely not articles)
        if len(url) < 20:
            continue
            
        valid_urls.append(url)
    
    return list(set(valid_urls))  # Remove duplicates


def get_email_body(msg: email.message.Message) -> str:
    """Extract text content from email message."""
    body = ""
    
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            if content_type == "text/plain":
                try:
                    payload = part.get_payload(decode=True)
                    if payload:
                        charset = part.get_content_charset() or 'utf-8'
                        body += payload.decode(charset, errors='ignore')
                except Exception as e:
                    logger.warning(f"Failed to decode email part: {e}")
    else:
        try:
            payload = msg.get_payload(decode=True)
            if payload:
                charset = msg.get_content_charset() or 'utf-8'
                body = payload.decode(charset, errors='ignore')
        except Exception as e:
            logger.warning(f"Failed to decode email body: {e}")
    
    return body


def connect_to_inbox(
    email_address: str,
    password: str,
    imap_server: Optional[str] = None
) -> imaplib.IMAP4_SSL:
    """Connect to email inbox via IMAP."""
    server = imap_server or get_imap_server(email_address)
    
    logger.info(f"Connecting to {server}...")
    
    mail = imaplib.IMAP4_SSL(server)
    mail.login(email_address, password)
    
    logger.info("Successfully connected to inbox")
    return mail


def fetch_unread_emails(
    mail: imaplib.IMAP4_SSL,
    folder: str = "INBOX",
    max_age_days: int = 7
) -> list[tuple[str, email.message.Message]]:
    """Fetch unread emails from specified folder."""
    mail.select(folder)
    
    # Search for unread emails
    # We also filter by date to avoid processing very old emails
    since_date = (datetime.now() - timedelta(days=max_age_days)).strftime("%d-%b-%Y")
    
    # Search criteria: UNSEEN (unread) and SINCE date
    status, messages = mail.search(None, f'(UNSEEN SINCE {since_date})')
    
    if status != 'OK':
        logger.warning("Failed to search emails")
        return []
    
    email_ids = messages[0].split()
    logger.info(f"Found {len(email_ids)} unread emails")
    
    emails = []
    for email_id in email_ids:
        status, msg_data = mail.fetch(email_id, '(RFC822)')
        if status == 'OK':
            raw_email = msg_data[0][1]
            msg = email.message_from_bytes(raw_email)
            emails.append((email_id.decode(), msg))
    
    return emails


def mark_as_read(mail: imaplib.IMAP4_SSL, email_id: str) -> None:
    """Mark an email as read."""
    mail.store(email_id, '+FLAGS', '\\Seen')


def delete_email(mail: imaplib.IMAP4_SSL, email_id: str) -> None:
    """Move email to Trash/Deleted folder."""
    # Most modern IMAP servers (Gmail, iCloud) support the \Deleted flag
    # which moves it to Trash or hides it until EXPUNGE
    mail.store(email_id, '+FLAGS', '\\Deleted')


def move_email(mail: imaplib.IMAP4_SSL, email_id: str, destination: str) -> None:
    """Move email to a different folder."""
    result = mail.copy(email_id, destination)
    if result[0] == 'OK':
        mail.store(email_id, '+FLAGS', '\\Deleted')


def url_already_ingested(url: str, data_dir: str = "data") -> bool:
    """
    Check if a URL has already been ingested by scanning markdown files.
    
    Args:
        url: URL to check
        data_dir: Root data directory containing category folders
    
    Returns:
        True if URL found in any existing markdown file, False otherwise
    """
    data_path = Path(data_dir)
    if not data_path.exists():
        return False
    
    # Normalize URL for comparison (remove trailing slashes, query params can vary)
    normalized_url = url.rstrip('/')
    
    # Search all markdown files in all category subdirectories
    for md_file in data_path.rglob("*.md"):
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
                # Look for URL in frontmatter
                if f'url: "{url}"' in content or f"url: '{url}'" in content:
                    return True
                # Also check normalized version
                if f'url: "{normalized_url}"' in content or f"url: '{normalized_url}'" in content:
                    return True
        except Exception as e:
            logger.warning(f"Error reading {md_file}: {e}")
            continue
    
    return False


def process_inbox(
    email_address: str,
    password: str,
    imap_server: Optional[str] = None,
    folder: str = "INBOX",
    data_dir: str = "data",
    allowed_senders: Optional[list[str]] = None,
    unread_only: bool = True,
    post_process_action: str = "read",  # "read", "delete", "archive"
    dry_run: bool = False
) -> int:
    """
    Main function to process inbox and ingest URLs.
    
    Args:
        email_address: Email to connect to
        password: App password for email
        imap_server: Optional IMAP server override
        folder: Email folder to check
        data_dir: Directory to store ingested articles
        allowed_senders: List of allowed sender emails (empty = allow all)
        unread_only: If True, only process UNSEEN emails.
        post_process_action: What to do after processing: 'read', 'delete', or 'archive'
        dry_run: If True, don't actually ingest
    
    Returns:
        Number of URLs successfully ingested
    """
    ingested_count = 0
    skipped_senders = 0
    allowed_senders = allowed_senders or []
    
    if allowed_senders:
        logger.info(f"Sender allowlist active: {allowed_senders}")
    else:
        logger.info("No sender allowlist configured - processing all emails")
    
    try:
        mail = connect_to_inbox(email_address, password, imap_server)
        
        # Determine search criteria
        if unread_only:
            emails = fetch_unread_emails(mail, folder)
        else:
            # Fetch ALL emails in folder from last 7 days
            mail.select(folder)
            since_date = (datetime.now() - timedelta(days=7)).strftime("%d-%b-%Y")
            status, messages = mail.search(None, f'(SINCE {since_date})')
            emails = []
            if status == 'OK':
                for email_id in messages[0].split():
                    status, msg_data = mail.fetch(email_id, '(RFC822)')
                    if status == 'OK':
                        emails.append((email_id.decode(), email.message_from_bytes(msg_data[0][1])))
        
        for email_id, msg in emails:
            subject = decode_email_subject(msg.get('Subject', ''))
            sender = msg.get('From', 'Unknown')
            
            # Check if sender is allowed
            if not is_sender_allowed(sender, allowed_senders):
                logger.warning(f"Skipping email from unauthorized sender: {sender}")
                skipped_senders += 1
                # Still apply post-process action so we don't keep seeing it
                if not dry_run:
                    if post_process_action == "delete":
                        delete_email(mail, email_id)
                    elif post_process_action == "archive":
                        move_email(mail, email_id, "Archive")
                    else:
                        mark_as_read(mail, email_id)
                continue
            
            logger.info(f"Processing email: '{subject}' from {sender}")
            
            # Extract URLs from subject and body
            body = get_email_body(msg)
            all_text = f"{subject}\n{body}"
            urls = extract_urls_from_text(all_text)
            
            if not urls:
                logger.info("No valid URLs found in email, skipping")
                if not dry_run:
                    mark_as_read(mail, email_id)
                continue
            
            logger.info(f"Found {len(urls)} URL(s): {urls}")
            
            # Process each URL
            for url in urls:
                try:
                    # Check if URL already ingested (to save LLM costs)
                    if url_already_ingested(url, data_dir):
                        logger.info(f"Skipping already ingested URL: {url}")
                        continue
                    
                    if dry_run:
                        logger.info(f"[DRY RUN] Would ingest: {url}")
                    else:
                        logger.info(f"Ingesting: {url}")
                        ingest_url(url, output_root=data_dir)
                        ingested_count += 1
                except Exception as e:
                    logger.error(f"Failed to ingest {url}: {e}")
            
            # Post-process email
            if not dry_run:
                if post_process_action == "delete":
                    delete_email(mail, email_id)
                    logger.info(f"Deleted email (moved to trash)")
                elif post_process_action == "archive":
                    # For Gmail, 'archive' is usually moving to '[Gmail]/All Mail' 
                    # but simple solution is to move to an 'Airlock-Archive' folder
                    move_email(mail, email_id, "Archive")
                    logger.info(f"Archived email")
                else:
                    mark_as_read(mail, email_id)
                    logger.info(f"Marked email as read")
        
        # Clean up deleted messages if any
        mail.expunge()
        mail.close()
        mail.logout()
        
    except Exception as e:
        logger.error(f"Failed to process inbox: {e}")
        raise
    
    logger.info(f"Total URLs ingested: {ingested_count}")
    return ingested_count


def main():
    parser = argparse.ArgumentParser(
        description="Poll email inbox for URLs to ingest into Content Airlock."
    )
    parser.add_argument(
        "--email",
        default=os.getenv("AIRLOCK_EMAIL"),
        help="Email address to poll (or set AIRLOCK_EMAIL env var)"
    )
    parser.add_argument(
        "--password",
        default=os.getenv("AIRLOCK_EMAIL_PASSWORD"),
        help="Email password/app password (or set AIRLOCK_EMAIL_PASSWORD env var)"
    )
    parser.add_argument(
        "--imap-server",
        default=os.getenv("AIRLOCK_IMAP_SERVER"),
        help="IMAP server (auto-detected if not specified)"
    )
    parser.add_argument(
        "--folder",
        default=os.getenv("AIRLOCK_EMAIL_FOLDER", "INBOX"),
        help="Email folder to check (default: INBOX)"
    )
    parser.add_argument(
        "--data-dir",
        default="data",
        help="Directory to store ingested articles"
    )
    parser.add_argument(
        "--allowed-senders",
        default=os.getenv("AIRLOCK_ALLOWED_SENDERS"),
        help="Comma-separated list of allowed sender emails (or set AIRLOCK_ALLOWED_SENDERS env var)"
    )
    parser.add_argument(
        "--unread-only",
        type=lambda x: (str(x).lower() == 'true'),
        default=(os.getenv("AIRLOCK_EMAIL_UNREAD_ONLY", "True").lower() == "true"),
        help="Only process unread emails (default: True)"
    )
    parser.add_argument(
        "--action",
        choices=["read", "delete", "archive"],
        default=os.getenv("AIRLOCK_EMAIL_ACTION", "read"),
        help="Action after processing: read, delete, or archive (default: read)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Don't actually ingest, just show what would be done"
    )
    
    args = parser.parse_args()
    
    if not args.email or not args.password:
        logger.error("Email and password are required!")
        logger.error("Set AIRLOCK_EMAIL and AIRLOCK_EMAIL_PASSWORD environment variables")
        logger.error("or pass --email and --password arguments")
        sys.exit(1)
    
    # Parse allowed senders
    allowed_senders = parse_allowed_senders(args.allowed_senders)
    
    process_inbox(
        email_address=args.email,
        password=args.password,
        imap_server=args.imap_server,
        folder=args.folder,
        data_dir=args.data_dir,
        allowed_senders=allowed_senders,
        unread_only=args.unread_only,
        post_process_action=args.action,
        dry_run=args.dry_run
    )


if __name__ == "__main__":
    main()
