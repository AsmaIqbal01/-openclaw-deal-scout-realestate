# SKILL.md — rightmove-parser

## Trigger
Use this skill when market_mode = "UK" and the email sender domain matches:
- `@rightmove.co.uk`, `@emails.rightmove.co.uk`
- `@zoopla.co.uk`, `@alerts.zoopla.co.uk`
- `@onthemarket.com`
OR when subject line contains: "New enquiry", "Viewing request", "Property enquiry", "You have a new lead"

## What This Skill Does
Parses Rightmove, Zoopla, and OnTheMarket lead notification emails into the Intake Sub-Agent's lead JSON schema.

## Parsing Rules

### Rightmove Lead Email Structure
Rightmove sends structured lead emails when a buyer enquires about a listing.
Extract:
- Buyer name → `contact.name`
- Buyer email → `contact.email`
- Buyer phone → `contact.phone` (if provided — not always present)
- Property address → `property.location`
- Property type → `property.type` (Flat, House, Bungalow → residential; Land → plot; Commercial → commercial)
- Asking price → `property.budget_gbp` (strip "£", commas — return integer)
- Bedrooms → `property.size` (e.g. "3 bed")
- Enquiry message → store in `property.enquiry_text` (extra field — append if present)
- Rightmove listing ID → `raw_source_id` (use as deduplication key)

### Zoopla Lead Email Structure
Same extraction logic. Zoopla emails include:
- Buyer's preferred viewing time → store in `property.preferred_viewing` (extra field)
- Whether buyer is in a chain → `property.in_chain: true/false` (extra field)

### OnTheMarket
Same extraction logic as Rightmove.

### Field Mapping Failures
If a field cannot be extracted:
- Set field to `null` — never guess
- Log: `parse_warning: "field_name could not be extracted"`

## Source Value
- `"rightmove"` for Rightmove emails
- `"zoopla"` for Zoopla emails
- `"onthemarket"` for OnTheMarket emails

## Urgency Signals
Set `urgency = "high"` if enquiry message contains: "urgent", "ASAP", "cash buyer", "no chain", "ready to proceed", "first time buyer mortgage agreed"
Set `urgency = "medium"` if viewing is requested
Set `urgency = "low"` for general interest messages

## Output
Return partial lead JSON (contact + property + urgency blocks).
Intake Sub-Agent merges with its own fields.

## Error Handling
- Email is a Rightmove/Zoopla marketing email (not a lead): return `parse_error: "marketing_email"` — check for absence of buyer contact fields
- Phone number is non-UK format: store as-is, set `parse_warning: "non_uk_phone"`
- Price in non-GBP currency: set `parse_warning: "non_gbp_currency"`, set budget_gbp to null
