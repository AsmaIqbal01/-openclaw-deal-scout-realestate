# SKILL.md — pk-whatsapp-lead

## Trigger
Use this skill when market_mode = "PK" and the input is a WhatsApp message (not an email).
WhatsApp messages arrive via OpenClaw's WhatsApp channel.

## What This Skill Does
Extracts property lead data from forwarded WhatsApp messages common in Pakistani real estate.
Pakistani agents receive property enquiries and listings as forwarded WhatsApp texts — often in Roman Urdu, mixed English/Urdu, or structured text from property portals.

## Common WhatsApp Message Patterns

### Pattern A — Forwarded listing
```
*DHA Phase 6 — 10 Marla House For Sale*
Price: 4.5 Crore (Negotiable)
Contact: Ali Raza — 0300-1234567
3 bed, 3 bath, double unit
```

### Pattern B — Buyer enquiry
```
Bhai mujhe gulshan iqbal mein 2 bed flat chahiye
budget 80-90 lac hai
WhatsApp karen: 0321-9876543
```

### Pattern C — Agent forward (no clear structure)
```
Ek client hai jise 5 marla plot chahiye Bahria Town mein
cash buyer hai, jaldi chahiye
number: 03001112233
```

## Extraction Rules

### Contact
- Phone: extract any Pakistani number format (03XX-XXXXXXX, +923XXXXXXXXX, 03XXXXXXXXX)
- Name: extract if explicitly mentioned — set null if not
- WhatsApp: same as phone if message is via WhatsApp (caller is sender)

### Property
- Type: map keywords → residential (ghar, flat, house, makan), plot (plot, land, zameen), commercial (dukaan, shop, office)
- Location: extract area name (DHA, Bahria, Gulshan, Nazimabad, etc.) — take as-is
- Budget: extract number + unit (lac, crore) → convert to PKR integer (1 lac = 100,000; 1 crore = 10,000,000)
- Size: extract if present (marla, kanal, square feet)

### Urgency Signals
Set `urgency = "high"` if message contains: "jaldi", "urgent", "cash buyer", "ready", "immediately", "abhi"
Set `urgency = "medium"` if budget is mentioned
Set `urgency = "low"` otherwise

## Language Handling
- Roman Urdu and English mixed: handle both
- Pure Urdu (Nastaliq script): attempt extraction, set `parse_warning: "urdu_script"` if extraction confidence is low
- Never translate message content — extract structured data only

## Output
Return partial lead JSON (contact + property + urgency blocks).
Set `source = "whatsapp_forward"`.

## Error Handling
- Message is a voice note transcription: process as text if transcription is present, else return `parse_error: "voice_note_no_transcription"`
- Message is an image/sticker only: return `parse_error: "non_text_message"`
- No property intent detectable: return `parse_error: "no_property_intent"` — do not produce lead output
