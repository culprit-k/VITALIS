# Git-history privacy and artifact audit

**Status:** automated reachable-history scan passed on current PR head; human triage and independent privacy/security review remain pending.

## What it scans

Run from a complete clone after fetching every branch and tag that is in scope:

    python scripts/audit_git_history.py --json-output /tmp/vitalis-history-audit.json

The scanner inspects commits and blobs reachable from local refs for:
- historical paths ending in common patient-data or model-artifact extensions;
- historical blobs larger than 5 MiB by default;
- high-confidence patterns for private-key blocks and common AWS, GitHub, Slack, and Google API credentials.

The report lists rule names, paths, blob hashes, and counts only. It never prints matched credential text. The command exits non-zero when findings exist, so each finding requires review before the audit can be considered clear. Keep the JSON report outside the repository because file paths and object hashes are internal audit metadata.

## Important limitations

- A clone must not be shallow. The script fails closed when it detects a shallow clone.
- Only refs present in the clone are in scope. Fetch all relevant branches and tags before treating the result as comprehensive.
- Credential regexes are heuristic and can produce false positives; review them without copying any credential value into issues, logs, or chat.
- A clean scan is not proof that no sensitive material was ever exposed. Use GitHub's available secret-scanning/security features and independent review where possible.
- If an actual credential is found, revoke/rotate it immediately. If patient data or regulated data is found, follow the applicable incident-response and governance process. Do not rewrite public history until the repository owner has assessed downstream clones, forks, and disclosure implications.
- The current-tree guard, this history scanner, and independent privacy/security review cover different risks; none replaces the others.

VITALIS remains research-only. This audit does not establish clinical validity or authorize patient-data collection.


## CI checkpoint — 16 October 2026

The current-head standard workflow [#38875089161](https://github.com/culprit-k/VITALIS/actions/runs/38875089161) completed the `Audit reachable Git history for data artifacts and high-confidence secrets` step successfully on commit `f46bfa7ecf56631a3b4ff8b1e8c97e95abdcb6a3`. Its retained log reports 780 commits, 760 unique blobs, and `findings_count: 0`. This is a positive automated scan result, not proof that no sensitive material was ever exposed. The scan covers commits/blobs reachable from refs fetched into that CI checkout and uses heuristic patterns; a human should review scope and findings/limitations, and any available GitHub secret-scanning results separately. Do not claim independent security review has occurred.
