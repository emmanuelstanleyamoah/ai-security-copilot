# T1566 Phishing

Tactic: Initial Access.

Phishing is an adversary sending a message that asks a person to open a file, click a link, or give up a session. In a mailbox alert, the useful fields are sender domain, reply-to mismatch, attachment hash, and whether a mailbox rule was created afterward.

Analyst check: confirm the message is still in the mailbox, then look for the same hash or sender across the tenant before resetting credentials.
