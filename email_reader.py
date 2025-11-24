def read_emails():
    try:
        # Fetch credentials from Render environment
        imap_user = os.getenv("IMAP_USER")
        imap_pass = os.getenv("IMAP_PASS")

        if not imap_user or not imap_pass:
            return {"error": "IMAP credentials missing", "emails": []}

        imap_server = "imap.gmail.com"
        mail = imaplib.IMAP4_SSL(imap_server)
        mail.login(imap_user, imap_pass)
        mail.select("inbox")

        status, messages = mail.search(None, "ALL")
        email_list = []

        for msg_id in messages[0].split():
            status, msg_data = mail.fetch(msg_id, "(RFC822)")
            raw_email = msg_data[0][1]
            msg = email.message_from_bytes(raw_email)

            subject = decode_header(msg["Subject"])[0][0]
            if isinstance(subject, bytes):
                subject = subject.decode()

            from_ = msg.get("From")
            date_ = msg.get("Date")

            email_list.append({
                "date": date_,
                "from": from_,
                "subject": subject
            })

        return {"emails": email_list, "status": "success"}

    except Exception as e:
        return {"error": str(e), "status": "failed"}
