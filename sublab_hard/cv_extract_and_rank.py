import json
import os
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

CANDIDATES_DIR = DATA / "candidates"
RUBRIC_FILE = DATA / "candidate_rubric.json"

MODEL = "gpt-5.6-luna"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_story(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def openai_client() -> OpenAI:
    key = os.getenv("OPENAI_API_KEY")

    if not key:
        raise RuntimeError("OPENAI_API_KEY is not set")

    return OpenAI(api_key=key)


def ask_llm(prompt: str) -> str:
    client = openai_client()

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ]
    )

    return response.choices[0].message.content or ""


def parse_json(text: str) -> dict:
    decoder = json.JSONDecoder()

    for i, char in enumerate(text):
        if char != "{":
            continue

        try:
            obj, _ = decoder.raw_decode(text[i:])
        except json.JSONDecodeError:
            continue

        if isinstance(obj, dict):
            return obj

    raise ValueError(
        f"Could not parse JSON: {text!r}"
    )


def build_prompt(candidate_id: str, story: str) -> str:
    return f"""
    You're extracting a structured CV from a scholarship candidate story.
    
    Candidate ID: {candidate_id}
    
    Story: {story}
    
    Rules: 
    
    - Never invent facts
    - If a fact isn't stated, return null
    - If GPA uses another scale, convert it to 4.0 scale,
    but preserve the original GPA and original scale
    - Count a peer-reviewed output as published only if the story says
    it's published or accepted
    - Don't count submitted, inder review, in preparation or in press as published
    - If the story contains contradictory value for a fields,
    don't choose one and don't average them
    Return null for that field and record the contradiction 
    - Give an evidence quote for every non-null extracted field
    - Return JSON only
    
    You must use only thus JSON structure:
    
    {{
        "candidate_id": "{candidate_id}",
        "full_name": null,
        "degree": null,
        "graduation_year": null,
        
        "gpa_original": null,
        "gpa_original_scale": null,
        "gpa_4_scale": null,
        
        "languages": [],
        "published_peer_reviewed_outputs": null,
        "other_research_outputs": [],
        "relevant_experience_months": null,
        "contradictions": [],
        
        "evidence": {{
            "full_name": null,
            "degree": null,
            "graduation_year": null,
            "gpa": null,
            "language": [],
            "published_peer_reviewed_output": [],
            "relevant_experience_months": []
        }}
    }}
    """.strip()


def validate_extraction(data: dict) -> bool:
    required = {
        "candidate_id",
        "full_name",
        "degree",
        "graduation_year",
        "gpa_original",
        "gpa_original_scale",
        "gpa_4_scale",
        "languages",
        "published_peer_reviewed_outputs",
        "other_research_outputs",
        "relevant_experience_months",
        "contradictions",
        "evidence",
    }

    if not isinstance(data, dict):
        return False

    if set(data.keys()) != required:
        print(
            "Extraction keys mismatch.\n"
            "Missing:",
            required - set(data.keys()),
            "\nExtra:",
            set(data.keys()) - required
        )
        return False

    if not isinstance(data["candidate_id"], str):
        return False

    if (
        data["full_name"] is not None
        and not isinstance(data["full_name"], str)
    ):
        return False

    if (
        data["degree"] is not None
        and not isinstance(data["degree"], str)
    ):
        return False

    if (
        data["graduation_year"] is not None
        and not isinstance(data["graduation_year"], int)
    ):
        return False

    if (
        data["gpa_4_scale"] is not None
        and not isinstance(
            data["gpa_4_scale"],
            (int, float)
        )
    ):
        return False

    if not isinstance(data["languages"], list):
        return False

    if (
        data["published_peer_reviewed_outputs"] is not None
        and not isinstance(
            data["published_peer_reviewed_outputs"],
            int
        )
    ):
        return False

    if not isinstance(
        data["other_research_outputs"],
        list
    ):
        return False

    if (
        data["relevant_experience_months"] is not None
        and not isinstance(
            data["relevant_experience_months"],
            (int, float)
        )
    ):
        return False

    if not isinstance(
        data["contradictions"],
        list
    ):
        return False

    if not isinstance(
        data["evidence"],
        dict
    ):
        return False

    return True


def extract_candidate(path: Path) -> dict:
    candidate_id = path.stem
    story = load_story(path)

    prompt = build_prompt(candidate_id, story)

    raw = ask_llm(prompt)

    try:
        parsed = parse_json(raw)
        parsed_ok = True
        valid = validate_extraction(parsed)

    except ValueError:
        parsed = None
        parsed_ok = False
        valid = False

    return {
        "candidate_id": candidate_id,
        "parsed_ok": parsed_ok,
        "valid": valid,
        "data": parsed,
        "raw": raw,
    }


def extract_all():
    results = []

    files = sorted(
        CANDIDATES_DIR.glob("story-*.md")
    )

    for path in files:
        print(f"\nExtracting {path.name}...")

        result = extract_candidate(path)

        results.append(result)

        print(
            f"{result['candidate_id']}: "
            f"parsed={result['parsed_ok']} "
            f"valid={result['valid']}"
        )

    return results


def null_fields(candidate: dict) -> list[str]:
    ignored = {
        "candidate_id",
        "evidence",
        "contradictions",
    }

    return [
        key
        for key, value in candidate.items()
        if key not in ignored and value is None
    ]


def print_extraction(result):
    print("\n----- EXTRACTION SUMMARY -----")

    for result in result:
        print(f"\n{result['candidate_id']}")
        print("Parsed:", result["parsed_ok"])
        print("Valid:", result["valid"])

        if result["data"] is None:
            continue

        print(
            "null fields:",
            null_fields(result["data"]),
        )

        print(
            "Contradictions:",
            result["data"]["contradictions"],
        )


def build_scoring_prompt(candidate: dict, rubric: dict) -> str:
    candidate_text = json.dumps(candidate, ensure_ascii=False, indent=2)

    rubric_text = json.dumps(rubric, ensure_ascii=False, indent=2)

    return f"""
Score this scholarship candidate using the rubric below
    
Candidate: {candidate_text}
    
Rubric: {rubric_text}

Rules:
    
- Follow the rubric and counting rules exactly.
- Give a score from 0 to 5 for academic.
- Give a score from 0 to 5 for research.
- Give a score from 0 to 5 for experience.
- Don't compute the weighted total.
- Don't rank candidates.
- Don't choose a winner.
- Return JSON only.

Return this structure:

{{
  "scores": [
    {{
      "criterion": "academic",
      "score": 0
    }},
    {{
      "criterion": "research",
      "score": 0
    }},
    {{
      "criterion": "experience",
      "score": 0
    }}
  ]
}}
""".strip()


def validate_scores(
    data: dict,
    rubric: dict
) -> bool:

    if not isinstance(data, dict):
        return False

    if set(data.keys()) != {"scores"}:
        return False

    scores = data["scores"]

    if not isinstance(scores, list):
        return False

    if len(scores) != 3:
        return False

    expected_ids = {
        item["id"]
        for item in rubric["criteria"]
    }

    actual_ids = []

    for item in scores:

        if not isinstance(item, dict):
            return False

        if set(item.keys()) != {
            "criterion",
            "score"
        }:
            return False

        criterion = item["criterion"]
        score = item["score"]

        if not isinstance(criterion, str):
            return False

        if not isinstance(
            score,
            (int, float)
        ):
            return False

        if not 0 <= score <= 5:
            return False

        actual_ids.append(criterion)

    if len(actual_ids) != len(set(actual_ids)):
        return False

    if set(actual_ids) != expected_ids:
        return False

    return True


def score_candidate(
    candidate: dict,
    rubric: dict
) -> dict:

    prompt = build_scoring_prompt(
        candidate,
        rubric
    )

    raw = ask_llm(prompt)

    try:
        parsed = parse_json(raw)

        valid = validate_scores(
            parsed,
            rubric
        )

    except ValueError:
        parsed = None
        valid = False

    if not valid:
        print(
            f"Invalid score reply for "
            f"{candidate['candidate_id']}:"
        )
        print(raw)

    return {
        "candidate_id": candidate["candidate_id"],
        "scores": parsed,
        "valid": valid,
        "raw": raw,
    }


def get_criteria(rubric:dict) -> list[dict]:
    criteria = rubric["criteria"]

    if isinstance(criteria, list):
        result = []

        for item in criteria:
            criterion_id = (
                    item.get("id")
                    or item.get("name")
                    or item.get("criterion")
            )

            result.append({
                "id": criterion_id,
                "weight": item["weight"],
            })

        return result

    if isinstance(criteria, dict):
        result = []

        for criterion_id, item in criteria.items():
            result.append({
                "id": criterion_id,
                "weight": item["weight"],
            })

        return result

    raise ValueError(
        "Unknown rubric criteria structure"
    )


def compute_total(
    score_data: dict,
    rubric: dict
) -> float:

    score_map = {
        item["criterion"]: item["score"]
        for item in score_data["scores"]
    }

    total = 0.0

    for criterion in rubric["criteria"]:
        criterion_id = criterion["id"]
        weight = criterion["weight"]

        if criterion_id not in score_map:
            raise ValueError(
                f"Missing score for {criterion_id}"
            )

        total += (
            score_map[criterion_id]
            * weight
        )

    return round(total, 2)


def score_all(
    extraction_results,
    rubric
):
    scored = []

    print("\n----- SCORING -----")

    for result in extraction_results:

        if not result["parsed_ok"]:
            print(
                result["candidate_id"],
                "skipped: extraction did not parse"
            )
            continue

        if not result["valid"]:
            print(
                result["candidate_id"],
                "skipped: extraction invalid"
            )
            continue

        candidate = result["data"]

        score_result = score_candidate(
            candidate,
            rubric
        )

        if not score_result["valid"]:
            print(
                result["candidate_id"],
                "skipped: score invalid"
            )
            continue

        try:
            total = compute_total(
                score_result["scores"],
                rubric
            )

        except ValueError as error:
            print(
                result["candidate_id"],
                "total error:",
                error
            )
            continue

        scored.append({
            "candidate_id":
                result["candidate_id"],

            "candidate":
                candidate,

            "scores":
                score_result["scores"],

            "total":
                total,
        })

        print(
            f"{result['candidate_id']}: "
            f"{score_result['scores']['scores']} "
            f"total={total:.2f}"
        )

    return scored


def choose_winner(scored_candidates):
    if not scored_candidates:
        raise RuntimeError(
            "No scored candidates"
        )

    return max(
        scored_candidates,
        key=lambda x: x["total"]
    )


def build_prose_ranking_prompt(
    scored_candidates,
    rubric
) -> str:

    candidates = [
        item["candidate"]
        for item in scored_candidates
    ]

    candidates_text = json.dumps(
        candidates,
        ensure_ascii=False,
        indent=2
    )

    rubric_text = json.dumps(
        rubric,
        ensure_ascii=False,
        indent=2
    )

    return f"""
You are selecting one candidate for a scholarship.

Candidate records:

{candidates_text}

Scholarship rubric:

{rubric_text}

Which ONE candidate should win?

Answer in normal prose.
Name the candidate ID and briefly explain why.

Don't return JSON.
""".strip()


def ask_for_prose_winner(
    scored_candidates,
    rubric
) -> str:

    prompt = build_prose_ranking_prompt(
        scored_candidates,
        rubric
    )

    return ask_llm(prompt)


def save_extractions(extraction_results):
    output_dir = ROOT / "outputs"
    output_dir.mkdir(exist_ok=True)

    data_to_save = {}

    for result in extraction_results:
        data_to_save[result["candidate_id"]] = result["data"]

    output_file = output_dir / "extractions.json"

    output_file.write_text(
        json.dumps(
            data_to_save,
            ensure_ascii=False,
            indent=2
        ),
        encoding="utf-8"
    )

    print(f"\nExtractions saved to: {output_file}")


def main():
    rubric = load_json(RUBRIC_FILE)

    extraction_results = extract_all()

    print_extraction(
        extraction_results
    )

    save_extractions(extraction_results)

    scored_candidates = score_all(
        extraction_results,
        rubric
    )

    if not scored_candidates:
        print(
            "\nERROR: No candidates were scored."
        )
        print(
            "Check extraction/scoring output above."
        )
        return

    print(
        "\n----- COMPUTED RANKING -----"
    )

    ranking = sorted(
        scored_candidates,
        key=lambda x: x["total"],
        reverse=True
    )

    for position, candidate in enumerate(
        ranking,
        start=1
    ):

        print(
            f"{position}. "
            f"{candidate['candidate_id']} "
            f"total={candidate['total']:.2f}"
        )

    winner = choose_winner(
        scored_candidates
    )

    print(
        "\n----- COMPUTED WINNER -----"
    )

    print(
        winner["candidate_id"],
        f"total={winner['total']:.2f}"
    )

    print(
        "\n----- LLM PROSE WINNER -----"
    )

    prose_winner = ask_for_prose_winner(
        scored_candidates,
        rubric
    )

    print(prose_winner)


if __name__ == "__main__":
    main()

