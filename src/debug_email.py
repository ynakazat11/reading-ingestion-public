import imaplib
import email
import os
import sys
import logging
from email.header import decode_header
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def decode_email_subject(subject):
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

def debug_connection():
    email_address = os.getenv("AIRLOCK_EMAIL")
    password = os.getenv("AIRLOCK_EMAIL_PASSWORD")
    server = os.getenv("AIRLOCK_IMAP_SERVER") or "imap.gmail.com"
    
    if not email_address or not password:
        logger.error("Missing credentials")
        return

    logger.info("Connecting to IMAP server...")
    try:
        mail = imaplib.IMAP4_SSL(server)
        mail.login(email_address, password)
        logger.info("Login successful")
    except Exception as e:
        logger.error(f"Login failed: {e}")
        return

    # List all folders
    logger.info("Listing all folders:")
    status, folders = mail.list()
    if status == 'OK':
        for folder in folders:
            logger.info(folder.decode())
    
    # Check INBOX
    check_folder(mail, "INBOX")
    
    # Check the Airlock folder (where alias emails should arrive)
    check_folder(mail, "Airlock")

    # Check [Gmail]/All Mail if it exists (common for Gmail aliases)
    check_folder(mail, "[Gmail]/All Mail")

    mail.logout()

def check_folder(mail, folder_name):
    logger.info(f"\nChecking folder: {folder_name}")
    try:
        status, _ = mail.select(folder_name, readonly=True)
        if status != 'OK':
            logger.warning(f"Could not select {folder_name}")
            return

        # Check Recent Unread (last 2 days)
        since_date = (datetime.now() - timedelta(days=2)).strftime("%d-%b-%Y")
        
        # 1. Check UNSEEN
        logger.info(f"Searching for UNSEEN emails since {since_date}...")
        status, messages = mail.search(None, f'(UNSEEN SINCE {since_date})')
        if status == 'OK':
            email_ids = messages[0].split()
            logger.info(f"Found {len(email_ids)} unread emails.")
            for eid in email_ids[-5:]: # Show last 5
                fetch_and_print_header(mail, eid)
        
        # 2. Check RECENT (sometimes unread but not UNSEEN flag? uncommon but possible)
        # Actually, let's just check ALL from today to see if they arrived but marked read
        today = datetime.now().strftime("%d-%b-%Y")
        logger.info(f"Searching for ALL emails since {today} (to see if they are arriving)...")
        status, messages = mail.search(None, f'(SINCE {today})')
        if status == 'OK':
            email_ids = messages[0].split()
            logger.info(f"Found {len(email_ids)} total emails since today.")
            for eid in email_ids[-5:]:
                fetch_and_print_header(mail, eid)

    except Exception as e:
        logger.error(f"Error checking folder {folder_name}: {e}")

def fetch_and_print_header(mail, email_id):
    try:
        status, msg_data = mail.fetch(email_id, '(RFC822.HEADER)')
        if status == 'OK':
            raw_email = msg_data[0][1]
            msg = email.message_from_bytes(raw_email)
            subject = decode_email_subject(msg.get('Subject', 'No Subject'))
            sender = msg.get('From', 'Unknown Sender')
            to = msg.get('To', 'Unknown Recipient')
            logger.info(f"  [ID {email_id.decode()}] From: {sender} | To: {to} | Subject: {subject}")
    except Exception as e:
        logger.error(f"  Error fetching header for {email_id}: {e}")

if __name__ == "__main__":
    debug_connection()
