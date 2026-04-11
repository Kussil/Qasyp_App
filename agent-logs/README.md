# Agent Logs

Audit trail for all AI Agent outreach activity (Epic E5).

## Purpose
Per CLAUDE.md: all agent-sent messages must be logged and auditable per user account.
No message may be sent without a corresponding log entry and explicit user approval.

## Log Entry Format
Each outreach draft creates a JSON log entry:

```json
{
  "log_id": "uuid",
  "timestamp": "ISO8601",
  "sender_bin": "123456789012",
  "recipient_bin": "987654321098",
  "language": "ru | kk | en",
  "goal": "description of outreach intent",
  "message_word_count": 180,
  "status": "DRAFT | APPROVED | SENT | REJECTED",
  "approved_by_user": false,
  "sent_at": null,
  "channel": "email | whatsapp | in-app | null"
}
```

## Status Flow
```
DRAFT → (user reviews) → APPROVED → SENT
                       → REJECTED
```

## Important
- `approved_by_user` must be `true` before any message is dispatched
- No agent may take irreversible send actions without human-in-the-loop approval (mandatory in staging)
- Log files are append-only — never delete or modify existing entries
