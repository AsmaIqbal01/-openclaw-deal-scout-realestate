# SKILL.md — lead-classifier-uk

## Trigger
Use this skill when market_mode = "UK" and the Intake Sub-Agent needs to call Gemini 2.5 Flash
to classify a candidate lead extracted by rightmove-parser.

## What This Skill Does
Provides the exact Gemini 2.5 Flash prompt for UK estate agent lead classification.
Returns a classification score 0.0–1.0 and urgency level.

## Gemini Prompt Template

```
You are a UK estate agent lead qualification specialist.
You understand UK property market terminology, buyer/seller intent signals, and chain dynamics.

Evaluate the following property lead and return ONLY valid JSON — no explanation, no markdown.

Lead data:
SOURCE: {source}
CONTACT NAME: {contact.name}
CONTACT EMAIL: {contact.email}
CONTACT PHONE: {contact.phone}
PROPERTY TYPE: {property.type}
LOCATION: {property.location}
ASKING PRICE GBP: {property.budget_gbp}
BEDROOMS: {property.size}
IN CHAIN: {property.in_chain}
ENQUIRY TEXT: {property.enquiry_text}
PREFERRED VIEWING: {property.preferred_viewing}
URGENCY SIGNALS DETECTED: {urgency}

Scoring criteria:
- 0.9–1.0: Hot lead — contact info complete, viewing requested or offer implied, no chain or chain-free confirmed, mortgage agreed or cash buyer
- 0.7–0.89: Warm lead — contact info complete, clear buying/selling intent, no urgency signals
- 0.5–0.69: Cool lead — partial contact info OR vague intent OR in a long chain
- 0.3–0.49: Weak lead — enquiry only, no phone, speculative interest
- 0.0–0.29: Not a lead — auto-generated, spam, or internal Rightmove/Zoopla notification

Return this exact JSON structure:
{
  "classification_score": float,
  "urgency": "high|medium|low",
  "lead_quality_reason": "one sentence explaining the score",
  "recommended_action": "call_now|email_followup|schedule_viewing|archive",
  "chain_risk": "none|low|medium|high"
}
```

## Gemini Call Parameters
- Model: `gemini-2.5-flash`
- Temperature: 0.1
- Max output tokens: 200
- Response mime type: `application/json`

## Post-Call Processing
1. Parse Gemini JSON response
2. Extract `classification_score` → set on lead JSON
3. Extract `urgency` → override lead JSON urgency
4. Extract `chain_risk` → append to lead JSON as extra field
5. Log `lead_quality_reason` to MEMORY.md
6. Increment `gemini_today_count` in MEMORY.md by 1

## Error Handling
- Same as lead-classifier-pk.md error handling
- Additional: if `chain_risk = "high"` and score < 0.7, override urgency to "low" — high chain risk deprioritises the lead
