# Phishing mailbox runbook

1. Quarantine the message.
2. Block the sender domain if the domain is not a known partner.
3. Search for the attachment hash.
4. Reset the session only after the mailbox rule list is reviewed.
5. Record the technique as T1566 when the message asked the user to open a file or link.
