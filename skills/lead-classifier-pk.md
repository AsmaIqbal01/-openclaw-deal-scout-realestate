# SKILL.md — lead-classifier-pk

## Trigger
Use this skill when market_mode = "PK" and the Intake Sub-Agent needs to call Gemini 2.5 Flash
to classify a candidate lead extracted by zameen-parser or pk-whatsapp-lead.

## What This Skill Does
Provides the exact Gemini 2.5 Flash prompt for PK real estate lead classification.
Returns a classification score 0.0–1.0 and urgency level.

## Gemini Prompt Template

```
You are a Pakistani real estate lead qualification specialist.
You understand Roman Urdu, English, and mixed-language property messages.

Evaluate the following property lead and return ONLY valid JSON — no explanation, no markdown.

Lead data:
SOURCE: {source}
CONTACT NAME: {contact.name}
CONTACT PHONE: {contact.phone}
CONTACT WHATSAPP: {contact.whatsapp}
PROPERTY TYPE: {property.type}
LOCATION: {property.location}
BUDGET PKR: {property.budget_pkr}
SIZE: {property.size}
URGENCY SIGNALS DETECTED: {urgency}

Scoring criteria:
- 0.9–1.0: Serious buyer/seller — contact info complete, clear property intent, budget mentioned, urgent signals present
- 0.7–0.89: Likely serious — contact info present, clear property intent, budget absent or vague
- 0.5–0.69: Possible lead — partial contact info OR ambiguous intent
- 0.3–0.49: Weak signal — very little contact info, unclear intent
- 0.0–0.29: Not a lead — spam, irrelevant, no property intent

Return this exact JSON structure:
{
  "classification_score": float,
  "urgency": "high|medium|low",
  "lead_quality_reason": "one sentence in English explaining the score",
  "recommended_action": "call_now|whatsapp_followup|email_followup|archive"
}
```

## Gemini Call Parameters
- Model: `gemini-2.5-flash`
- Temperature: 0.1 (low — we want consistent scoring, not creative)
- Max output tokens: 150
- Response mime type: `application/json`

## Post-Call Processing
1. Parse Gemini JSON response
2. Extract `classification_score` → set on lead JSON
3. Extract `urgency` → override lead JSON urgency if Gemini confidence is higher
4. Log `lead_quality_reason` to MEMORY.md for audit trail
5. Increment `gemini_today_count` in MEMORY.md by 1

## Error Handling
- Gemini returns non-JSON: retry once with same prompt, if fails set `classification_score: 0`, `rejection_reason: "gemini_parse_error"`
- Gemini quota error (429): set `classification_score: 0`, `rejection_reason: "gemini_quota"`, halt pipeline, notify owner
- Gemini timeout (>10s): set `classification_score: 0`, `rejection_reason: "gemini_timeout"`, skip lead, continue pipeline
