# Review Analyzer

## What this is
A tool that takes a customer/product review (raw text) and returns **structured output**:
- `rating`: integer 1–5 (inferred from the review text)
- `sentiment`: one of `positive`, `neutral`, `negative`
- `confidence`: float 0–1 (how confident the model is in the above)
- `summary`: one-sentence summary of the review

Input: a single review string, or a batch (CSV/JSON list of reviews).
Output: validated JSON matching the schema below — never free-form prose.

## Stack
- Python 3.11+
- Anthropic SDK (`anthropic` package) for the LLM call
- `pydantic` for schema validation of the structured output
- `pytest` for tests

> Adjust this section if the actual stack differs (e.g. Node/TypeScript) — Claude should not assume.

## Output schema (source of truth)
Define this once in `schema.py` and import it everywhere. Do not redefine the shape inline in prompts or other files.

```python
from pydantic import BaseModel, Field
from typing import Literal

class ReviewAnalysis(BaseModel):
    rating: int = Field(ge=1, le=5)
    sentiment: Literal["positive", "neutral", "negative"]
    confidence: float = Field(ge=0, le=1)
    summary: str
```

## How structured output is produced
- Use Claude's tool-use (function-calling) feature with a tool whose `input_schema` mirrors `ReviewAnalysis`, OR use the `response_format`/JSON-mode equivalent if available in the SDK version in use. Tool-use is preferred — it is more reliable than asking the model to "return JSON" in plain prompt text.
- Always validate the model's output against the `ReviewAnalysis` pydantic model before returning it to the caller. If validation fails, retry once with the validation error appended to the prompt; if it fails twice, raise a clear error rather than returning malformed data.
- Never post-process or "fix up" model output with regex. If the schema doesn't validate, that's a prompt/schema problem to fix, not a string-patching problem.

## Commands
```bash
pip install -r requirements.txt 
# pip install -r requirements.txt --break-system-packages   # only if working in the sandboxed environment
python -m pytest                                            # run tests
python analyze.py --text "great product, fast shipping"     # single review
python analyze.py --file reviews.csv --output results.json  # batch
```

> Replace with real commands once the project's actual entrypoints exist.

## Conventions
- One review in, one `ReviewAnalysis` out. Don't bundle batch-averaging or aggregate stats into the same function that does per-review analysis — keep those as a separate step.
- Sentiment and rating are independent fields: don't derive `sentiment` from `rating` with a hardcoded rule (e.g. "4–5 = positive") inside the code. Both come from the model's judgment of the text, since a 3-star review can read as either mildly positive or mildly negative depending on tone.
- Non-English reviews (e.g. Bangla) should be analyzed in their original language — don't translate before analysis unless explicitly asked, since translation can shift tone and lose sentiment cues.
- Log the raw model response alongside the parsed result during development; strip this in production paths.

## Testing
- Unit tests live in `tests/`. Every new prompt change should be checked against a small fixed set of example reviews with known expected ratings/sentiment (`tests/fixtures/reviews.json`) to catch regressions.
- Don't mark a test "passing" by loosening the schema (e.g. making `rating` a string to dodge a validation error) — fix the prompt or parsing instead.

## What NOT to do
- Don't have the model return prose with the rating/sentiment embedded in a sentence ("I'd say this is a 4-star, mostly positive review because...") — that's not structured output, and parsing it back out defeats the purpose.
- Don't silently default to `rating: 3, sentiment: "neutral"` on errors — surface the failure.