import argparse
import csv
import json
import sys
from pathlib import Path

import anthropic
from pydantic import ValidationError

from schema import ReviewAnalysis

MODEL = "claude-opus-4-8"
TOOL_NAME = "record_review_analysis"

TOOL_DEF = {
    "name": TOOL_NAME,
    "description": (
        "Record the structured analysis of a customer review. "
        "Infer rating and sentiment independently from the review text — "
        "do not derive one from the other via a rule."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "rating": {
                "type": "integer",
                "minimum": 1,
                "maximum": 5,
                "description": "Star rating inferred from the review, 1 (worst) to 5 (best).",
            },
            "sentiment": {
                "type": "string",
                "enum": ["positive", "neutral", "negative"],
                "description": "Overall emotional tone of the review.",
            },
            "confidence": {
                "type": "number",
                "minimum": 0,
                "maximum": 1,
                "description": "Model confidence in the rating and sentiment, 0–1.",
            },
            "summary": {
                "type": "string",
                "description": "One-sentence summary of the review.",
            },
        },
        "required": ["rating", "sentiment", "confidence", "summary"],
    },
}

SYSTEM_PROMPT = (
    "You are a review analysis assistant. "
    "Analyze the review text and call the provided tool with your structured output. "
    "Evaluate the review in its original language — do not translate it. "
    "Rating and sentiment are independent judgments based on the text's tone and content."
)


def _extract_tool_input(response: anthropic.types.Message) -> dict:
    for block in response.content:
        if block.type == "tool_use" and block.name == TOOL_NAME:
            return block.input
    raise ValueError(
        f"Model did not call '{TOOL_NAME}'. Stop reason: {response.stop_reason}. "
        f"Content: {response.content}"
    )


def _call_api(
    client: anthropic.Anthropic, messages: list[dict]
) -> anthropic.types.Message:
    return client.messages.create(
        model=MODEL,
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        tools=[TOOL_DEF],
        tool_choice={"type": "tool", "name": TOOL_NAME},
        messages=messages,
    )


def analyze_review(text: str, client: anthropic.Anthropic | None = None) -> ReviewAnalysis:
    if client is None:
        client = anthropic.Anthropic()

    messages: list[dict] = [{"role": "user", "content": f"Analyze this review:\n\n{text}"}]

    response = _call_api(client, messages)
    tool_input = _extract_tool_input(response)

    try:
        return ReviewAnalysis(**tool_input)
    except ValidationError as first_error:
        # Retry once with the validation error appended
        messages.append({"role": "assistant", "content": response.content})
        messages.append(
            {
                "role": "user",
                "content": (
                    f"Your previous response failed schema validation:\n{first_error}\n\n"
                    "Please call the tool again with corrected values."
                ),
            }
        )
        retry_response = _call_api(client, messages)
        retry_input = _extract_tool_input(retry_response)
        return ReviewAnalysis(**retry_input)


def _read_reviews_file(path: Path) -> list[str]:
    suffix = path.suffix.lower()
    if suffix == ".json":
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, list):
            raise ValueError("JSON file must contain a list of review strings.")
        return [str(item) if not isinstance(item, str) else item for item in data]
    elif suffix == ".csv":
        reviews = []
        with path.open(newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            field = None
            for row in reader:
                if field is None:
                    # Prefer a column named 'review' or 'text', else use first column
                    field = next(
                        (k for k in row if k.lower() in ("review", "text")),
                        next(iter(row)),
                    )
                reviews.append(row[field])
        return reviews
    else:
        raise ValueError(f"Unsupported file type: {suffix!r}. Use .csv or .json.")


def _run_batch(input_path: Path, output_path: Path | None, client: anthropic.Anthropic) -> None:
    reviews = _read_reviews_file(input_path)
    results = []
    for i, review in enumerate(reviews, 1):
        print(f"Analyzing review {i}/{len(reviews)}...", file=sys.stderr)
        analysis = analyze_review(review, client)
        results.append({"review": review, "analysis": analysis.model_dump()})

    output = json.dumps(results, indent=2, ensure_ascii=False)
    if output_path:
        output_path.write_text(output, encoding="utf-8")
        print(f"Results written to {output_path}", file=sys.stderr)
    else:
        print(output)


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze customer reviews with Claude.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--text", help="Single review text to analyze.")
    group.add_argument("--file", type=Path, help="Path to a .csv or .json file of reviews.")
    parser.add_argument(
        "--output",
        type=Path,
        help="Output path for batch results (default: stdout). Only used with --file.",
    )
    args = parser.parse_args()

    client = anthropic.Anthropic()

    if args.text:
        result = analyze_review(args.text, client)
        print(result.model_dump_json(indent=2))
    else:
        _run_batch(args.file, args.output, client)


if __name__ == "__main__":
    main()
