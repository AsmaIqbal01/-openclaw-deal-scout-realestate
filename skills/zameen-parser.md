# SKILL.md — zameen-parser

## Trigger
Use this skill when market_mode = "PK" and the email sender domain matches:
- `@zameen.com`, `@alerts.zameen.com`, `@olx.com.pk`, `@alerts.olx.com.pk`
OR when subject line contains: "New listing", "Property Alert", "New property", "نئی جائیداد"

## What This Skill Does
Parses Zameen.com and OLX Pakistan property alert emails into the Intake Sub-Agent's lead JSON schema.

## Parsing Rules

### Zameen Alert Email Structure
Extract these fields from the email body:
- Property title → `property.type` (map: Flat→residential, Plot→plot, House→residential, Shop→commercial)
- Location string → `property.location` (take as-is, do not normalise)
- Price → `property.budget_pkr` (strip "PKR", "Rs.", commas — return integer)
- Area → `property.size` (e.g. "5 Marla", "1 Kanal")
- Agent/seller name → `contact.name` (if present in email body)
- Agent phone → `contact.phone` (Pakistani format: +92XXXXXXXXXX or 03XXXXXXXXX)
- Listing URL → store in `property.listing_url` (extra field, not in base schema — append if present)

### OLX Alert Email Structure
Same extraction logic. OLX emails also include seller WhatsApp number in some alerts:
- WhatsApp number → `contact.whatsapp`

### Field Mapping Failures
If a field cannot be extracted:
- Set field to `null` — never guess or infer
- Log: `parse_warning: "field_name could not be extracted from source"`

## Source Value
Set `source` field to:
- `"zameen_alert"` for Zameen emails
- `"olx_alert"` for OLX emails

## Output
Return partial lead JSON (contact + property blocks only).
Intake Sub-Agent merges this with its own fields (lead_id, tenant_id, score, etc.).

## Error Handling
- Email body empty or unreadable: return `parse_error: "empty_body"`, do not produce output
- Price in USD/GBP detected: flag `parse_warning: "foreign_currency"`, set budget_pkr to null
- Duplicate listing_url already in processed_ids: return `parse_error: "duplicate_listing"` immediately
