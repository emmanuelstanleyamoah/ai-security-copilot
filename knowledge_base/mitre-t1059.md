# T1059 Command and Scripting Interpreter

Tactic: Execution.

Command and scripting interpreters cover shells and runtime hosts such as PowerShell and cmd.exe. Encoded PowerShell is a common alert because the command line is hidden from a casual reader.

Analyst check: recover the parent process, the decoded command line, and the host isolation state. Do not treat the encoded blob as trusted content.
