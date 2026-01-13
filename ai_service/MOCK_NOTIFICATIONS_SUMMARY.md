# Mock Notifications Implementation Summary

## What Was Implemented

A system to capture and display notifications in readable markdown files when running in mock mode, instead of sending them to the remote server.

## Changes Made

### 1. Enhanced Notification Service
**File**: `app/services/enhanced_notification_service.py`

**Added**:
- Mock mode check in `_send_notification()` (line ~306)
- `_extract_notification_summary()` method - Extracts key fields from each notification type
- `_write_mock_notification()` method - Writes formatted markdown to file

**Behavior**:
- When `MOCK_ENABLED=true`, HTTP sending is skipped
- Notifications are written to `./mock_notifications/{call_id}.md`
- Full transcript and translation text included (not truncated)
- One file per call with all notifications

### 2. Configuration Setting
**File**: `app/config/settings.py`

**Added**:
- `mock_notifications_folder` setting (default: `./mock_notifications`)

### 3. Environment Files
**Files**: `.env` and `.env.example`

**Added**:
```env
MOCK_NOTIFICATIONS_FOLDER=./mock_notifications
```

### 4. Documentation
**Files Created**:
- `mock_notifications/README.md` - How to use mock notifications
- `MOCK_NOTIFICATIONS_SUMMARY.md` - This summary

**Files Updated**:
- `MOCK_TESTING_GUIDE.md` - Added section on viewing mock notifications

---

## How It Works

### 1. Enable Mock Mode

Your `.env` already has:
```env
MOCK_ENABLED=true
MOCK_NOTIFICATIONS_FOLDER=./mock_notifications
```

### 2. Run a Test

```bash
python scripts/mock_asterisk.py --audio-folder ./test_audio --count 1
```

### 3. Check the Logs

You'll see in the Celery worker:
```
[mock] Skipping HTTP send - writing to mock notification file
[mock] Wrote postcall_transcription to mock_notifications/1768210616.0.md
[mock] Wrote postcall_translation to mock_notifications/1768210616.0.md
[mock] Wrote postcall_classification to mock_notifications/1768210616.0.md
...
```

### 4. View the Notification File

```bash
cat mock_notifications/1768210616.0.md
```

Or open in any markdown editor:
```bash
code mock_notifications/1768210616.0.md
```

---

## What's in the Markdown File

Each markdown file contains:

### Header
- Call ID
- Processing mode
- Start timestamp

### Notifications

**1. POSTCALL_TRANSCRIPTION**
- Full transcript text (complete, not truncated)
- Character count

**2. POSTCALL_TRANSLATION**
- Full translation text (complete, not truncated)
- Character count

**3. POSTCALL_CLASSIFICATION**
- Main category
- Sub-category
- Intervention type
- Priority level
- Confidence percentage

**4. POSTCALL_ENTITIES**
- Entity counts (persons, locations, organizations, dates)
- Complete list of extracted entities

**5. POSTCALL_QA_SCORING**
- Total metrics evaluated
- Pass rate percentage
- Overall quality assessment

**6. POSTCALL_SUMMARY**
- Generated summary text

**7. POSTCALL_COMPLETE**
- Final status
- Total processing time

---

## Example Output

```markdown
# Call Notifications: 1768212491.0

**Processing Mode**: post_call
**Started**: 2026-01-12T13:12:15Z

---

## POSTCALL_TRANSCRIPTION

**Time**: 2026-01-12T13:12:15Z
**Type**: postcall_transcription
**Length**: 616 characters

**Full Transcript**:
\```
na zungunja na batari na zengunja nanani na zangunja katitama inu na na naktige su mu kutukawasi na pia kutuga kaioli na irobi kukoka ya legahni central na dama south central...
\```

---

## POSTCALL_TRANSLATION

**Time**: 2026-01-12T13:12:15Z
**Type**: postcall_translation
**Length**: 402 characters

**Full Translation**:
\```
and surrounds with some of the fighting groups and groups that joined us and I'm truly proud of you for taking care of us both physically and emotionally...
\```

---

## POSTCALL_CLASSIFICATION

**Time**: 2026-01-12T13:12:15Z
**Type**: postcall_classification
**Category**: Advice and Counselling → Homelessness
**Sub-Category 2**: No Care Giver
**Intervention**: Counselling
**Priority**: 3
**Confidence**: 57.4%

---

...
```

---

## Benefits

1. **No external server needed** - Test without running the notification endpoint
2. **Human-readable format** - Easy to review all notifications for a call
3. **Complete content** - Full transcripts and translations (not truncated)
4. **Fast** - No network delays or HTTP retries
5. **Debugging** - See exactly what notifications were generated
6. **One file per call** - Each call's notifications organized together

---

## Comparing Mock vs Production

| Aspect | Mock Mode | Production Mode |
|--------|-----------|-----------------|
| HTTP Requests | ❌ Skipped | ✅ Sent to server |
| Output | Markdown files | HTTP POST |
| Location | `./mock_notifications/` | Remote server |
| Speed | Fast (no network) | Network latency |
| Format | Human-readable markdown | JSON payload |
| Dependencies | None | Requires server running |

---

## Troubleshooting

### No markdown file created

**Check**:
1. Is `MOCK_ENABLED=true` in `.env`?
2. Did you restart the server after changing `.env`?
3. Check Celery worker logs for errors

### Empty markdown file

**Likely cause**: Notifications not sent due to processing mode

**Solution**: Ensure `ENABLE_POSTCALL_PROCESSING=true` for post-call notifications

### File not updating

**Cause**: File is created on first notification for new call_id

**Solution**:
- Delete existing file: `rm mock_notifications/1768210616.0.md`
- Run test again with different call_id

---

## Notes

- Mock mode works for both **real-time** and **post-call** notifications
- Files are created/appended automatically
- Folder is created automatically if it doesn't exist
- Each call_id gets its own file
- Re-running same call_id overwrites the file
- The system still logs to `agent_payloads.jsonl` if that's enabled

---

## Verification

To verify it's working:

1. **Check server logs** during startup:
   ```
   [config] Mock mode enabled
   [config] Mock notifications folder: ./mock_notifications
   ```

2. **Check Celery logs** during processing:
   ```
   [mock] Skipping HTTP send - writing to mock notification file
   [mock] Wrote postcall_transcription to mock_notifications/1768212491.0.md
   ```

3. **Check the folder**:
   ```bash
   ls -lh mock_notifications/
   # Should show .md files named by call_id
   ```

4. **View a file**:
   ```bash
   cat mock_notifications/{call_id}.md
   # Should show formatted markdown with all notifications
   ```
